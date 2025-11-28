from fastapi import APIRouter, Depends, status
from fastapi.security import OAuth2PasswordRequestForm

from app.auth.dependencies import get_current_user_with_role

from app.services.user_service import UserService
from app.dependencies import get_user_service

from app.models.users_model import User as UserModel, UserRole
from app.schemas.users import UserSchema, UserCreateSchema





router = APIRouter(
    prefix='/users',
    tags=['Users']
)


@router.post('/', response_model=UserSchema, status_code=status.HTTP_201_CREATED)
async def create_user(user: UserCreateSchema, service: UserService = Depends(get_user_service)):
    return await service.create_user(user.model_dump(exclude_unset=True))



@router.post('/token')
async def login(form_data: OAuth2PasswordRequestForm = Depends(), service: UserService = Depends(get_user_service)):
    return await service.login(form_data=form_data)



@router.post('/refresh-token')
async def refresh_token(refresh_token: str, service: UserService = Depends(get_user_service)):
    return await service.refresh_token(refresh_token=refresh_token)



@router.get('/', response_model=list[UserSchema])
async def get_all_users(service: UserService = Depends(get_user_service),
                        current_admin: UserModel = Depends(get_current_user_with_role(UserRole.admin))):
    return await service.get_all_users()




@router.delete('/{user_id}', response_model=UserSchema)
async def delete_user_logic(user_id: int, service: UserService = Depends(get_user_service), 
                            current_admin: UserModel = Depends(get_current_user_with_role(UserRole.admin))):
    
    return await service.delete_user_logic(user_id=user_id)