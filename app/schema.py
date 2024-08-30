from typing import List
from pydantic import BaseModel, AnyHttpUrl


class Product(BaseModel):
    request_id: str
    product_id: str
    name: str
    images: List[str]