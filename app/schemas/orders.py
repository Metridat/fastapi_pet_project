from pydantic import BaseModel, Field, ConfigDict
from decimal import Decimal
from app.schemas.products import ProductSchema
from datetime import datetime


class OrderItem(BaseModel):
    id: int = Field(description='Product item ID')
    product_id: int = Field(description='Product ID')
    quantity: int = Field(ge=1, description='Quantity')
    unit_price: Decimal = Field(ge=0, description='Unit price at time of purchase')
    total_price: Decimal = Field(ge=0, description='Amount per item')
    product: ProductSchema | None = Field(None, description='Full product information')

    model_config = ConfigDict(from_attributes=True)



class Order(BaseModel):
    id: int = Field(description='Order ID')
    buyer_id: int = Field(description='Buyer ID')
    status: str = Field(description='Current order status')
    total_amount: Decimal = Field(ge=0, description='Total cost')
    created_at: datetime = Field(description='When the order was created')
    updated_at: datetime = Field(description='When was it last updated')
    items: list[OrderItem] = Field(default_factory=list, description='List of positions')

    model_config = ConfigDict(from_attributes=True)



class OrderList(BaseModel):
    items: list[Order] = Field(description='Orders on the current page')    
    total: int = Field(ge=0, description='Total number of orders')
    page: int = Field(ge=1, description='Current page')
    page_size: int = Field(ge=1, description='Page size')

    model_config = ConfigDict(from_attributes=True)
    


