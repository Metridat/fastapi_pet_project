from sqlalchemy import String, Boolean
from sqlalchemy.orm import Mapped, mapped_column as mc, relationship
from app.database import Base


class Category(Base):
    __tablename__ = 'categories'

    id: Mapped[int] = mc(primary_key=True, index=True)
    name: Mapped[str] = mc(String(50), unique=True)
    is_active: Mapped[bool] = mc(Boolean, default=True)

    products = relationship(
        'Product',
        back_populates='category'
    )
 
