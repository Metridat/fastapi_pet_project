from fastapi import APIRouter, Depends, status, Path
from typing import Annotated


from app.dependencies import get_category_service
from app.schemas.categories import CategorySchema, CreateCategorySchema
from app.models.users_model import User as UserModel, UserRole
from app.auth.dependencies import get_current_user_with_role

from app.services.category_service import CategoryService



router = APIRouter(
    prefix='/categories',
    tags=['Categories']
)



@router.get('/', response_model=list[CategorySchema])
async def get_all_catigories(service: CategoryService = Depends(get_category_service)):

    
    return await service.get_all_catigories(active=True)




@router.get('/nonactive', response_model=list[CategorySchema])
async def get_nonactive_catigories(service: CategoryService = Depends(get_category_service)):


    return await service.get_all_catigories(active=False)




@router.get('/{category_id}', response_model=CategorySchema)
async def get_category(category_id: Annotated[int, Path(ge=1)], 
                       service: CategoryService = Depends(get_category_service)):
    
    return await service.get_category(category_id=category_id)
    



@router.post('/', response_model=CategorySchema, status_code=status.HTTP_201_CREATED)
async def create_category(category: CreateCategorySchema, 
                          service: CategoryService = Depends(get_category_service), 
                          current_admin: UserModel = Depends(get_current_user_with_role(UserRole.admin))):
    
    return await service.create_category(name=category.name)
    
   


@router.put('/{category_id}', response_model=CategorySchema)
async def upgrade_category(category_id: Annotated[int, Path(ge=1)], 
                          new_category: CreateCategorySchema,
                          service: CategoryService = Depends(get_category_service),
                          current_admin: UserModel = Depends(get_current_user_with_role(UserRole.admin))):
    
    return await service.update_category(
        category_id, 
        new_category.model_dump(exclude_unset=True))
    



@router.delete('/{category_id}', response_model=dict)
async def delete_category(category_id: Annotated[int, Path(ge=1)],
                          service: CategoryService = Depends(get_category_service),
                          current_admin: UserModel = Depends(get_current_user_with_role(UserRole.admin))):
    

    return await service.delete_category(category_id)





@router.patch('/{category_id}/activate', response_model=dict)
async def category_activation(category_id: Annotated[int, Path(ge=1)], 
                          service: CategoryService = Depends(get_category_service),
                        current_admin: UserModel = Depends(get_current_user_with_role(UserRole.admin))):
    

    return await service.category_activation(category_id)
