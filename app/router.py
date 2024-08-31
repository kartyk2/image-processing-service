from datetime import datetime
import io
import traceback
import uuid, ast
from fastapi import APIRouter, Depends, UploadFile, HTTPException, status
from fastapi.responses import JSONResponse
from celery.result import AsyncResult
from celery import chord
import pandas as pd
from typing import List
from sqlalchemy.orm import Session

from app.config import Logger
from app.database import get_db
from app.model import Request
from app.schema import Product
from celery_worker.task import add, finalize_request, process_product, simulate_long_task

router = APIRouter()
logger = Logger.get_logger()

@router.get("/health_check")
async def health_check():
    # Add tasks to the queue
    task_ids = []
    for i in range(5, 10):
        result = simulate_long_task.apply_async(args=[i])
        task_ids.append(result.id)
    
    # Check the status of the tasks
    task_statuses = {}
    for task_id in task_ids:
        result = AsyncResult(task_id)
        task_statuses[task_id] = result.status
    
    return {
        "status": "Tasks have been added to the queue.",
        "timestamp": datetime.now(),
        "task_statuses": task_statuses
    }

@router.post("/upload")
async def upload_csv_file(file: UploadFile, db: Session = Depends(get_db)):
    try:
        if not file.filename.endswith('.csv'):
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Only CSV files are allowed.")
        
        content = await file.read()
        try:
            data = io.StringIO(content.decode('utf-8'))
            df = pd.read_csv(data, sep=",")
            
            print(df.head())
        except Exception as e:
            return JSONResponse(content={"message": f"Error reading CSV file: {e}"}, status_code=status.HTTP_400_BAD_REQUEST)

        required_columns = {'SerialNumber', 'ProductName', 'InputImageUrls'}
        
        if not required_columns.issubset(df.columns):
            missing = required_columns - set(df.columns)
            return JSONResponse(content={"message": f"CSV file is missing required columns: {', '.join(missing)}"}, status_code=status.HTTP_400_BAD_REQUEST)
            
        unique_request_id = uuid.uuid4().hex

        new_request = Request(request_id=unique_request_id)
        db.add(new_request)
        db.commit()  
        
        tasks= []
        for index, product_row in df.iterrows():
            try:
                # Print the entire row
                print(product_row)

                # Access the data directly from the product_row Series
                serial_number = str(product_row['SerialNumber'])
                product_name = product_row['ProductName']
                input_image_urls = input_image_urls = product_row['InputImageUrls'].split(',')

                # Print to verify values
                print(f"Product Name: {product_name}")

                # Create a product object
                product = Product(
                    request_id=unique_request_id,
                    product_id=serial_number,
                    name=product_name,
                    images=input_image_urls
                )
                
                print(product)
                tasks.append(process_product.s(product.model_dump()))
            
            except (ValueError, SyntaxError) as e:
                raise HTTPException(status_code=400, detail=f"Error processing row {index + 1}: {str(e)}")
            
        # Process each product asynchronously
        # Use chord to trigger a callback after all tasks are completed
        print(len(tasks))
        task_callback = chord(tasks)(finalize_request.s(unique_request_id))
        print(task_callback)

        # Return the unique request ID as JSON
        return JSONResponse(content={"request_id": unique_request_id}, status_code=status.HTTP_200_OK)

    except HTTPException as http_exc:
        logger.warning(f"HTTP exception for file {file.filename}: {http_exc.detail}")
        raise http_exc

    except Exception as exception:
        logger.error(f"An error occurred while uploading file {file.filename}: {traceback.format_exc()}")
        return JSONResponse(content={"message": "An error occurred while processing the file."}, status_code=status.HTTP_500_INTERNAL_SERVER_ERROR)
