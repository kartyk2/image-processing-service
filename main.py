from fastapi import FastAPI
from app.router import router

app= FastAPI(title= "image processing app")
app.include_router(router, prefix= "/v1")