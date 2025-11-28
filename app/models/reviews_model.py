from sqlalchemy.orm import Mapped, mapped_column as mc, relationship
from sqlalchemy import ForeignKey, String, Boolean, Integer, DateTime, UniqueConstraint
from datetime import datetime, timezone
from app.database import Base


class Review(Base):
    __tablename__ = "reviews"

    __table_args__ = (
        UniqueConstraint("buyer_id", "product_id", name="uq_reviews_buyer_product"),
    )

    id: Mapped[int] = mc(primary_key=True, index=True)
    buyer_id: Mapped[int] = mc(Integer, ForeignKey("users.id"), nullable=False)
    product_id: Mapped[int] = mc(
        Integer, ForeignKey("products.id", ondelete="CASCADE"), nullable=False
    )
    comment: Mapped[str | None] = mc(String(200), nullable=True)
    comment_date: Mapped[datetime] = mc(
        DateTime(timezone=True), default=lambda: datetime.now(timezone.utc)
    )
    grade: Mapped[int] = mc(Integer, nullable=False)
    is_active: Mapped[bool] = mc(Boolean, default=True)

    buyer = relationship("User", back_populates="reviews")

    product = relationship("Product", back_populates="reviews")
