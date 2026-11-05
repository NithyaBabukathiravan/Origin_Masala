
from app.db.session import SessionLocal
from app.models import Recipe
import re

RECIPES = [
    {
        "title": "Spicy Chicken Curry",
        "category": "Chicken",
        "image": "/images/cc1.jpeg",
        "cook_time": "40 mins",
        "servings": "4",
        "description": "A flavorful chicken curry made with aromatic spices.",
        "ingredients": [
            "500 g chicken",
            "2 onions, chopped",
            "2 tomatoes, chopped",
            "2 tbsp ginger-garlic paste",
            "2 tbsp oil",
            "2 tbsp chicken masala",
            "Salt to taste",
            "Water as needed",
        ],
        "steps": [
            "Heat oil in a pan and sauté the onions.",
            "Add ginger-garlic paste and tomatoes; cook until soft.",
            "Add chicken, chicken masala, salt and water.",
            "Cover and cook until the chicken is tender.",
            "Serve hot with rice or chapati.",
        ],
    },
    {
        "title": "Chicken Biryani",
        "category": "Chicken",
        "image": "/images/k1.jpeg",
        "cook_time": "60 mins",
        "servings": "4",
        "description": "Aromatic chicken biryani cooked with fragrant rice and spices.",
        "ingredients": [
            "500 g chicken",
            "2 cups basmati rice",
            "2 onions, sliced",
            "2 tomatoes, chopped",
            "Ginger-garlic paste",
            "Biryani masala",
            "Mint and coriander leaves",
            "Salt and oil",
        ],
        "steps": [
            "Wash and soak the rice.",
            "Sauté onions, ginger-garlic paste and tomatoes in a pot.",
            "Add chicken, biryani masala, herbs and salt.",
            "Add rice and the required water.",
            "Cover and cook until the rice and chicken are done.",
        ],
    },
    {
        "title": "Mutton Curry",
        "category": "Mutton",
        "image": "/images/k3.jpeg",
        "cook_time": "60 mins",
        "servings": "4",
        "description": "A rich and spicy mutton curry with traditional Indian spices.",
        "ingredients": [
            "500 g mutton",
            "2 onions, chopped",
            "2 tomatoes, chopped",
            "Ginger-garlic paste",
            "Mutton masala",
            "Turmeric powder",
            "Salt and oil",
            "Water as needed",
        ],
        "steps": [
            "Heat oil and sauté the onions.",
            "Add ginger-garlic paste and tomatoes.",
            "Add mutton, masala, turmeric and salt.",
            "Add water and cook until the mutton is tender.",
            "Serve hot with rice or chapati.",
        ],
    },
    {
        "title": "Mutton Biryani",
        "category": "Mutton",
        "image": "/images/k2.jpeg",
        "cook_time": "75 mins",
        "servings": "4",
        "description": "A fragrant mutton biryani prepared with basmati rice and spices.",
        "ingredients": [
            "500 g mutton",
            "2 cups basmati rice",
            "2 onions, sliced",
            "2 tomatoes, chopped",
            "Ginger-garlic paste",
            "Biryani masala",
            "Mint and coriander leaves",
            "Salt and oil",
        ],
        "steps": [
            "Wash and soak the rice.",
            "Sauté onions, ginger-garlic paste and tomatoes.",
            "Add mutton, masala, herbs and salt.",
            "Cook the mutton until tender.",
            "Add rice and water, then cook until done.",
        ],
    },
    {
        "title": "Paneer Masala",
        "category": "Vegetarian",
        "image": "/images/k4.jpeg",
        "cook_time": "30 mins",
        "servings": "3",
        "description": "Soft paneer cubes simmered in a creamy, spiced tomato gravy.",
        "ingredients": [
            "250 g paneer",
            "2 tomatoes",
            "1 onion",
            "Ginger-garlic paste",
            "Garam masala",
            "Chilli powder",
            "Oil and salt",
            "Water as needed",
        ],
        "steps": [
            "Sauté chopped onions in oil.",
            "Add ginger-garlic paste and tomatoes; cook until soft.",
            "Add the spices and a little water.",
            "Add paneer cubes and simmer for several minutes.",
            "Serve hot with chapati or rice.",
        ],
    },
    {
        "title": "Vegetable Biryani",
        "category": "Vegetarian",
        "image": "/images/k5.jpeg",
        "cook_time": "45 mins",
        "servings": "3",
        "description": "A colorful vegetable biryani cooked with rice and aromatic spices.",
        "ingredients": [
            "2 cups basmati rice",
            "2 cups mixed vegetables",
            "1 onion, sliced",
            "1 tomato, chopped",
            "Ginger-garlic paste",
            "Biryani masala",
            "Mint and coriander leaves",
            "Salt and oil",
        ],
        "steps": [
            "Wash and soak the rice.",
            "Sauté onions, ginger-garlic paste and tomatoes.",
            "Add mixed vegetables, masala, herbs and salt.",
            "Add rice and the required water.",
            "Cover and cook until the rice and vegetables are tender.",
        ],
    },
]


def make_slug(name):
    return re.sub(r"[^a-z0-9]+", "-", name.lower()).strip("-")


def main():
    db = SessionLocal()

    try:
        added = 0
        skipped = 0

        for item in RECIPES:
            existing = (
                db.query(Recipe)
                .filter(Recipe.title.ilike(item["title"]))
                .first()
            )

            if existing:
                print(f"SKIPPED (already exists): {item['title']}")
                skipped += 1
                continue

            base_slug = make_slug(item["title"])
            slug = base_slug
            counter = 2

            while db.query(Recipe).filter(Recipe.slug == slug).first():
                slug = f"{base_slug}-{counter}"
                counter += 1

            recipe = Recipe(
                title=item["title"],
                slug=slug,
                category=item["category"],
                description=item["description"],
                image=item["image"],
                cook_time=item["cook_time"],
                servings=item["servings"],
                ingredients=item["ingredients"],
                steps=item["steps"],
                is_published=True,
            )

            db.add(recipe)
            added += 1

        db.commit()

        print("\nRecipe seeding complete!")
        print(f"Added: {added}")
        print(f"Skipped existing recipes: {skipped}")
        print(f"Total recipes in database: {db.query(Recipe).count()}")

    except Exception:
        db.rollback()
        raise

    finally:
        db.close()


if __name__ == "__main__":
    main()
