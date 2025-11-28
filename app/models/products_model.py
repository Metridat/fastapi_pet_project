from decimal import Decimal
from sqlalchemy import (
    ForeignKey, 
    String, 
    Float, 
    Boolean, 
    Integer, 
    Numeric,
    Computed,
    Index
)
from sqlalchemy.dialects.postgresql import TSVECTOR
from sqlalchemy.orm import Mapped, mapped_column as mc, relationship
from app.database import Base


class Product(Base):
    __tablename__ = 'products'

    id: Mapped[int] = mc(primary_key=True, index=True)
    name: Mapped[str] = mc(String(50), unique=True, index=True, nullable=False)
    description: Mapped[str | None] = mc(String(500), nullable=True)
    price: Mapped[Decimal] = mc(Numeric(10, 2), nullable=False)
    image_url: Mapped[str | None] = mc(String(200), nullable=True)
    stock: Mapped[int] = mc(Integer, nullable=False)
    category_id: Mapped[int] = mc(Integer, ForeignKey('categories.id', ondelete='SET NULL'), nullable=False)
    seller_id: Mapped[int] = mc(Integer, ForeignKey('users.id', ondelete='CASCADE'), nullable=False)
    rating: Mapped[float] = mc(Float, default=0.0)
    is_active: Mapped[bool] = mc(Boolean, default=True)


    tsv: Mapped[str] = mc(
        TSVECTOR,
        Computed(
            """
            setweight(to_tsvector('english', coalesce(name, '')), 'A')
            ||
            setweight(to_tsvector('russian', coalesce(name, '')), 'A')
            ||
            setweight(to_tsvector('english', coalesce(description, '')), 'B')
            ||
            setweight(to_tsvector('russian', coalesce(description, '')), 'B')
            """,
            persisted=True
        ),
        nullable=False
    )


    category = relationship(
        'Category',
        back_populates='products')
    
    seller = relationship(
        'User',
        back_populates='products') 

    reviews = relationship(
        'Review',
        back_populates='product'
    )

    cart_items = relationship(
        'CartItem',
        back_populates='product'
    )

    order_items = relationship(
        'OrderItem',
        back_populates='product'
    )

    __table_args__ = (
        Index("ix_products_tsv_gin", "tsv", postgresql_using="gin"),
    )