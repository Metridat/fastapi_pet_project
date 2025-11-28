from pydantic import BaseModel, Field, ConfigDict
from app.schemas.products import ProductSchema
from decimal import Decimal


class CartItemBase(BaseModel):
    """
    Base model for CartItem
    """
    product_id: int = Field(description='Product ID')
    quantity: int = Field(ge=1, description='Quanity products')




class CartItemCreate(CartItemBase):
    """
    Model for POST request by CartItem
    """
    


class CartItemUpdate(BaseModel):
    """
    Model for PUT request by CartItem
    """
    quantity: int = Field(ge=1, description='New quanity products')


class CartItemSchema(BaseModel):
    """
    Item in cart with product details.
    Model for GET request by CartItem
    """
    id: int = Field(description='Cart item ID')
    quantity: int = Field(ge=1, description='Quanity products')
    product: ProductSchema = Field(description='Info product')

    model_config = ConfigDict(from_attributes=True)    



class Cart(BaseModel):
    """
    Full info about cart
    Model for GET request by Cart
    """
    buyer_id: int = Field(description='Buyer ID')
    items: list[CartItemSchema] = Field(default_factory=list, description='Cart contents')
    total_quantity: int = Field(ge=0, description='Total quanity')
    total_price: Decimal = Field(ge=0, description='Total price')

    model_config = ConfigDict(from_attributes=True)

    

