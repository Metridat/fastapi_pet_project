from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.models.users_model import User as UserModel

class UserRepo:
    def __init__(self, db: AsyncSession):
        self.db = db


    async def get_user(self, user_email, active: bool = True):
        stmt = select(UserModel).where(UserModel.email == user_email)
        if active is not None:
            stmt = stmt.where(UserModel.is_active == active)
        return await self.db.scalar(stmt)    


    async def get_active_users(self):
        users =  await self.db.scalars(select(UserModel)
                                       .where(UserModel.is_active))
        return users.all()
    

    async def delete_user(self, user_id: int):
        return await self.db.scalar(select(UserModel).where(UserModel.id == user_id,
                                                      UserModel.is_active.is_(True)))