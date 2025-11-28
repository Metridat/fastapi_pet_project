from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, desc, or_
from app.models.products_model import Product as ProductModel
from app.models.categories_model import Category as CategoryModel


class ProductRepo:
    def __init__(self, db: AsyncSession):
        self.db = db



    async def get_products(
            self,
            filters: list | None = None,
            search: str | None = None,
            page: int = 1,
            page_size: int = 20
    ):
        filters = filters or []

        total_stmt = select(func.count()).select_from(ProductModel).where(*filters)

        rank_col = None
        if search:
            search_value = search.strip()
            if search_value:
                ts_query_en = func.websearch_to_tsquery('english', search_value)
                ts_query_ru = func.websearch_to_tsquery('russian', search_value)
                
                ts_match_any = or_(
                    ProductModel.tsv.op('@@')(ts_query_en),
                    ProductModel.tsv.op('@@')(ts_query_ru)
                )
                filters.append(ts_match_any)

                rank_col = func.greatest(
                    func.ts_rank_cd(ProductModel.tsv, ts_query_en),
                    func.ts_rank_cd(ProductModel.tsv, ts_query_ru)
                ).label('rank')
                total_stmt = select(func.count()).select_from(ProductModel).where(*filters)

        total = await self.db.scalar(total_stmt) or 0

        if rank_col is not None:
            stmt = (
                select(ProductModel, rank_col)
                .where(*filters)
                .order_by(desc(rank_col), ProductModel.id)
                .offset((page - 1) * page_size)
                .limit(page_size)
            )
            result = await self.db.execute(stmt)
            items = [row[0] for row in result.all()]

        else:
            stmt = (
                select(ProductModel)
                .where(*filters)
                .order_by(ProductModel.id)
                .offset((page - 1) * page_size)
                .limit(page_size)
            )
            items = (await self.db.scalars(stmt)).all()

        return items, total


    async def get_all_products(self, active: bool = True):
        products = await self.db.scalars(select(ProductModel)
                                            .join(CategoryModel).where(CategoryModel.is_active == True, 
                                                                        ProductModel.is_active == active))
        
        return products.all()

            

    async def get_product(self, product_id: int, active: bool = True):
        return await self.db.scalar(select(ProductModel)
                                    .join(CategoryModel).where(ProductModel.id == product_id, 
                                                               CategoryModel.is_active.is_(True), 
                                                               ProductModel.is_active.is_(active)))    
    
    

    async def get_by_name(self, name: str):
        return await self.db.scalar(select(ProductModel).where(
            ProductModel.name == name))
    


    async def checking_category_activity(self, category_id: int):
        return await self.db.scalar(select(CategoryModel).where(
            CategoryModel.id == category_id, 
            CategoryModel.is_active.is_(True)))
    


    async def get_products_category(self, category_id: int):
        products = await self.db.scalars(select(ProductModel)
                                         .join(CategoryModel).where(ProductModel.category_id == category_id, 
                                                                    CategoryModel.is_active.is_(True), 
                                                                    ProductModel.is_active.is_(True)))
        
        return products.all()