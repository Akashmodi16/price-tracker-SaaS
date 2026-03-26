from fastapi import FastAPI, Depends
from sqlalchemy.orm import Session
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
import os

from .database import engine, SessionLocal
from . import models

models.Base.metadata.create_all(bind=engine)

app = FastAPI(title="Price Tracker API")

# Serve static files
app.mount(
    "/static",
    StaticFiles(directory=os.path.join(os.getcwd(), "static")),
    name="static"
)

# ------------------ DB Dependency ------------------
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


# ------------------ Schemas ------------------
class ProductCreate(BaseModel):
    url: str


# ------------------ Routes ------------------

@app.get("/")
def root():
    return {"message": "API running 🚀"}


@app.get("/products")
def get_products(db: Session = Depends(get_db)):
    products = db.query(models.Product).all()
    result = []

    for product in products:

        if not product.url or not product.url.startswith("http"):
            continue

        latest_price = (
            db.query(models.PriceHistory)
            .filter(models.PriceHistory.product_id == product.id)
            .order_by(models.PriceHistory.timestamp.desc())
            .first()
        )

        if not latest_price or latest_price.price == 0:
            continue

        result.append({
            "id": product.id,
            "url": product.url,
            "price": latest_price.price
        })

    return result


@app.get("/history/{product_id}")
def get_price_history(product_id: int, db: Session = Depends(get_db)):
    prices = (
        db.query(models.PriceHistory)
        .filter(
            models.PriceHistory.product_id == product_id,
            models.PriceHistory.price > 0
        )
        .order_by(models.PriceHistory.timestamp)
        .all()
    )

    return [
        {
            "price": p.price,
            "timestamp": p.timestamp
        }
        for p in prices
    ]


@app.post("/add-product")
def add_product(data: ProductCreate, db: Session = Depends(get_db)):
    product = models.Product(url=data.url)
    db.add(product)
    db.commit()
    db.refresh(product)

    return {"message": "Product added successfully"}