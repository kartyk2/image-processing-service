from fastapi import FastAPI

app= FastAPI(title= "image processing app")
app.include_router(prefix= "/v1")