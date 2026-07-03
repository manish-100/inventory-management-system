from datetime import datetime
from decimal import Decimal
from typing import List, Optional
from pydantic import BaseModel, EmailStr, Field

class ProductBase(BaseModel):
    name: str = Field(min_length=2, max_length=120)
    sku: str = Field(min_length=2, max_length=80)
    description: Optional[str] = None
    price: Decimal = Field(gt=0)
    stock: int = Field(ge=0)
class ProductCreate(ProductBase): pass
class ProductUpdate(ProductBase): pass
class ProductOut(ProductBase):
    id: int
    created_at: datetime
    model_config = {'from_attributes': True}

class CustomerBase(BaseModel):
    name: str = Field(min_length=2, max_length=120)
    email: EmailStr
    phone: Optional[str] = None
    address: Optional[str] = None
class CustomerCreate(CustomerBase): pass
class CustomerUpdate(CustomerBase): pass
class CustomerOut(CustomerBase):
    id: int
    created_at: datetime
    model_config = {'from_attributes': True}

class OrderItemCreate(BaseModel):
    product_id: int
    quantity: int = Field(gt=0)
class OrderCreate(BaseModel):
    customer_id: int
    items: List[OrderItemCreate] = Field(min_length=1)
class OrderItemOut(BaseModel):
    id: int
    product_id: int
    quantity: int
    unit_price: Decimal
    product: ProductOut
    model_config = {'from_attributes': True}
class OrderOut(BaseModel):
    id: int
    customer_id: int
    total_amount: Decimal
    status: str
    created_at: datetime
    customer: CustomerOut
    items: List[OrderItemOut]
    model_config = {'from_attributes': True}


class OrderStatusUpdate(BaseModel):
    status: str

class DashboardSummary(BaseModel):
    totalProducts: int
    totalCustomers: int
    totalOrders: int
    lowStockProducts: int
