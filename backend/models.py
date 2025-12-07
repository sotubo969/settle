from pydantic import BaseModel, Field, EmailStr
from typing import List, Optional
from datetime import datetime
from bson import ObjectId

# Custom ObjectId type for Pydantic
class PyObjectId(ObjectId):
    @classmethod
    def __get_validators__(cls):
        yield cls.validate

    @classmethod
    def validate(cls, v):
        if not ObjectId.is_valid(v):
            raise ValueError("Invalid ObjectId")
        return ObjectId(v)

    @classmethod
    def __get_pydantic_json_schema__(cls, schema):
        schema.update(type="string")
        return schema

# Address Model
class Address(BaseModel):
    fullName: str
    address: str
    city: str
    postcode: str
    phone: str
    isDefault: bool = False

# User Model
class User(BaseModel):
    id: Optional[PyObjectId] = Field(default_factory=PyObjectId, alias="_id")
    name: str
    email: EmailStr
    password: Optional[str] = None
    role: str = "customer"
    avatar: Optional[str] = None
    phone: Optional[str] = None
    addresses: List[Address] = []
    googleId: Optional[str] = None
    createdAt: datetime = Field(default_factory=datetime.utcnow)
    updatedAt: datetime = Field(default_factory=datetime.utcnow)

    class Config:
        populate_by_name = True
        arbitrary_types_allowed = True
        json_encoders = {ObjectId: str}

# Vendor Model
class Vendor(BaseModel):
    id: Optional[PyObjectId] = Field(default_factory=PyObjectId, alias="_id")
    userId: Optional[PyObjectId] = None
    businessName: str
    description: str
    email: EmailStr
    phone: str
    address: str
    city: str
    postcode: str
    location: str
    verified: bool = False
    rating: float = 0.0
    totalSales: int = 0
    commission: float = 1.0
    status: str = "pending"
    createdAt: datetime = Field(default_factory=datetime.utcnow)
    updatedAt: datetime = Field(default_factory=datetime.utcnow)

    class Config:
        populate_by_name = True
        arbitrary_types_allowed = True
        json_encoders = {ObjectId: str}

# Product Model
class VendorInfo(BaseModel):
    name: str
    rating: float
    location: str
    totalSales: int = 0

class Product(BaseModel):
    id: Optional[PyObjectId] = Field(default_factory=PyObjectId, alias="_id")
    name: str
    brand: str
    description: str
    price: float
    originalPrice: Optional[float] = None
    image: str
    images: List[str] = []
    category: str
    categoryId: int
    vendorId: PyObjectId
    vendor: VendorInfo
    rating: float = 0.0
    reviews: int = 0
    stock: int
    weight: str
    inStock: bool = True
    featured: bool = False
    createdAt: datetime = Field(default_factory=datetime.utcnow)
    updatedAt: datetime = Field(default_factory=datetime.utcnow)

    class Config:
        populate_by_name = True
        arbitrary_types_allowed = True
        json_encoders = {ObjectId: str}

# Request/Response Models
class UserRegister(BaseModel):
    name: str
    email: EmailStr
    password: str

class UserLogin(BaseModel):
    email: EmailStr
    password: str