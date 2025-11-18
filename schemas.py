"""
Database Schemas

Define your MongoDB collection schemas here using Pydantic models.
These schemas are used for data validation in your application.

Each Pydantic model represents a collection in your database.
Model name is converted to lowercase for the collection name:
- User -> "user" collection
- Product -> "product" collection
- BlogPost -> "blogs" collection
"""

from pydantic import BaseModel, Field
from typing import Optional, Literal
from datetime import datetime

# Example schemas (replace with your own):

class User(BaseModel):
    """
    Users collection schema
    Collection name: "user" (lowercase of class name)
    """
    name: str = Field(..., description="Full name")
    email: str = Field(..., description="Email address")
    address: str = Field(..., description="Address")
    age: Optional[int] = Field(None, ge=0, le=120, description="Age in years")
    is_active: bool = Field(True, description="Whether user is active")

class Product(BaseModel):
    """
    Products collection schema
    Collection name: "product" (lowercase of class name)
    """
    title: str = Field(..., description="Product title")
    description: Optional[str] = Field(None, description="Product description")
    price: float = Field(..., ge=0, description="Price in dollars")
    category: str = Field(..., description="Product category")
    in_stock: bool = Field(True, description="Whether product is in stock")

# Add your own schemas here:
# --------------------------------------------------

class Event(BaseModel):
    """
    Christian events collection schema
    Collection name: "event"
    """
    title: str = Field(..., description="Event title")
    description: Optional[str] = Field(None, description="Event description")
    type: Literal['worship','conference','retreat','concert','service','youth','prayer','other'] = Field('other', description="Type of event")
    start_date: datetime = Field(..., description="Event start date/time (UTC)")
    end_date: Optional[datetime] = Field(None, description="Event end date/time (UTC)")
    location_name: Optional[str] = Field(None, description="Venue or location name")
    latitude: float = Field(..., ge=-90, le=90, description="Latitude")
    longitude: float = Field(..., ge=-180, le=180, description="Longitude")
    city: Optional[str] = Field(None, description="City")
    country: Optional[str] = Field(None, description="Country")
    url: Optional[str] = Field(None, description="Event URL or registration link")
