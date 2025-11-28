from datetime import datetime

from sqlalchemy.orm import Mapped, mapped_column as mc, relationship
from sqlalchemy import ForeignKey, DateTime, Integer, UniqueConstraint, func

from app.database import Base


class CartItem(Base):
    __tablename__ = "cart_items"

    __table_args__ = (
        UniqueConstraint("buyer_id", "product_id", name="uq_cart_items_user_product"),
    )

    id: Mapped[int] = mc(Integer, primary_key=True)
    buyer_id: Mapped[int] = mc(
        Integer, 
        ForeignKey("users.id", ondelete="CASCADE"), 
        nullable=False, 
        index=True
    )
    product_id: Mapped[int] = mc(
        Integer,
        ForeignKey("products.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    quantity: Mapped[int] = mc(Integer, nullable=False, default=1)
    created_at: Mapped[datetime] = mc(
        DateTime(timezone=True),
        server_default=func.now(), 
        nullable=False
    )
    updated_at: Mapped[datetime] = mc(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False
    )

    buyer = relationship(
        'User',
        back_populates='cart_items'
    )
    product = relationship(
        'Product',
        back_populates='cart_items'
    )