from fastapi import FastAPI, Depends
from sqlalchemy.orm import Session
from fastapi.staticfiles import StaticFiles

from pydantic import BaseModel

from .database import engine, SessionLocal
from . import models
from .utils import clean_price

models.Base.metadata.create_all(bind=engine)

app = FastAPI(title="Price Tracker API")

app.mount("/static", StaticFiles(directory="static"), name="static")


# Dependency
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


class ProductCreate(BaseModel):
    url: str
    price: str  # raw string

@app.get("/")
def root():
    return {"message": "Price Tracker API is running 🚀"}

@app.post("/track")
def track_product(product: ProductCreate, db: Session = Depends(get_db)):
    print("Incoming data:", product.dict())

    # 🔍 Check if product exists
    db_product = db.query(models.Product).filter(models.Product.url == product.url).first()

    if not db_product:
        db_product = models.Product(url=product.url)
        db.add(db_product)
        db.commit()
        db.refresh(db_product)

    # 🔄 Clean price
    cleaned_price = clean_price(product.price)

    # 💾 Save price history
    price_entry = models.PriceHistory(
        price=cleaned_price,
        product_id=db_product.id
    )

    db.add(price_entry)
    db.commit()

    return {
        "status": "success",
        "price_saved": cleaned_price,
        "product_id": db_product.id
    }

@app.get("/products")
def get_products(db: Session = Depends(get_db)):
    products = db.query(models.Product).all()

    result = []

    for product in products:

        # 🚫 Skip invalid URLs
        if not product.url or not product.url.startswith("http"):
            continue

        latest_price = (
            db.query(models.PriceHistory)
            .filter(models.PriceHistory.product_id == product.id)
            .order_by(models.PriceHistory.timestamp.desc())
            .first()
        )

        # 🚫 Skip invalid prices
        if not latest_price or latest_price.price == 0:
            continue

        result.append({
    "id": product.id,   # 👈 ADD HERE
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
            models.PriceHistory.price > 0   # 👈 FILTER HERE
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