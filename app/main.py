from dotenv import load_dotenv

load_dotenv()

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.gzip import GZipMiddleware

from app.models import users_model
from app.logger import logger
import time


from app.routers import users, categories, products, reviews, cart_items, orders


app = FastAPI(title="FastAPI ecommerce")


origins = ["http://localhost:3000", "http://example.com"]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.add_middleware(GZipMiddleware, minimum_size=1000)


@app.middleware("http")
async def simple_logging_middleware(request: Request, call_next):
    start = time.time()

    logger.info(f"-> {request.method} {request.url.path}")

    try:
        response = await call_next(request)
    except Exception as e:
        logger.exception(f"Error: {e}")
        raise

    duration = (time.time() - start) * 1000

    logger.info(
        f"<- {request.method} {request.url.path}"
        f"{response.status_code} ({duration:.2f}ms)"
    )

    return response


app.include_router(users.router)
app.include_router(categories.router)
app.include_router(products.router)
app.include_router(reviews.router)
app.include_router(cart_items.router)
app.include_router(orders.router)


@app.get("/")
async def root():
    return {"message": "Welcome to reviews for products"}
