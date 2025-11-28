from fastapi import  HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.reviews_model import Review as ReviewModel
from app.repositories.reviews_repo import ReviewsRepo



class ReviewService:
    def __init__(self, db: AsyncSession):
        self.repo = ReviewsRepo(db)
        self.db = db




    async def get_all_reviews(self, active: bool = True):
        return await self.repo.get_reviews()




    async def get_review(self, review_id: int):
        review = await self.repo.get_review(review_id)
        
        if not review:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='Review not found or not active')
        return review



    async def create_review(self, buyer_id: int, create_data: dict):

        existing_review = await self.repo.get_review_user(buyer_id=buyer_id, product_id=create_data['product_id'])
        if existing_review:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail='You have already left a review for this product')
        
        product = await self.repo.check_active_product(create_data['product_id'])
        if not product:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='It is impossible to review a non-existent product')

        review = ReviewModel(**create_data, buyer_id=buyer_id)
        self.db.add(review)
        await self.db.commit()
        await self.db.refresh(review)

        await self.repo.update_product_rating(review.product_id)

        return review 




    async def update_review(self, review_id: int, update_data: dict, buyer_id: int):
        
        review = await self.repo.get_review(review_id)
        if not review:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='Review not found or not active')
        
        if review.buyer_id != buyer_id:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN,
                                detail='You can only update your own reviews')

        old_grade = review.grade     
    
        for k, v in update_data.items():
            setattr(review, k, v)

        await self.db.commit()
        await self.db.refresh(review)

        if old_grade != review.grade:
            await self.repo.update_product_rating(review.product_id)

        return review




    async def get_all_reviews_for_products(self, product_id: int):
        return await self.repo.get_review_product(product_id=product_id)




    async def delete_review(self, review_id: int, buyer_id: int) -> dict:

        review = await self.repo.get_review(review_id)
        if not review:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='Review not found or not active')
        
        if review.buyer_id != buyer_id:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN,
                                detail='You can only delete your own reviews')
        
        review.is_active = False
        await self.db.commit()

        await self.repo.update_product_rating(review.product_id)

        return {"message": f"Review {review.id} for product {review.product_id} successfully deleted"}




    async def activate_review(self, review_id: int) -> dict:

        review = await self.repo.get_review(review_id, active=False)
        if not review:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='Review not found or already active')
        
        review.is_active = True

        await self.db.commit()

        await self.repo.update_product_rating(review.product_id)
        
        return {"message": f"Review {review.id} for product {review.product_id} successfully activate"}

