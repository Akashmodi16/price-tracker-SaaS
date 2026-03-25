from playwright.sync_api import sync_playwright
from app.database import SessionLocal
from app import models
from app.utils import clean_price


def get_price(page, url: str) -> float:
    try:
        page.goto(url, timeout=60000)
        page.wait_for_timeout(3000)

        # Amazon selectors
        whole = page.query_selector("span.a-price-whole")
        fraction = page.query_selector("span.a-price-fraction")

        if whole:
            whole_text = whole.inner_text().strip()

            if fraction:
                fraction_text = fraction.inner_text().strip()
                raw_price = f"{whole_text}{fraction_text}"
            else:
                raw_price = whole_text
        else:
            print(f"❌ Price not found for: {url}")
            return 0.0

        return clean_price(raw_price)

    except Exception as e:
        print(f"❌ Error while scraping {url}: {e}")
        return 0.0


def run_scraper():
    db = SessionLocal()
    products = db.query(models.Product).all()

    if not products:
        print("⚠️ No products found in database.")
        return

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False)
        page = browser.new_page()

        for product in products:

            # 🚫 Skip invalid URLs
            if not product.url or not product.url.startswith("http"):
                print(f"⚠️ Invalid URL skipped: {product.url}")
                continue

            print(f"\n🔍 Checking: {product.url}")

            price = get_price(page, product.url)

            # 🚫 Skip invalid price
            if price == 0.0:
                print(f"⚠️ Skipping invalid product: {product.url}")
                continue

            try:
                # 💾 Save price
                price_entry = models.PriceHistory(
                    price=price,
                    product_id=product.id
                )

                db.add(price_entry)
                db.commit()

                print(f"✅ Saved price: {price}")

                # 🚨 SAFE ALERT LOGIC
                previous_prices = (
                    db.query(models.PriceHistory)
                    .filter(models.PriceHistory.product_id == product.id)
                    .order_by(models.PriceHistory.timestamp.desc())
                    .limit(2)
                    .all()
                )

                if len(previous_prices) == 2:
                    latest = previous_prices[0].price
                    previous = previous_prices[1].price

                    if latest < previous:
                        print("\n🚨 PRICE DROP ALERT!")
                        print(f"🔗 Product: {product.url}")
                        print(f"💸 Old Price: {previous}")
                        print(f"💰 New Price: {latest}")

                        # 📧 Email Alert
                        try:
                            from app.email_utils import send_email_alert
                            send_email_alert(product.url, previous, latest)
                        except Exception as e:
                            print("❌ Email error:", e)

            except Exception as e:
                print(f"❌ DB Error for {product.url}: {e}")

        browser.close()
        db.close()


if __name__ == "__main__":
    run_scraper()