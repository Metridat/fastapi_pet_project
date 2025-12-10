from fastapi import HTTPException, status, Response
from sqlalchemy.ext.asyncio import AsyncSession
from decimal import Decimal

from app.models.cart_items_model import CartItem as CartItemModel

from app.repositories.cart_items_repo import CartItemRepo
from app.logger import logger


class CartItemService:
    def __init__(self, db: AsyncSession):
        self.repo = CartItemRepo(db)
        self.db = db

    async def get_cart(self, buyer_id: int) -> dict:
        logger.debug(f"Fetching cart for buyer_id={buyer_id}")

        items = await self.repo.get_cart_buyer(buyer_id=buyer_id)

        total_quantity = sum(item.quantity for item in items)
        price_items = (
            Decimal(item.quantity)
            * (item.product.price if item.product.price is not None else Decimal("0"))
            for item in items
        )
        total_price_decimal = sum(price_items, Decimal("0"))

        logger.info(
            f"Cart fetched for buyer_id={buyer_id} "
            f"(items={len(items)}, total_price={total_price_decimal}, )"
        )

        return {
            "buyer_id": buyer_id,
            "items": items,
            "total_quantity": total_quantity,
            "total_price": total_price_decimal,
        }

    async def add_item_to_cart(self, item_data: dict, buyer_id: int):
        logger.debug(f"Adding item to cart (buyer_id={buyer_id}, data={item_data})")

        product = await self.repo.get_active_product(product_id=item_data["product_id"])

        if not product:
            logger.warning(
                f"Attempt to add non-existent or inactive product "
                f'id={item_data["product_id"]} to cart'
            )
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Product not found or not active",
            )

        if item_data["quantity"] > product.stock:
            logger.warning(f"Not enough stock for product_id={product.id}")
            raise HTTPException(status_code=400, detail="Not enough stock")

        cart_item = await self.repo.get_product_cart(
            buyer_id=buyer_id, product_id=item_data["product_id"]
        )

        if cart_item:
            logger.debug(
                f"Product exists in cart, updating quantity "
                f"(cart_item_id={cart_item.id})"
            )
            new_quantity = cart_item.quantity + item_data["quantity"]
            if product.stock < new_quantity:
                logger.warning(f"Stock limit exceeded for product_id={product.id}")
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Cannot order more than stock",
                )
            cart_item.quantity = new_quantity

        else:
            logger.debug(f'Product not in cart - createing new cart item')
            cart_item = CartItemModel(buyer_id=buyer_id, **item_data)

            self.db.add(cart_item)

        await self.db.commit()
        await self.db.refresh(cart_item, ["product"])

        logger.info(f'Item added to cart (cart_item_id={cart_item.id}) '
                    f'buyer_id={buyer_id}, quantity={cart_item.quantity}')

        return cart_item

    async def update_cart_item(self, product_id: int, quantity: int, buyer_id: int):
        logger.debug(f'Updating cart item (buyer_id{buyer_id}), product_id={product_id}'
                     f'new_quantity={quantity}')
        product = await self.repo.get_active_product(product_id=product_id)
        if not product:
            logger.warning(
                f"Attempt to update item for inactive product_id={product_id} "
            )
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Product not found or not active",
            )

        cart_item = await self.repo.get_product_cart(
            buyer_id=buyer_id, product_id=product_id
        )
        if not cart_item:
            logger.warning(f'Attempts to update non-existent cart item'
                           f'(buyer_id={buyer_id}), product_id={product_id}')
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="Cart item not found"
            )

        if product.stock < quantity:
            logger.warning(f'Stock limit exceeded for update product_id={product_id}')
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST, detail="Not enough stock"
            )

        cart_item.quantity = quantity
        await self.db.commit()
        await self.db.refresh(cart_item, ["product"])

        logger.info(f'Cart item updated (cart_item_id={cart_item.id}) '
                    f'new_quantity={quantity}')

        return cart_item

    async def remove_item_from_cart(self, product_id: int, buyer_id: int):
        logger.debug(f'Removing item from cart (buyer_id={buyer_id}), product_id={product_id}')
        cart_item = await self.repo.get_product_cart(
            buyer_id=buyer_id, product_id=product_id
        )
        if not cart_item:
            logger.warning(f'Attempt to remove non_existent cart item '
                           f'(buyer_id={buyer_id}), product_id={product_id}')
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="Cart item not found"
            )

        await self.db.delete(cart_item)
        await self.db.commit()

        logger.info(f'Cart item removed (cart_item_id={cart_item.id})')

        return Response(status_code=status.HTTP_204_NO_CONTENT)

    async def clear_cart(self, buyer_id: int):
        logger.debug(f'Cleaning cart for buyer_id={buyer_id}')
        await self.repo.clear_cart(buyer_id=buyer_id)

        await self.db.commit()

        logger.info(f'Cart cleared for buyer_id={buyer_id}')

        return Response(status_code=status.HTTP_204_NO_CONTENT)
