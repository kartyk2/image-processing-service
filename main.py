from fastapi import FastAPI, File, HTTPException, UploadFile
from app.router import router
from app.database import Base, engine
from app.model import *
app= FastAPI(title= "image processing app")
app.include_router(router, prefix= "/v1")

Base.metadata.create_all(engine)


from pathlib import Path
import shutil

UPLOAD_DIRECTORY = Path("/files")
UPLOAD_DIRECTORY.mkdir(parents=True, exist_ok=True)

@app.post("/webhook")
async def receive_file(file: UploadFile = File(...)):
    try:
        # Print the file details
        print(f"Received file: {file.filename}")
        
        file_location = UPLOAD_DIRECTORY / file.filename
        
        # Print the file location where it will be saved
        print(f"Saving file to: {file_location}")
        
        # Save the uploaded file to the specified directory
        with file_location.open("wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
        
        # Print success message
        print(f"File successfully saved as: {file.filename}")
        
        return {"filename": file.filename, "status": "success"}
    
    except Exception as e:
        # Print the error details
        print(f"Error saving file: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error saving file: {str(e)}")