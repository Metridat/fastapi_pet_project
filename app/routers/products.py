from fastapi import APIRouter, Depends, status, Path, Query

from typing import Annotated

from app.auth.dependencies import get_current_user_with_role
from app.services.product_service import ProductService

from app.models.users_model import User as UserModel, UserRole
from app.schemas.products import (
    ProductSchema, 
    ProductCreateSchema, 
    ProductUpgradeSchema,
    ProductList)

from app.dependencies import get_product_service



router = APIRouter(
    prefix='/products',
    tags=['Products']
)


@router.get('/', response_model=ProductList)
async def get_products(
    service: ProductService = Depends(get_product_service),
    page: int = Query(1, ge=1),
    page_size: int = Query(20, le=100),
    category_id: int | None = Query(None),
    search: str | None = Query(None, min_length=1),
    min_price: float | None = Query(None, ge=0),
    max_price: float | None = Query(None, ge=0),
    in_stock: bool | None = Query(None),
    seller_id: int | None = Query(None),
    min_rating: float | None = Query(None, ge=0, le=5),
    max_rating: float | None = Query(None, ge=0, le=5)
):


    return await service.list_products(
        page=page,
        page_size=page_size,
        category_id=category_id,
        search=search,
        min_price=min_price,
        max_price=max_price,
        seller_id=seller_id,
        in_stock=in_stock,
        min_rating=min_rating,
        max_rating=max_rating
    )


@router.get('/all', response_model=list[ProductSchema])
async def get_all_products(service: ProductService = Depends(get_product_service)):


    return await service.get_all_products()


@router.get('/nonactive', response_model=list[ProductSchema])
async def get_nonactive_products(service: ProductService = Depends(get_product_service)):


    return await service.get_all_products(active=False)



@router.get('/{product_id}', response_model=ProductSchema)
async def get_product(product_id: Annotated[int, Path(ge=1)], 
                      service: ProductService = Depends(get_product_service)):


    return await service.get_product(product_id, active=True)
    



@router.post('/', response_model=ProductSchema, status_code=status.HTTP_201_CREATED)
async def create_product(new_product: ProductCreateSchema, 
                         service: ProductService = Depends(get_product_service),
                         current_seller: UserModel = Depends(get_current_user_with_role(UserRole.seller))):
    

    return await service.create_product(
        data_create=new_product.model_dump(exclude_unset=True), 
        seller_id=current_seller.id)




@router.put('/{product_id}', response_model=ProductSchema)
async def update_product(new_product: ProductUpgradeSchema, 
                         product_id: Annotated[int, Path(ge=1)], 
                         service: ProductService = Depends(get_product_service),
                        current_seller: UserModel = Depends(get_current_user_with_role(UserRole.seller))):
    

    return await service.update_product(
        product_id=product_id , 
        seller_id=current_seller.id, 
        update_data=new_product.model_dump(exclude_unset=True))





@router.get('/category/{category_id}', response_model=list[ProductSchema])
async def get_all_products_for_category(category_id: Annotated[int, Path(ge=1)], 
                                        service: ProductService = Depends(get_product_service)):
    

    return await service.get_all_products_for_category(category_id=category_id)
    



@router.delete('/{product_id}', response_model=dict)
async def delete_product(product_id: Annotated[int, Path(ge=1)], 
                         service: ProductService = Depends(get_product_service),
                        current_admin: UserModel = Depends(get_current_user_with_role(UserRole.admin))):
    

    return await service.delete_product(product_id=product_id)




@router.patch('/{product_id}/activate', response_model=dict)
async def activation_product(product_id: Annotated[int, Path(ge=1)], 
                             service: ProductService = Depends(get_product_service),
                             current_admin: UserModel = Depends(get_current_user_with_role(UserRole.admin))):
    

    return await service.activation_product(product_id=product_id)