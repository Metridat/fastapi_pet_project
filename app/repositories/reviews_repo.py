from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func

from app.models.categories_model import Category as CategoryModel
from app.models.products_model import Product as ProductModel
from app.models.reviews_model import Review as ReviewModel


class ReviewsRepo:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_reviews(self, active: bool = True):
        reviews = await self.db.scalars(
            select(ReviewModel)
            .join(ProductModel)
            .join(CategoryModel)
            .where(
                CategoryModel.is_active.is_(True),
                ProductModel.is_active.is_(True),
                ReviewModel.is_active.is_(active),
            )
        )
        return reviews.all()

    async def get_review(self, review_id: int, active: bool = True):
        return await self.db.scalar(
            select(ReviewModel)
            .join(ProductModel)
            .join(CategoryModel)
            .where(
                ReviewModel.id == review_id,
                ReviewModel.is_active.is_(active),
                ProductModel.is_active.is_(True),
                CategoryModel.is_active.is_(True),
            )
        )

    async def check_active_product(self, product_id: int):
        return await self.db.scalar(
            select(ProductModel)
            .join(CategoryModel)
            .where(
                ProductModel.id == product_id,
                ProductModel.is_active.is_(True),
                CategoryModel.is_active.is_(True),
            )
        )

    async def get_review_product(self, product_id: int):
        reviews_for_products = await self.db.scalars(
            select(ReviewModel)
            .join(ProductModel)
            .join(CategoryModel)
            .where(
                ReviewModel.product_id == product_id,
                ReviewModel.is_active.is_(True),
                ProductModel.is_active.is_(True),
                CategoryModel.is_active.is_(True),
            )
        )
        return reviews_for_products.all()

    async def get_review_user(self, buyer_id: int, product_id: int):
        return await self.db.scalar(
            select(ReviewModel).where(
                ReviewModel.buyer_id == buyer_id,
                ReviewModel.product_id == product_id,
                ReviewModel.is_active.is_(True),
            )
        )

    async def get_avg_rating(self, product_id: int):
        return await self.db.scalar(
            select(func.avg(ReviewModel.grade)).where(
                ReviewModel.product_id == product_id, ReviewModel.is_active.is_(True)
            )
        )

    async def update_product_rating(self, product_id: int):
        product = await self.check_active_product(product_id)
        if not product:
            return None
        avg_grade = await self.get_avg_rating(product_id)
        product.rating = round(avg_grade or 0, 2)

        self.db.add(product)
        await self.db.commit()
        await self.db.refresh(product)
