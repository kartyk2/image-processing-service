from typing import List
from pydantic import BaseModel, AnyHttpUrl


class ProductAdd(BaseModel):
    """ schema for Product object """
    request_id: str
    product_id: str
    name: str
    images: List[str]