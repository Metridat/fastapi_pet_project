from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.models.categories_model import Category as CategoryModel



class CategoryRepo:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_category(self, category_id: int, active: bool = True):
        return await self.db.scalar(select(CategoryModel).where(
            CategoryModel.id == category_id, 
            CategoryModel.is_active.is_(active)))

    async def get_all_categories(self, active: bool = True):
        categories = await self.db.scalars(select(CategoryModel).where(
            CategoryModel.is_active.is_(active)))
        return categories.all()

    async def get_by_name(self, name: str):
        return await self.db.scalar(
        select(CategoryModel).where(CategoryModel.name == name)
        )