from sqlalchemy import select, delete, update, func
from sqlalchemy.orm import selectinload
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.orders_model import Order as OrderModel, OrderItem as OrderItemModel
from app.models.cart_items_model import CartItem as CartItemModel
from app.models.products_model import Product as ProductModel


class OrderRepo:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def load_order_with_items(self, order_id: int):
        return await self.db.scalar(
            select(OrderModel)
            .options(
                selectinload(OrderModel.items).selectinload(OrderItemModel.product)
            )
            .where(OrderModel.id == order_id)
        )

    async def get_cart_items(self, buyer_id: int):
        return (
            await self.db.scalars(
                select(CartItemModel)
                .options(selectinload(CartItemModel.product))
                .where(CartItemModel.buyer_id == buyer_id)
                .order_by(CartItemModel.id)
            )
        ).all()

    async def delete_cart_items(self, buyer_id: int):
        await self.db.execute(
            delete(CartItemModel).where(CartItemModel.buyer_id == buyer_id)
        )

    async def decrease_stock(self, product_id: int, qty: int):
        return (
            await self.db.execute(
                update(ProductModel)
                .where(ProductModel.id == product_id, ProductModel.stock >= qty)
                .values(stock=ProductModel.stock - qty)
                .returning(ProductModel.id)
            )
        ).scalar()



    async def get_total_orders(self, buyer_id: int):
        return await self.db.scalar(
            select(func.count(OrderModel.id)).where(OrderModel.buyer_id == buyer_id)
        )


    async def get_orders(self, buyer_id: int, page: int, page_size: int):
        return (
            await self.db.scalars(
                select(OrderModel)
                .options(
                    selectinload(OrderModel.items).selectinload(OrderItemModel.product)
                )
                .where(OrderModel.buyer_id == buyer_id)
                .order_by(OrderModel.created_at.desc())
                .offset((page - 1) * page_size)
                .limit(page_size)
            )
        ).all()
