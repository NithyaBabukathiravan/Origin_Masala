
from decimal import Decimal
import re

from app.db.session import SessionLocal
from app.models import Product, Category


PRODUCTS = [
    {
        "name": "Sambar Masala",
        "category": "South Indian Masalas",
        "price": 120,
        "mrp": 150,
        "weight": "100 g",
        "image": "/images/sambarmasla.jpeg",
    },
    {
        "name": "Chicken Masala",
        "category": "Blended Masalas",
        "price": 140,
        "mrp": 170,
        "weight": "100 g",
        "image": "/images/chickenmasala.jpeg",
    },
    {
        "name": "Chicken 65 Masala",
        "category": "Blended Masalas",
        "price": 130,
        "mrp": 160,
        "weight": "100 g",
        "image": "/images/chicken65masala.jpeg",
    },
    {
        "name": "Chicken Fry Masala",
        "category": "Blended Masalas",
        "price": 130,
        "mrp": 160,
        "weight": "100 g",
        "image": "/images/chickenfrymasla.jpeg",
    },
    {
        "name": "Dosa Podi",
        "category": "South Indian Masalas",
        "price": 90,
        "mrp": 120,
        "weight": "150 g",
        "image": "/images/dosapodi.jpeg",
    },
    {
        "name": "Egg Rice Masala",
        "category": "Blended Masalas",
        "price": 110,
        "mrp": 140,
        "weight": "100 g",
        "image": "/images/eggricemasala.jpeg",
    },
    {
        "name": "Fish Masala",
        "category": "Blended Masalas",
        "price": 130,
        "mrp": 160,
        "weight": "100 g",
        "image": "/images/fishmasala.jpeg",
    },
    {
        "name": "Idly Podi",
        "category": "South Indian Masalas",
        "price": 100,
        "mrp": 125,
        "weight": "150 g",
        "image": "/images/idlypodi.jpeg",
    },
    {
        "name": "Mutton Masala",
        "category": "Blended Masalas",
        "price": 150,
        "mrp": 180,
        "weight": "100 g",
        "image": "/images/muttonmasala.jpeg",
    },
    {
        "name": "Veg Fried Rice Masala",
        "category": "Blended Masalas",
        "price": 110,
        "mrp": 140,
        "weight": "100 g",
        "image": "/images/vegfriedricemasla.jpeg",
    },
    {
        "name": "Biriyani Masala",
        "category": "Blended Masalas",
        "price": 120,
        "mrp": 150,
        "weight": "100 g",
        "image": "/images/b1.jpeg",
    },
    {
        "name": "Cumin Seeds",
        "category": "Whole Spices",
        "price": 100,
        "mrp": 120,
        "weight": "100 g",
        "image": "/images/cumin-seeds.jpeg",
    },
    {
        "name": "Cardamom",
        "category": "Whole Spices",
        "price": 150,
        "mrp": 180,
        "weight": "50 g",
        "image": "/images/cardamom.jpeg",
    },
    {
        "name": "Cinnamon",
        "category": "Whole Spices",
        "price": 120,
        "mrp": 145,
        "weight": "100 g",
        "image": "/images/cinnamon.jpeg",
    },
    {
        "name": "Cloves",
        "category": "Whole Spices",
        "price": 130,
        "mrp": 155,
        "weight": "50 g",
        "image": "/images/cloves.jpeg",
    },
    {
        "name": "Fennel Seeds",
        "category": "Whole Spices",
        "price": 80,
        "mrp": 100,
        "weight": "100 g",
        "image": "/images/fennel-seeds.jpeg",
    },
    {
        "name": "Red Chilli Powder",
        "category": "Powdered Spices",
        "price": 90,
        "mrp": 110,
        "weight": "100 g",
        "image": "/images/r2.jpeg",
    },
    {
        "name": "Turmeric Powder",
        "category": "Powdered Spices",
        "price": 75,
        "mrp": 95,
        "weight": "100 g",
        "image": "/images/t2.jpeg",
    },
    {
        "name": "Black Pepper Powder",
        "category": "Powdered Spices",
        "price": 110,
        "mrp": 135,
        "weight": "100 g",
        "image": "/images/b3.jpeg",
    },
    {
        "name": "Garam Masala",
        "category": "South Indian Masalas",
        "price": 100,
        "mrp": 125,
        "weight": "100 g",
        "image": "/images/g1.jpeg",
    },
    {
        "name": "Chicken Masala",
        "category": "South Indian Masalas",
        "price": 95,
        "mrp": 120,
        "weight": "100 g",
        "image": "/images/chickenmasala.jpeg",
    },
    {
        "name": "Rasam Powder",
        "category": "South Indian Masalas",
        "price": 80,
        "mrp": 100,
        "weight": "100 g",
        "image": "/images/r1.jpeg",
    },
    {
        "name": "Spice Gift Box",
        "category": "Special Masalas",
        "price": 499,
        "mrp": 599,
        "weight": "Combo Pack",
        "image": "/images/spice-gift-box.jpeg",
    },
    {
        "name": "Spice Starter Kit",
        "category": "Special Masalas",
        "price": 399,
        "mrp": 499,
        "weight": "Combo Pack",
        "image": "/images/spice-starter-kit.jpeg",
    },
]


def make_slug(value):
    value = value.lower().strip()
    return re.sub(r"[^a-z0-9]+", "-", value).strip("-")


def main():
    db = SessionLocal()
    added = 0
    skipped = 0

    try:
        categories = {
            category.name: category
            for category in db.query(Category).all()
        }

        for item in PRODUCTS:
            category = categories.get(item["category"])

            if category is None:
                raise ValueError(
                    f"Category not found: {item['category']}"
                )

            # Skip an existing product with the same name and category.
            existing = (
                db.query(Product)
                .filter(
                    Product.name == item["name"],
                    Product.category_id == category.id,
                )
                .first()
            )

            if existing:
                print(f"SKIPPED: {item['name']} ({category.name})")
                skipped += 1
                continue

            base_slug = make_slug(item["name"])
            slug = base_slug

            # Keep existing unique slugs unchanged.
            slug_exists = (
                db.query(Product)
                .filter(Product.slug == slug)
                .first()
            )

            if slug_exists:
                slug = f"{base_slug}-{category.slug}"

            suffix = 2
            while (
                db.query(Product)
                .filter(Product.slug == slug)
                .first()
            ):
                slug = f"{base_slug}-{category.slug}-{suffix}"
                suffix += 1

            product = Product(
                name=item["name"],
                slug=slug,
                category_id=category.id,
                description=f"{item['name']} - quality Indian spices.",
                price=Decimal(str(item["price"])),
                original_price=Decimal(str(item["mrp"])),
                image=item["image"],
                stock=20,
                net_weight=item["weight"],
                is_featured=False,
                is_active=True,
                rating=0,
                rating_count=0,
            )

            db.add(product)
            db.flush()
            print(f"ADDED: {item['name']} ({category.name})")
            added += 1

        db.commit()

        print("\nImport completed successfully.")
        print("Added:", added)
        print("Skipped:", skipped)
        print("Total products in database:", db.query(Product).count())

    except Exception:
        db.rollback()
        raise
    finally:
        db.close()


if __name__ == "__main__":
    main()
