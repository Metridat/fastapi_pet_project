from fastapi import  HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from fastapi.security import OAuth2PasswordRequestForm

from app.models.users_model import User as UserModel
from app.repositories.user_repo import UserRepo
from app.auth.security import hash_password, verify_password, create_access_token, create_refresh_token

import jwt
from app.config import SECRET_KEY, ALGORITHM



class UserService:
    
    def __init__(self, db: AsyncSession):
        self.repo = UserRepo(db)
        self.db = db



    async def create_user(self, user_data_create: dict):
        check_user = await self.repo.get_user(user_email=user_data_create['email'])
        if check_user:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                                detail='Email already registered')
        db_user = UserModel(
            email=user_data_create['email'],
            hashed_password=hash_password(user_data_create['password']),
            role=user_data_create['role']
        )
        self.db.add(db_user)
        await self.db.commit()
        await self.db.refresh(db_user)
        return db_user



    async def login(self, form_data: OAuth2PasswordRequestForm):

        user_db = await self.repo.get_user(form_data.username)
        if not user_db or not verify_password(form_data.password, user_db.hashed_password):
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,
                                detail='Incorrect email or password',
                                headers={"WWW-Authenticate": "Bearer"})
        
        if not user_db.is_active:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                                detail='Account is deactivated')
        
        access_token = create_access_token(data={'sub': user_db.email,
                                                'role': user_db.role.value,
                                                'id': user_db.id})
        refresh_token = create_refresh_token(data={'sub': user_db.email,
                                                'role': user_db.role.value,
                                                'id': user_db.id})
        return {'access_token': access_token, 'refresh_token': refresh_token, 'token_type': 'bearer'}



    async def refresh_token(self, refresh_token: str):
        credentials_exception = HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,
                                            detail='Could not validate refresh token',
                                            headers={"WWW-Authenticate": "Bearer"})
        try:
            payload = jwt.decode(refresh_token, SECRET_KEY, algorithms=[ALGORITHM])
            email: str = payload.get('sub')
            if not email:
                raise credentials_exception
        except jwt.ExpiredSignatureError:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,
                                detail='Token has expired',
                                headers={"WWW_Authenticate": "Bearer"})
        
        except jwt.InvalidTokenError:
            raise credentials_exception   
        
        user = await self.repo.get_user(email, active=True)
        if not user:
            raise credentials_exception

        access_token = create_access_token(data={'sub': user.email,
                                                'role': user.role.value,
                                                'id': user.id})
        return {'access_token': access_token, 'token_type': 'bearer'}



    async def get_all_users(self):
        return await self.repo.get_active_users()




    async def delete_user_logic(self, user_id: int):
        user_db = await self.repo.delete_user(user_id=user_id)
        if not user_db:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                                detail='User not found or not active')
        
        user_db.is_active = False
        await self.db.commit()
        await self.db.refresh(user_db)
        return user_db        