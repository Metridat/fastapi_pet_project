from fastapi import APIRouter, Depends, status, Path
from typing import Annotated

from app.models.users_model import User as UserModel, UserRole

from app.schemas.reviews import ReviewSchema, ReviewsCreateSchema, ReviewsUpdateSchema
from app.services.review_service import ReviewService

from app.auth.dependencies import get_current_user_with_role
from app.dependencies import get_review_service



router = APIRouter(
    prefix='/reviews',
    tags=['Reviews']
)


@router.get('/', response_model=list[ReviewSchema])
async def get_all_reviews(service: ReviewService = Depends(get_review_service)):

    return await service.get_all_reviews(active=True)




@router.get('/nonactive', response_model=list[ReviewSchema])
async def get_nonactive_reviews(service: ReviewService = Depends(get_review_service)):

    return await service.get_all_reviews(active=False)


    

@router.get('/{review_id}', response_model=ReviewSchema)
async def get_review(review_id: Annotated[int, Path(ge=1)], 
                     service: ReviewService = Depends(get_review_service)):

    return await service.get_review(review_id)
    


@router.post('/', response_model=ReviewSchema, status_code=status.HTTP_201_CREATED)
async def create_review(new_review: ReviewsCreateSchema, 
                        service: ReviewService = Depends(get_review_service),
                        current_buyer: UserModel = Depends(get_current_user_with_role(UserRole.buyer))):

   return await service.create_review(
       buyer_id=current_buyer.id, 
       create_data=new_review.model_dump(exclude_unset=True))





@router.put('/{review_id}', response_model=ReviewSchema)
async def update_review(review_id: Annotated[int, Path(ge=1)], 
                        new_review: ReviewsUpdateSchema, 
                        service: ReviewService = Depends(get_review_service),
                        current_buyer: UserModel = Depends(get_current_user_with_role(UserRole.buyer))):
    
    return await service.update_review(
        review_id=review_id,
        update_data=new_review.model_dump(exclude_unset=True),
        buyer_id=current_buyer.id)




@router.get('/products/{product_id}', response_model=list[ReviewSchema])
async def get_all_reviews_for_products(product_id: Annotated[int, Path(ge=1)], 
                                       service: ReviewService = Depends(get_review_service)):

    return await service.get_all_reviews_for_products(product_id=product_id)



@router.delete('/{review_id}', response_model=dict)
async def delete_review(review_id: Annotated[int, Path(ge=1)], 
                        service: ReviewService = Depends(get_review_service),
                        current_buyer: UserModel = Depends(get_current_user_with_role(UserRole.buyer))) -> dict:
    
    return await service.delete_review(
        review_id=review_id, 
        buyer_id=current_buyer.id)




@router.patch('/{review_id}', response_model=dict)
async def activate_review(review_id: Annotated[int, Path(ge=1)], 
                        service: ReviewService = Depends(get_review_service),
                        current_admin: UserModel = Depends(get_current_user_with_role(UserRole.admin))) -> dict:
    
    return await service.activate_review(review_id=review_id)

