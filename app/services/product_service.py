from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.products_model import Product as ProductModel
from app.repositories.products_repo import ProductRepo


from typing import Any

class ProductService:
    
    def __init__(self, db: AsyncSession):
        self.repo = ProductRepo(db)
        self.db = db



    async def list_products(
            self,
            page: int = 1,
            page_size: int = 20,
            category_id: int | None = None,
            search: str | None = None,
            min_price: float | None = None,
            max_price: float | None = None,
            in_stock: bool | None = None,
            seller_id: int | None = None,
            min_rating: float | None = None,
            max_rating: float | None = None
    ):
        if min_price is not None and max_price is not None and min_price > max_price:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="min_price cannot be greater than max_price",
            )
        if min_rating is not None and max_rating is not None and min_rating > max_rating:
            raise HTTPException(
        status_code=status.HTTP_400_BAD_REQUEST,
        detail="min_rating не может быть больше max_rating"
    )

        filters: list[Any] = [ProductModel.is_active.is_(True)]
        if category_id is not None:
            filters.append(ProductModel.category_id == category_id)

        if min_price is not None:
            filters.append(ProductModel.price >= min_price)

        if max_price is not None:
            filters.append(ProductModel.price <= max_price)

        if in_stock is not None:
            filters.append(ProductModel.stock > 0 if in_stock else ProductModel.stock == 0)
    
        if seller_id is not None:
            filters.append(ProductModel.seller_id == seller_id)

        if min_rating is not None:
            filters.append(ProductModel.rating >= min_rating)
        if max_rating is not None:
            filters.append(ProductModel.rating <= max_rating)

        items, total = await self.repo.get_products(
            filters=filters,
            search=search,
            page=page,
            page_size=page_size
        )

        return {
            'items': items,
            'total': total,
            'page': page,
            'page_size': page_size
        }



    async def get_all_products(self, active: bool = True):

        return await self.repo.get_all_products(active=active)



    async def get_product(self, product_id: int, active: bool = True):

        product = await self.repo.get_product(product_id=product_id, active=active)
        if not product:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='Product not found or not active')
        
        return product



    async def create_product(self, data_create: dict, seller_id: int):

        product_exits = await self.repo.get_by_name(name=data_create['name'])
        if product_exits:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                                detail='Product with this name already exist')
        
        check_category = await self.repo.checking_category_activity(category_id=data_create['category_id'])
        if not check_category:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='Category not found or not active')
        
        product = ProductModel(**data_create, seller_id=seller_id)
        self.db.add(product)
        await self.db.commit()
        await self.db.refresh(product)
        return product



    async def update_product(self, product_id: int, seller_id: int, update_data: dict):

        product = await self.repo.get_product(product_id)
        if not product:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='Product not found or not active')
        
        if product.seller_id != seller_id:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN,
                                detail='You can only update your own products')
        
        if 'name' in update_data:
            check_name = await self.repo.get_by_name(update_data['name'])
            if check_name and check_name.id != product.id:
                    raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                                    detail='Product with this name already exist')  
            
        
        for key, value in update_data.items():
            setattr(product, key, value)
        await self.db.commit()
        await self.db.refresh(product)
        return product        



    async def get_all_products_for_category(self, category_id: int):
        
        return await self.repo.get_products_category(category_id=category_id)
    



    async def delete_product(self, product_id: int):

        product = await self.repo.get_product(product_id)
        if not product:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='Product not found or not active')
        
        product.is_active = False
        await self.db.commit()
        return {"message": f"Product '{product.name}' deleted successfully"}




    async def activation_product(self, product_id: int):

        product = await self.repo.get_product(product_id, active=False)
        if not product:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='Product not found or already active')
        
        product.is_active = True
        await self.db.commit()
        return {"message": f"Product '{product.name}' restored successfully"}
