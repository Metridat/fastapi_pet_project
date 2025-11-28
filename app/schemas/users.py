from pydantic import BaseModel, Field, ConfigDict, EmailStr
from enum import Enum

class UserRoleEnum(str, Enum):
    buyer = 'buyer'
    seller = 'seller'

class UserRoleAdminEnum(str, Enum):
    admin = 'admin'
    buyer = 'buyer'
    seller = 'seller'


class UserSchema(BaseModel):
    """
    Model for GET request by User
    """

    id: int
    email: EmailStr
    role: UserRoleAdminEnum = Field(description='Role "buyer" or "seller"')
    is_active: bool
    model_config = ConfigDict(from_attributes=True)


class UserCreateSchema(BaseModel):
    """
    Model for POST|PUT|PATCH request by User
    """

    email: EmailStr = Field(max_length=100, description="User's email")
    password: str = Field(min_length=8, description='Password should be min 8 symbols')
    role: UserRoleEnum  = Field(default=UserRoleEnum.buyer,
                      description='Role "buyer" or "seller"')