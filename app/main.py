from dotenv import load_dotenv
load_dotenv()

from fastapi import FastAPI
from app.models import users_model


from app.routers import (
    users,
    categories,
    products,
    reviews,
    cart_items,
    orders
)


app = FastAPI(title='Reviews for products')

app.include_router(users.router)
app.include_router(categories.router)
app.include_router(products.router)
app.include_router(reviews.router)
app.include_router(cart_items.router)
app.include_router(orders.router)



@app.get('/')
async def root():
    return {'message': 'Welcome to reviews for products'}

