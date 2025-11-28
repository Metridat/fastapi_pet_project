from sqlalchemy.orm import Mapped, mapped_column as mc, relationship
from app.database import Base
from datetime import datetime
from decimal import Decimal
from sqlalchemy import String, Numeric, ForeignKey, DateTime, func, Integer


class Order(Base):

    __tablename__ = "orders"


    id: Mapped[int] = mc(primary_key=True)
    buyer_id: Mapped[int] = mc(
        ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True
    )
    status: Mapped[str] = mc(String(20), default="pending", nullable=False)
    total_amount: Mapped[Decimal] = mc(Numeric(10, 2), default=0, nullable=False)
    created_at: Mapped[datetime] = mc(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
    updated_at: Mapped[DateTime] = mc(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False,
    )

    buyer = relationship("User", back_populates="orders")
    items = relationship("OrderItem", back_populates="order")


class OrderItem(Base):

    __tablename__ = "order_items"

    id: Mapped[int] = mc(primary_key=True)
    order_id: Mapped[int] = mc(
        ForeignKey("orders.id", ondelete="CASCADE"), nullable=False, index=True
    )
    product_id: Mapped[int] = mc(
        ForeignKey("products.id", ondelete="SET NULL"), nullable=False, index=True
    )
    quantity: Mapped[int] = mc(Integer, nullable=False)
    unit_price: Mapped[Decimal] = mc(Numeric(10, 2), nullable=False)
    total_price: Mapped[Decimal] = mc(Numeric(10, 2), nullable=False)

    order = relationship("Order", back_populates="items")
    product = relationship('Product', back_populates='order_items')
    