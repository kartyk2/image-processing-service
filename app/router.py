from datetime import datetime
import io
from fastapi import APIRouter, UploadFile, HTTPException, status, Form
from fastapi.responses import JSONResponse
from typing import List
import logging, pandas as pd

from app.config import Logger

router = APIRouter()

logger= Logger.get_logger()
router= APIRouter()

@router.get("/health_check")
async def health_check():
    return datetime.now()


@router.post("/upload")
async def upload_csv_file(file: UploadFile):
    try:
        # Check if the uploaded file is a CSV
        if not file.filename.endswith('.csv'):
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Only CSV files are allowed.")
        
        # Read the file content
        content = await file.read()
        
        # Convert the content to a pandas DataFrame
        try:
            # Use StringIO to read the CSV content
            data = io.StringIO(content.decode('utf-8'))
            df = pd.read_csv(data, sep=",")
            
            print(df.head())
        except Exception as e:
            return f"Error reading CSV file: {e}"

        # Define the required columns
        required_columns = {'Serial Number', 'Product Name', 'Input Image Urls'}
        
        # Check if all required columns are present
        if not required_columns.issubset(df.columns):
            missing = required_columns - set(df.columns)
            return f"CSV file is missing required columns: {', '.join(missing)}"

        

        logger.info(f"Successfully uploaded file: {file.filename}")
        return JSONResponse(content={"message": "File uploaded successfully."}, status_code=status.HTTP_200_OK)

    except HTTPException as http_exc:
        logger.warning(f"HTTP exception for file {file.filename}: {http_exc.detail}")
        raise http_exc  # Re-raise to propagate the correct HTTP response

    except Exception as exception:
        logger.error(f"An error occurred while uploading file {file.filename}: {str(exception)}")
        return JSONResponse(content={"message": "An error occurred while processing the file."}, status_code=status.HTTP_500_INTERNAL_SERVER_ERROR)
