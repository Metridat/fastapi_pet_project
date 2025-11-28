from app.services.category_service import CategoryService
from app.services.product_service import ProductService
from app.services.review_service import ReviewService
from app.services.user_service import UserService
from app.services.cart_items_service import CartItemService
from app.services.order_service import OrderService

from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import Depends

from app.database import async_session_maker




async def get_async_db():
    async with async_session_maker() as session:
        yield session



def get_category_service(db: AsyncSession = Depends(get_async_db)) -> CategoryService:
    return CategoryService(db)



def get_product_service(db: AsyncSession = Depends(get_async_db)) -> ProductService:
    return ProductService(db)



def get_review_service(db: AsyncSession = Depends(get_async_db)) -> ReviewService:
    return ReviewService(db)



def get_user_service(db: AsyncSession = Depends(get_async_db)) -> UserService:
    return UserService(db)


def get_cart_item_service(db: AsyncSession = Depends(get_async_db)) -> CartItemService:
    return CartItemService(db)

def get_order_service(db: AsyncSession = Depends(get_async_db)) -> OrderService:
    return OrderService(db)