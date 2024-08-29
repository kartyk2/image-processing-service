from datetime import datetime
from fastapi import APIRouter, UploadFile, HTTPException, status, Form
from fastapi.responses import JSONResponse
from typing import List
import logging

from app.config import Logger

router = APIRouter()

logger= Logger.get_logger()
router= APIRouter()

@router.get("/health_check")
async def health_check():
    return datetime.now()



@router.post("/upload")
async def upload_csv_file(file: UploadFile = Form()):
    try:
        # Check if the uploaded file is a CSV
        if not file.filename.endswith('.csv'):
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Only CSV files are allowed.")
        
        # Read the file content
        content = await file.read()
        
        # Here you can add code to process the CSV file content
        # For example, parse CSV data using pandas or any other library

        logger.info(f"Successfully uploaded file: {file.filename}")
        return JSONResponse(content={"message": "File uploaded successfully."}, status_code=status.HTTP_200_OK)

    except HTTPException as http_exc:
        logger.warning(f"HTTP exception for file {file.filename}: {http_exc.detail}")
        raise http_exc  # Re-raise to propagate the correct HTTP response

    except Exception as exception:
        logger.error(f"An error occurred while uploading file {file.filename}: {str(exception)}")
        return JSONResponse(content={"message": "An error occurred while processing the file."}, status_code=status.HTTP_500_INTERNAL_SERVER_ERROR)
