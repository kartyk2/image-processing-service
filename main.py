from fastapi import FastAPI
from app.router import router
from app.database import Base, engine
from app.model import *
app= FastAPI(title= "image processing app")
app.include_router(router, prefix= "/v1")

Base.metadata.create_all(engine)