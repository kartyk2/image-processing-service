from sqlalchemy import (
    create_engine,
    Column,
    String,
    Integer,
    Enum,
    ForeignKey,
    Text,
    DateTime,
)
from sqlalchemy.orm import relationship
import uuid
import enum
from datetime import datetime
from app.database import Base


class RequestStatus(enum.Enum):
    pending = "pending"
    processing = "processing"
    completed = "completed"
    failed = "failed"


class ImageStatus(enum.Enum):
    pending = "pending"
    processing = "processing"
    completed = "completed"
    failed = "failed"


class Request(Base):
    __tablename__ = "requests"

    request_id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    status = Column(Enum(RequestStatus), default=RequestStatus.pending)
    created_at = Column(DateTime, default=datetime.now())
    updated_at = Column(DateTime, default=datetime.now(), onupdate=datetime.now())
    input_csv_url = Column(Text, nullable=True)
    output_csv_url = Column(Text, nullable=True)

    products = relationship("Product", back_populates="request")


class Product(Base):
    __tablename__ = "products"

    product_id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    request_id = Column(String, ForeignKey("requests.request_id"))
    serial_number = Column(Integer)
    product_name = Column(String)

    request = relationship("Request", back_populates="products")
    image_urls = relationship("ImageUrl", back_populates="product")


class ImageUrl(Base):
    __tablename__ = "image_urls"

    image_id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    product_id = Column(String, ForeignKey("products.product_id"))
    input_image_url = Column(Text)
    output_image_url = Column(Text, nullable=True)
    status = Column(Enum(ImageStatus), default=ImageStatus.pending)

    product = relationship("Product", back_populates="image_urls")
