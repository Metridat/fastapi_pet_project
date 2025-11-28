from decimal import Decimal
from pydantic import BaseModel, Field, ConfigDict

class ProductSchema(BaseModel):
    """
    Model for GET request by Product
    """

    id: int
    name: str
    description: str | None
    price: float
    image_url: str | None
    stock: int | None
    category_id: int | None
    seller_id: int | None
    rating: float = Field(description="Product rating")
    is_active: bool
    model_config = ConfigDict(from_attributes=True)

class ProductCreateSchema(BaseModel):
    """
    Model for POST|request by Product
    """    

    name: str = Field(max_length=50, min_length=2, description='Name product')
    description: str | None = Field(default=None, max_length=500, description="Description's product")
    price: Decimal = Field(ge=0.01, le=100000.00, description="Price product")
    image_url: str | None = Field(default=None, description="Product image")
    stock: int = Field(gt=0, description="Products in stock")
    category_id: int = Field(ge=1, description="Product category")

    


class ProductUpgradeSchema(BaseModel):
    """
    Model for PUT|PATCH request by Product
    """    

    name: str = Field(max_length=50, min_length=2, description='Name product')
    description: str | None = Field(default=None, max_length=500, description="Description's product")
    price: float = Field(ge=0.01, le=100000.00, description="Price product")
    image_url: str | None = Field(default=None, description="Product image")
    stock: int = Field(gt=0, description="Products in stock")


class ProductList(BaseModel):
    items: list[ProductSchema] = Field(description='Products for the current page')
    total: int = Field(ge=0, description='Total number of goods')
    page: int = Field(ge=1, description='Current page number')
    page_size: int = Field(ge=1, description='Number of elements per page')

    model_config = ConfigDict(from_attributes=True)