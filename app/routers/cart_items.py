from fastapi import APIRouter, Depends, status, Path
from typing import Annotated

from app.models.users_model import User as UserModel, UserRole
from app.auth.dependencies import get_current_user_with_role
from app.dependencies import CartItemService, get_cart_item_service

from app.schemas.cartitems import (
    Cart,
    CartItemSchema,
    CartItemCreate,
    CartItemUpdate,
)

router = APIRouter(prefix="/cart", tags=["Cart"])


@router.get("/", response_model=Cart)
async def get_cart(
    service: CartItemService = Depends(get_cart_item_service),
    current_buyer: UserModel = Depends(get_current_user_with_role(UserRole.buyer)),
):

    return await service.get_cart(buyer_id=current_buyer.id)


@router.post("/items", response_model=CartItemSchema, status_code=status.HTTP_201_CREATED)
async def add_item_to_cart(
    payload: CartItemCreate,
    service: CartItemService = Depends(get_cart_item_service),
    current_buyer: UserModel = Depends(get_current_user_with_role(UserRole.buyer)),
):



    return await service.add_item_to_cart(
        item_data=payload.model_dump(exclude_unset=True), buyer_id=current_buyer.id
    )


@router.put('/items/{product_id}')
async def update_cart_item(
    payload: CartItemUpdate, 
    product_id: Annotated[int, Path(ge=1)],
    service: CartItemService = Depends(get_cart_item_service),
    current_buyer: UserModel = Depends(get_current_user_with_role(UserRole.buyer))):


    return await service.update_cart_item(product_id=product_id, quantity=payload.quantity, buyer_id=current_buyer.id)


@router.delete('/items/{product_id}', status_code=status.HTTP_204_NO_CONTENT)
async def remove_item_from_cart(
    product_id: int,
    service: CartItemService = Depends(get_cart_item_service),
    current_buyer: UserModel = Depends(get_current_user_with_role(UserRole.buyer))
):
    return await service.remove_item_from_cart(
        product_id=product_id,
        buyer_id=current_buyer.id
    )


@router.delete('/', status_code=status.HTTP_204_NO_CONTENT)
async def clear_cart(
    service: CartItemService = Depends(get_cart_item_service),
    current_buyer: UserModel = Depends(get_current_user_with_role(UserRole.buyer))):

    return await service.clear_cart(
        buyer_id=current_buyer.id
    )