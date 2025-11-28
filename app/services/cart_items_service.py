from fastapi import HTTPException, status, Response
from sqlalchemy.ext.asyncio import AsyncSession
from decimal import Decimal

from app.models.cart_items_model import CartItem as CartItemModel

from app.repositories.cart_items_repo import CartItemRepo


class CartItemService:
    def __init__(self, db: AsyncSession):
        self.repo = CartItemRepo(db)
        self.db = db

    async def get_cart(self, buyer_id: int) -> dict:

        items = await self.repo.get_cart_buyer(buyer_id=buyer_id)

        total_quantity = sum(item.quantity for item in items)
        price_items = (
            Decimal(item.quantity)
            * (item.product.price if item.product.price is not None else Decimal("0"))
            for item in items
        )
        total_price_decimal = sum(price_items, Decimal("0"))

        return {
            "buyer_id": buyer_id,
            "items": items,
            "total_quantity": total_quantity,
            "total_price": total_price_decimal,
        }

    async def add_item_to_cart(self, item_data: dict, buyer_id: int):

        product = await self.repo.get_active_product(product_id=item_data["product_id"])

        if not product:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Product not found or not active",
            )

        if item_data["quantity"] > product.stock:
            raise HTTPException(status_code=400, detail="Not enough stock")

        cart_item = await self.repo.get_product_cart(
            buyer_id=buyer_id, product_id=item_data["product_id"]
        )

        if cart_item:
            new_quantity = cart_item.quantity + item_data["quantity"]
            if product.stock < new_quantity:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Cannot order more than stock",
                )
            cart_item.quantity = new_quantity

        else:
            cart_item = CartItemModel(buyer_id=buyer_id, **item_data)

            self.db.add(cart_item)

        await self.db.commit()
        await self.db.refresh(cart_item, ['product'])
        return cart_item

    async def update_cart_item(self, product_id: int, quantity: int, buyer_id: int):

        product = await self.repo.get_active_product(product_id=product_id)
        if not product:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Product not found or not active",
            )

        cart_item = await self.repo.get_product_cart(
            buyer_id=buyer_id, product_id=product_id
        )
        if not cart_item:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="Cart item not found"
            )

        if product.stock < quantity:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST, detail="Not enough stock"
            )

        cart_item.quantity = quantity
        await self.db.commit()
        await self.db.refresh(cart_item, ['product'])
        return cart_item

    async def remove_item_from_cart(self, product_id: int, buyer_id: int):
        cart_item = await self.repo.get_product_cart(buyer_id=buyer_id, product_id=product_id)
        if not cart_item:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="Cart item not found"
            )

        await self.db.delete(cart_item)
        await self.db.commit()
        return Response(status_code=status.HTTP_204_NO_CONTENT)


    async def clear_cart(self, buyer_id: int):
        await self.repo.clear_cart(buyer_id=buyer_id)

        await self.db.commit()

        return Response(status_code=status.HTTP_204_NO_CONTENT)
