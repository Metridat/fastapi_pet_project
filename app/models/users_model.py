from enum import Enum as PyEnum
from sqlalchemy import Enum


from sqlalchemy import String, Boolean
from sqlalchemy.orm import Mapped, mapped_column as mc, relationship
from app.database import Base

class UserRole(PyEnum):
    buyer = 'buyer'
    seller = 'seller'
    admin = 'admin'
    
class User(Base):
    __tablename__ = 'users'

    id: Mapped[int] = mc(primary_key=True, index=True)
    email: Mapped[str] = mc(String(100), unique=True, index=True, nullable=False)
    hashed_password: Mapped[str] = mc(String(500), nullable=False)
    is_active: Mapped[bool] = mc(Boolean, default=True)
    role: Mapped[UserRole] = mc(Enum(UserRole), default=UserRole.buyer)

    products = relationship(
        'Product',
        back_populates='seller')
    
    reviews = relationship(
        'Review',
        back_populates='buyer'
    )

    cart_items = relationship(
        'CartItem',
        back_populates='buyer'
    )

    orders = relationship(
        'Order',
        back_populates='buyer'
    )