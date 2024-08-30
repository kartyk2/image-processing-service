from datetime import datetime
import io
from fastapi import APIRouter, UploadFile, HTTPException, status
from fastapi.responses import JSONResponse
from celery.result import AsyncResult
import pandas as pd
from typing import List
import logging

from app.config import Logger
from celery_worker.task import add, simulate_long_task

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
async def upload_csv_file(file: UploadFile):
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

        required_columns = {'Serial Number', 'Product Name', 'Input Image Urls'}
        
        if not required_columns.issubset(df.columns):
            missing = required_columns - set(df.columns)
            return JSONResponse(content={"message": f"CSV file is missing required columns: {', '.join(missing)}"}, status_code=status.HTTP_400_BAD_REQUEST)

        logger.info(f"Successfully uploaded file: {file.filename}")
        return JSONResponse(content={"message": "File uploaded successfully."}, status_code=status.HTTP_200_OK)

    except HTTPException as http_exc:
        logger.warning(f"HTTP exception for file {file.filename}: {http_exc.detail}")
        raise http_exc

    except Exception as exception:
        logger.error(f"An error occurred while uploading file {file.filename}: {str(exception)}")
        return JSONResponse(content={"message": "An error occurred while processing the file."}, status_code=status.HTTP_500_INTERNAL_SERVER_ERROR)
