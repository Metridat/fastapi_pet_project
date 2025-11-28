from sqlalchemy import select, delete
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.cart_items_model import CartItem as CartItemModel
from app.models.products_model import Product as ProductModel
from app.models.categories_model import Category as CategoryModel

from sqlalchemy.orm import selectinload


class CartItemRepo:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_cart_buyer(self, buyer_id: int):

        return (
            await self.db.scalars(
                select(CartItemModel)
                .options(selectinload(CartItemModel.product))
                .where(
                    CartItemModel.buyer_id == buyer_id,
                )
                .order_by(CartItemModel.id)
            )
        ).all()

    async def get_active_product(self, product_id: int):

        return await self.db.scalar(
            select(ProductModel)
            .join(CategoryModel)
            .where(
                ProductModel.id == product_id,
                ProductModel.is_active.is_(True),
                CategoryModel.is_active.is_(True),
            )
        )

    async def get_product_cart(
        self, buyer_id: int, product_id: int
    ) -> CartItemModel | None:

        return await self.db.scalar(
            select(CartItemModel)
            .join(ProductModel)
            .options(selectinload(CartItemModel.product))
            .where(
                CartItemModel.buyer_id == buyer_id,
                CartItemModel.product_id == product_id
            )
        )


    async def clear_cart(self, buyer_id: int):

        await self.db.execute(delete(CartItemModel).where(CartItemModel.buyer_id == buyer_id))
        