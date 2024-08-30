import time
from celery_worker.worker import celery_app
from app.config import Logger

logger= Logger.get_logger()

@celery_app.task(name='add_numbers', queue= "fast")
def add(x, y):
    """A simple task to add two numbers."""
    return x + y

@celery_app.task(name='simulate_long_task_for_a_while', queue= "slow")
def simulate_long_task(seconds):
    """A task that simulates a long-running process."""
    time.sleep(seconds)
    return f"Task completed after {seconds} seconds."

@celery_app.task(name='process_product', queue='image_process')
def process_product(product_details):
    """Process a row of a CSV implying processing a product"""
    try:
        product_id = product_details.get('Product ID')
        product_name = product_details.get('ProductName')
        image_url = product_details.get('InputImageUrls')

        logger.info(f"Processing product: {product_id} - {product_name}")

        if image_url:
            logger.info(f"Processing image from URL: {image_url}")
            process_image(image_url)
        else:
            logger.warning(f"No image URL provided for product: {product_id}")

        save_product_to_database(product_id, product_name)

        return {
            'status': 'success',
            'message': f'Product {product_id} processed successfully.'
        }

    except Exception as e:
        logger.error(f"Error processing product: {product_details} - {e}")
        return {
            'status': 'failure',
            'message': str(e)
        }

def process_image(image_url):
    """Simulate image processing"""
    import time
    time.sleep(2)

def save_product_to_database(product_id, product_name):
    """Simulate saving product to a database"""
    logger.info(f"Saving product {product_id} to database with name {product_name}")
