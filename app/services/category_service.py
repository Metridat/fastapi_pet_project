from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.repositories.categories_repo import CategoryRepo
from app.models.categories_model import Category as CategoryModel

from app.logger import logger


class CategoryService:

    def __init__(self, db: AsyncSession):
        self.repo = CategoryRepo(db)
        self.db = db

    async def get_all_catigories(self, active: bool = True):
        logger.debug(f"Fetching all categories (active={active})")

        return await self.repo.get_all_categories(active)

    async def get_category(self, category_id: int, active: bool = True):
        logger.debug(f"Fetching category id={category_id} (active={active})")

        category = await self.repo.get_category(category_id, active)
        if not category:
            logger.warning(f"Category id={category_id} not found or inactive")
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Category not found or not active",
            )
        return category

    async def create_category(self, name: str):
        logger.info(f"Create category name={name}")

        category_exist = await self.repo.get_by_name(name=name)
        if category_exist:
            logger.warning(f'Category with name "{name}" already exist')
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Category with this name already exist",
            )

        new_category = CategoryModel(name=name)

        self.db.add(new_category)
        await self.db.commit()
        await self.db.refresh(new_category)

        logger.info(f"Category created id={new_category.id}")

        return new_category

    async def update_category(self, category_id: int, update_data: dict):
        logger.info(f"Update category id={category_id}")

        category = await self.repo.get_category(category_id)
        if not category:
            logger.warning(f"Category with id={category_id} not found for update")
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Category not found or not active",
            )

        if "name" in update_data:
            check_name = await self.repo.get_by_name(update_data["name"])
            if check_name and check_name.id != category.id:
                logger.warning(f'Name "{update_data["name"]}" already taken')
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Category with this name already exist",
                )

        for key, value in update_data.items():
            setattr(category, key, value)

        await self.db.commit()
        await self.db.refresh(category)

        logger.info(f"Category updated id={category.id}")

        return category

    async def delete_category(self, category_id: int):
        logger.warning(f"Soft deleting category id={category_id}")
        category = await self.repo.get_category(category_id)
        if not category:
            logger.warning(f"Category id={category_id} not found for delete")
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Category not found or not active",
            )

        category.is_active = False
        await self.db.commit()

        logger.info(f"Category deleted id={category.id}")

        return {"message": f"Category '{category.name}' deleted successfully"}

    async def category_activation(self, category_id: int):
        logger.info(f"Activating category id={category_id}")

        category = await self.repo.get_category(category_id, active=False)
        if not category:
            logger.warning(f"Category id={category_id} not found for activation")
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Category not found or already active",
            )

        category.is_active = True
        await self.db.commit()

        logger.info(f"Category activated id={category.id}")

        return {"message": f"Category '{category.name}' restored successfully"}
