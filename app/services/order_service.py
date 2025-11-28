from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from decimal import Decimal

from app.repositories.orders_repo import OrderRepo
from app.schemas.orders import OrderList, Order as OrderSchema
from app.models.orders_model import Order as OrderModel, OrderItem as OrderItemModel


class OrderService:
    def __init__(self, db: AsyncSession):
        self.order_repo = OrderRepo(db)
        self.db = db



    async def create_order(self, buyer_id: int):

        cart_items = await self.order_repo.get_cart_items(buyer_id=buyer_id)
        if not cart_items:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST, detail="Cart is empty"
            )

        order = OrderModel(buyer_id=buyer_id)
        total_amount = Decimal("0")

        for cart_item in cart_items:
            product = cart_item.product

            if not product or not product.is_active:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"Product {cart_item.product_id} is unavailable",
                )

            unit_price = product.price
            if unit_price is None:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"Product {product.name} has no price set",
                )

            updated_id = await self.order_repo.decrease_stock(
                product_id=cart_item.product_id, qty=cart_item.quantity
            )
            if not updated_id:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"Not enough stock for product {product.name}",
                )

            total_price = unit_price * cart_item.quantity
            total_amount += total_price

            order_item = OrderItemModel(
                product_id=cart_item.product_id,
                quantity=cart_item.quantity,
                unit_price=unit_price,
                total_price=total_price,
            )
            order.items.append(order_item)

        order.total_amount = total_amount
        self.db.add(order)

        await self.order_repo.delete_cart_items(buyer_id=buyer_id)
        
        await self.db.commit()

        created_order = await self.order_repo.load_order_with_items(order_id=order.id)
        if not created_order:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Order was created but cannot be loaded",
            )

        return created_order



    async def get_list_orders(self, buyer_id: int, page: int, page_size: int):
        total = await self.order_repo.get_total_orders(buyer_id=buyer_id)

        orders = await self.order_repo.get_orders(
            buyer_id=buyer_id, page=page, page_size=page_size
        )

        pydantic_orders = [
            OrderSchema.model_validate(order, from_attributes=True) for order in orders
        ]

        return OrderList(
            items=pydantic_orders, total=total or 0, page=page, page_size=page_size
        )


    async def get_order(self, order_id: int, buyer_id: int):
        order = await self.order_repo.load_order_with_items(order_id=order_id)

        if not order or order.buyer_id != buyer_id:
            HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="Order not found"
            )

        return order

