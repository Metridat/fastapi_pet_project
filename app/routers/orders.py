from fastapi import APIRouter, Depends, status, Query

from app.dependencies import get_order_service, OrderService

from app.auth.dependencies import get_current_user_with_role
from app.models.users_model import User as UserModel, UserRole

from app.schemas.orders import Order as OrderSchema, OrderList


router = APIRouter(prefix="/orders", tags=["Orders"])


@router.post(
    "/checkout", response_model=OrderSchema, status_code=status.HTTP_201_CREATED
)
async def checkout(
    service: OrderService = Depends(get_order_service),
    current_buyer: UserModel = Depends(get_current_user_with_role(UserRole.buyer)),
):
    return await service.create_order(current_buyer.id)


@router.get("/", response_model=OrderList)
async def list_orders(
    service: OrderService = Depends(get_order_service),
    current_buyer: UserModel = Depends(get_current_user_with_role(UserRole.buyer)),
    page: int = Query(1, ge=1),
    page_size: int = Query(10, ge=1, le=100),
):

    return await service.get_list_orders(
        buyer_id=current_buyer.id, page=page, page_size=page_size
    )



@router.get("/{order_id}", response_model=OrderSchema)
async def get_order(
    order_id: int,
    service: OrderService = Depends(get_order_service),
    current_buyer: UserModel = Depends(get_current_user_with_role(UserRole.buyer)),
):

    return await service.get_order(order_id=order_id, buyer_id=current_buyer.id)


