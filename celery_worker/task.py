import time
import uuid
import io
import requests
from io import BytesIO
from PIL import Image
import pandas as pd
from sqlalchemy import update, func, text
from app.database import ConnectionManager
from app.model import ImageStatus, ImageUrl, Product, Request
from celery_worker.worker import celery_app
from app.config import settings, Logger


logger = Logger.get_logger()

@celery_app.task(name='add_numbers', queue="fast")
def add(x, y):
    """A simple task to add two numbers."""
    return x + y

@celery_app.task(name='simulate_long_task_for_a_while', queue="slow")
def simulate_long_task(seconds):
    """A task that simulates a long-running process."""
    time.sleep(seconds)
    return f"Task completed after {seconds} seconds."



@celery_app.task(name='finalize_request', queue='image_process')
def finalize_request(results, request_id):
    """
    This task finalizes the request by checking that all tasks are complete,
    querying the database for results, converting the results to a CSV file,
    and sending it to the webhook URL as a file.
    """
    
    print("ALL TASKS COMPLETED")
    try:
        # Initialize database connection
        with ConnectionManager(settings.database_url.unicode_string()) as db:
            # Query to concatenate input and output URLs for each product using string_agg
            query_result = (
                db.query(
                    Request.request_id,
                    Product.product_id,
                    Product.serial_number,
                    Product.product_name,
                    func.string_agg(ImageUrl.input_image_url, ', ').label('input_image_urls'),
                    func.string_agg(ImageUrl.output_image_url, ', ').label('output_image_urls')
                )
                .join(Product, Request.request_id == Product.request_id)
                .join(ImageUrl, Product.product_id == ImageUrl.product_id)
                .filter(Request.request_id == request_id)
                .group_by(Request.request_id, Product.product_id, Product.serial_number, Product.product_name)
                .all()
            )

        # Check if query_result is empty
        if not query_result:
            logger.warning(f"No data found for request_id: {request_id}")
            return

        # Convert query results to a pandas DataFrame
        data = []
        for row in query_result:
            data.append({
                'Product ID': row.product_id,
                'Serial Number': row.serial_number,
                'Product Name': row.product_name,
                'Input Image URLs': row.input_image_urls,
                'Output Image URLs': row.output_image_urls,
            })
        df = pd.DataFrame(data)

        # Convert DataFrame to CSV
        csv_buffer = io.StringIO()
        df.to_csv(csv_buffer, index=False)

        # Prepare to send the CSV to the webhook URL
        csv_buffer.seek(0)  # Move to the start of the stream
        webhook_url = "http://127.0.0.1:8003/webhook"  # Replace with your actual webhook URL
        files = {'file': ('results.csv', csv_buffer, 'text/csv')}

        # Send POST request with the CSV file to the webhook URL
        response = requests.post(webhook_url, files=files, data={'request_id': request_id})
        response.raise_for_status()  # Raise an error for any unsuccessful status code

        logger.info(f"Webhook sent successfully for request_id: {request_id}. Response: {response.status_code}")

    except Exception as e:
        logger.error(f"Error in finalize_request for request_id {request_id}: {e}")
        raise e


@celery_app.task(name='process_product', queue='image_process')
def process_product(product_details):
    """Process a row of a CSV implying processing a product and its images."""
    try:
        request_id = product_details.get('request_id')
        serial_number = product_details.get('product_id')
        product_name = product_details.get('name')
        image_urls = product_details.get('images')

        unique_product_id = uuid.uuid4().hex
        new_product = Product(
            product_id= unique_product_id,
            request_id=request_id,
            serial_number=serial_number,
            product_name=product_name
        )
        save_product_to_database(new_product)
        product_id= unique_product_id

        logger.info(f"Processing product: {serial_number} - {product_name}")

        if image_urls:
            for image_url in image_urls:
                logger.info(f"Processing image from URL: {image_url}")

                # Properly handle session and add ImageUrl instance to the session
                with ConnectionManager(settings.database_url.unicode_string()) as db:
                    # Create ImageUrl instance and save to DB within the session context
                    image_instance = ImageUrl(
                        product_id=product_id,
                        input_image_url=image_url,
                        status=ImageStatus.pending
                    )
                    db.add(image_instance)  # Add to session
                    db.commit()  # Commit to save and bind the instance

                    # Now the image_instance is bound to the session, you can access its ID
                    image_id = image_instance.image_id

                    # Process the image within the same task
                    try:
                        # Update status to 'processing'
                        db.execute(
                            text("UPDATE image_urls SET status = :status WHERE image_id = :image_id"),
                            {"status": ImageStatus.processing.value, "image_id": image_id}
                        )
                        db.commit()

                        # Retrieve the ImageUrl object by image_id
                        image = db.query(ImageUrl).filter_by(image_id=image_id).one_or_none()
                        if not image:
                            logger.error(f"Image with ID {image_id} not found in database.")
                            continue

                        # Download the image
                        response = requests.get(image.input_image_url)
                        response.raise_for_status()

                        # Open the image with PIL
                        img = Image.open(BytesIO(response.content))

                        # Resize the image by 50%
                        img = img.resize((int(img.width * 0.5), int(img.height * 0.5)))

                        # Save the processed image to an output path
                        output_image_url = f"/path/to/output/directory/{image.image_id}.jpg"
                        img.save(output_image_url)

                        # Update image URL and status
                        db.execute(
                            text("UPDATE image_urls SET output_image_url = :output_image_url, status = :status WHERE image_id = :image_id"),
                            {"output_image_url": output_image_url, "status": ImageStatus.completed.value, "image_id": image_id}
                        )
                        db.commit()

                        logger.info(f"Image processed and saved at: {output_image_url}")

                    except Exception as e:
                        # Handle any errors during image processing
                        logger.error(f"Error processing image {image_id}: {e}")
                        db.execute(
                            text("UPDATE image_urls SET status = :status WHERE image_id = :image_id"),
                            {"status": ImageStatus.failed.value, "image_id": image_id}
                        )
                        db.commit()

        else:
            logger.warning(f"No image URL provided for product: {serial_number}")
        
        return {
            'status': 'success',
            'message': f'Product {product_id} and its images processed successfully.'
        }

    except Exception as e:
        logger.error(f"Error processing product: {product_details} - {e}")
        return {
            'status': 'failure',
            'message': str(e)
        }

# Simulate saving product to a database
def save_product_to_database(product):
    """Simulate saving product to a database"""
    with ConnectionManager(settings.database_url.unicode_string()) as db:
        db.add(product)
        db.commit()

# Simulate saving image to a database
def save_image_to_database(image):
    """Save image instance to database"""
    with ConnectionManager(settings.database_url.unicode_string()) as db:
        db.add(image)
        db.commit()

def trigger_webhook(request_id, webhook_url):
    if not webhook_url:
        return

    try:
        response = requests.post(webhook_url, json={"request_id": request_id, "status": "completed"})
        response.raise_for_status()
        logger.info(f"Webhook triggered successfully for request {request_id} at {webhook_url}")
    except Exception as e:
        logger.error(f"Error triggering webhook for request {request_id}: {e}")