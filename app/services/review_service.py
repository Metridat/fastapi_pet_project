from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.reviews_model import Review as ReviewModel
from app.repositories.reviews_repo import ReviewsRepo
from app.logger import logger


class ReviewService:
    def __init__(self, db: AsyncSession):
        self.repo = ReviewsRepo(db)
        self.db = db

    async def get_all_reviews(self, active: bool = True):
        logger.debug(f"Service: fetching all reviews")
        return await self.repo.get_reviews()

    async def get_review(self, review_id: int):
        logger.debug(f"Service: fetching review | id={review_id}")
        review = await self.repo.get_review(review_id)

        if not review:
            logger.warning(f"Service: review not found | id={review_id}")
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Review not found or not active",
            )
        return review

    async def create_review(self, buyer_id: int, create_data: dict):
        logger.debug(f"Service: create review attempt | buyer_id={buyer_id}")
        existing_review = await self.repo.get_review_user(
            buyer_id=buyer_id, product_id=create_data["product_id"]
        )
        if existing_review:
            logger.warning(
                f'Service: review already exists | buyer_id={buyer_id}, product_id={create_data["product_id"]}'
            )
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You have already left a review for this product",
            )

        product = await self.repo.check_active_product(create_data["product_id"])
        if not product:
            logger.warning(
                f'Service: product not found for review | product_id={create_data["product_id"]}'
            )
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="It is impossible to review a non-existent product",
            )

        review = ReviewModel(**create_data, buyer_id=buyer_id)
        self.db.add(review)
        await self.db.commit()
        await self.db.refresh(review)

        logger.info(
            f"Service: review created | review_id={review.id}, product_id={review.product_id}, buyer_id={buyer_id}"
        )

        await self.repo.update_product_rating(review.product_id)

        return review

    async def update_review(self, review_id: int, update_data: dict, buyer_id: int):
        logger.debug(
            f"Service: update review attempt | id={review_id}, buyer_id={buyer_id}"
        )
        review = await self.repo.get_review(review_id)
        if not review:
            logger.warning(f"Service: review not found | id={review_id}")
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Review not found or not active",
            )

        if review.buyer_id != buyer_id:
            logger.warning(
                f"Service: update forbidden - not the owner | id={review_id}, buyer_id={buyer_id}"
            )
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You can only update your own reviews",
            )

        old_grade = review.grade

        for k, v in update_data.items():
            setattr(review, k, v)

        await self.db.commit()
        await self.db.refresh(review)

        logger.info(
            f"Service: review updated | id={review.id}, product_id={review.product_id}"
        )

        if old_grade != review.grade:
            logger.debug(
                f"Service: rating changed, updating product rating | product_id={review.product_id}"
            )
            await self.repo.update_product_rating(review.product_id)

        return review

    async def get_all_reviews_for_products(self, product_id: int):
        logger.debug(f"Service: fetching reviews for product | product_id={product_id}")
        return await self.repo.get_review_product(product_id=product_id)

    async def delete_review(self, review_id: int, buyer_id: int) -> dict:
        logger.debug(
            f"Service: delete review attempt | id={review_id}, buyer_id={buyer_id}"
        )
        review = await self.repo.get_review(review_id)
        if not review:
            logger.warning(f"Sevice: review not found | id={review_id}")
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Review not found or not active",
            )

        if review.buyer_id != buyer_id:
            logger.warning(
                f"Service: delete forbidden - not the owner | id={review_id}, buyer_id={buyer_id}"
            )
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You can only delete your own reviews",
            )

        review.is_active = False
        await self.db.commit()

        logger.info(
            f"Service: review deactivated | id={review.id}, product_id={review.product_id}"
        )

        await self.repo.update_product_rating(review.product_id)

        return {
            "message": f"Review {review.id} for product {review.product_id} successfully deleted"
        }

    async def activate_review(self, review_id: int) -> dict:
        logger.debug(f"Service: activate review attempt | id={review_id}")
        review = await self.repo.get_review(review_id, active=False)
        if not review:
            logger.warning(f"Service: activate - review not found | id={review_id}")
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Review not found or already active",
            )

        review.is_active = True

        await self.db.commit()

        logger.info(
            f"Service: review activated | id={review.id}, product_id={review.product_id}"
        )

        await self.repo.update_product_rating(review.product_id)

        return {
            "message": f"Review {review.id} for product {review.product_id} successfully activate"
        }
