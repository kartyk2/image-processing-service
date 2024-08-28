from fastapi import APIRouter
from datetime import datetime

router= APIRouter()


@router.get("/health_check")
async def health_check():
    return datetime.now()