from fastapi.security import OAuth2PasswordBearer
from fastapi import HTTPException, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.config import SECRET_KEY, ALGORITHM
from app.dependencies import get_async_db
from app.models.users_model import User as UserModel, UserRole
from sqlalchemy import select

import jwt


oauth2_scheme = OAuth2PasswordBearer(tokenUrl='users/token')


async def get_current_user(token: str = Depends(oauth2_scheme), db: AsyncSession = Depends(get_async_db)):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail='Could not validate credentials',
        headers={"WWW_Authenticate": "Bearer"}
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        email: str = payload.get('sub')
        if not email:
            raise credentials_exception
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,
                            detail='Token has expired',
                            headers={"WWW_Authenticate": "Bearer"})
    except jwt.InvalidTokenError:
        raise credentials_exception  
    user = await db.scalar(select(UserModel).where(UserModel.email == email,
                                                   UserModel.is_active.is_(True)))
    if not user:
        raise credentials_exception
    return user



def get_current_user_with_role(necessary_role: UserRole):
    async def dependency(current_user: UserModel = Depends(get_current_user)):

        if current_user.role.value != necessary_role.value:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN,
                             detail=f'Only {necessary_role.value} can perform this action')
        return current_user
    return dependency