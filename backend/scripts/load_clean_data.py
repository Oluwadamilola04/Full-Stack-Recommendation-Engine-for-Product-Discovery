from __future__ import annotations

from pathlib import Path
import random
import re
from datetime import datetime, timedelta, timezone


def _repo_root() -> Path:
    return Path(__file__).resolve().parents[2]


def _backend_dir() -> Path:
    return Path(__file__).resolve().parents[1]


def _split_csv_tokens(value: str | None) -> list[str]:
    if not value or not isinstance(value, str):
        return []
    tokens = [t.strip() for t in value.split(",")]
    tokens = [t for t in tokens if t]
    seen: set[str] = set()
    out: list[str] = []
    for token in tokens:
        if token not in seen:
            out.append(token)
            seen.add(token)
    return out


def _parse_image_urls(value: str | None) -> list[str]:
    if not value or not isinstance(value, str):
        return []
    parts = [p.strip() for p in value.split("|")]
    return [p for p in parts if p]


def _estimate_price_ngn(
    *,
    name: str,
    brand: str | None,
    category: str,
    category_raw: str | None,
    tags: list[str],
) -> float:
    text = " ".join(
        [
            name.lower(),
            (brand or "").lower(),
            category.lower(),
            (category_raw or "").lower(),
            " ".join(tag.lower() for tag in tags),
        ]
    )

    usd_price = 12.0

    category_bases = {
        "beauty": 9.5,
        "personal": 8.0,
        "health": 11.0,
        "household": 10.0,
        "home": 18.0,
        "food": 7.0,
        "sports": 24.0,
        "clothing": 20.0,
        "baby": 13.0,
        "electronics": 45.0,
        "auto": 16.0,
        "pets": 12.0,
        "industrial": 28.0,
    }
    usd_price = category_bases.get(category.lower(), usd_price)

    keyword_bases = [
        ("razor blade refill", 14.0),
        ("protein shake", 18.0),
        ("diffuser", 24.0),
        ("humidifier", 26.0),
        ("shampoo and conditioner", 14.0),
        ("conditioner", 8.0),
        ("shampoo", 8.0),
        ("hair color", 9.0),
        ("lip balm", 4.0),
        ("lipstick", 6.0),
        ("lip lacquer", 6.5),
        ("toothpaste", 5.0),
        ("toothbrush", 4.5),
        ("mousse", 7.5),
        ("styling gel", 8.0),
        ("molding clay", 9.0),
        ("nail lacquer", 7.0),
        ("nail polish", 6.5),
        ("blush", 7.0),
        ("razor", 9.0),
        ("protein", 15.0),
        ("vitamin", 12.0),
        ("supplement", 14.0),
        ("detergent", 11.0),
        ("cleaner", 9.0),
        ("diaper", 18.0),
        ("baby", 10.0),
        ("headphone", 35.0),
        ("charger", 15.0),
        ("case", 12.0),
    ]
    for keyword, base in keyword_bases:
        if keyword in text:
            usd_price = max(usd_price, base)

    premium_brands = {
        "opi": 1.35,
        "loreal": 1.15,
        "pantene": 1.15,
        "gillette": 1.2,
        "colgate": 1.05,
        "old spice": 1.12,
        "vaseline": 1.05,
        "clairol": 1.12,
        "crest": 1.08,
        "orly": 1.2,
        "kokie": 1.1,
        "art of shaving": 1.35,
        "vega": 1.25,
    }
    for premium_brand, multiplier in premium_brands.items():
        if premium_brand in text:
            usd_price *= multiplier
            break

    pack_match = re.search(r"pack of (\d+)", text)
    if not pack_match:
        pack_match = re.search(r"\((\d+)\s*pack\)", text)
    if not pack_match:
        pack_match = re.search(r"\b(\d+)\s*ct\b", text)
    if pack_match:
        pack_count = max(1, min(int(pack_match.group(1)), 12))
        usd_price *= 1 + ((pack_count - 1) * 0.35)

    ounce_match = re.search(r"(\d+(?:\.\d+)?)\s*(?:fl\s*)?oz\b", text)
    if ounce_match:
        ounce_value = float(ounce_match.group(1))
        if ounce_value >= 10:
            usd_price *= 1.25
        elif ounce_value <= 1:
            usd_price *= 0.82

    if "premium" in text:
        usd_price *= 1.18

    usd_price = max(3.5, min(usd_price, 85.0))
    ngn_price = usd_price * 1650.0
    rounded = round(ngn_price / 50.0) * 50.0
    return float(rounded)


def main() -> int:
    import sys

    # Ensure `import app.*` works when running from repo root.
    sys.path.insert(0, str(_backend_dir()))

    import pandas as pd

    from app.core.database import Base, SessionLocal, engine
    from app.models.interaction import UserProductInteraction
    from app.models.product import Product
    from app.models.user import User

    csv_path = _repo_root() / "clean_data.csv"
    if not csv_path.exists():
        print(f"ERROR: {csv_path} not found")
        return 1

    print(f"Loading dataset: {csv_path} ({csv_path.stat().st_size} bytes)")
    df = pd.read_csv(
        csv_path,
        dtype={
            # Read as strings first to avoid integer overflow in pandas dtypes.
            "ID": "string",
            "ProdID": "string",
        },
    )

    # Drop the index column created by some CSV exports.
    for col in list(df.columns):
        if str(col).startswith("Unnamed"):
            df = df.drop(columns=[col])

    required = {
        "ID",
        "ProdID",
        "Rating",
        "ReviewCount",
        "Category",
        "Brand",
        "Name",
        "ImageURL",
        "Description",
        "Tags",
    }
    missing = required - set(df.columns)
    if missing:
        print(f"ERROR: Missing required columns: {sorted(missing)}")
        return 1

    # Deduplicate to one row per ProdID (keep the most-reviewed row).
    df["ReviewCount"] = pd.to_numeric(df["ReviewCount"], errors="coerce").fillna(0)
    df = df.sort_values("ReviewCount", ascending=False)
    df = df.drop_duplicates(subset=["ProdID"], keep="first")

    print(f"Rows after dedupe: {len(df)}")

    # Reset schema for SQLite dev DB.
    print("Resetting tables...")
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)

    products: list[Product] = []
    for row in df.itertuples(index=False):
        category_raw = getattr(row, "Category", None)
        category_tokens = _split_csv_tokens(category_raw)
        category = category_tokens[0] if category_tokens else "unknown"

        tags = _split_csv_tokens(getattr(row, "Tags", None))

        source_id_raw = getattr(row, "ID")
        prod_id_raw = getattr(row, "ProdID")

        source_id = int(str(source_id_raw)) if source_id_raw is not None else None
        prod_id = int(str(prod_id_raw)) if prod_id_raw is not None else None

        products.append(
            Product(
                source_id=source_id,
                prod_id=prod_id,
                name=str(getattr(row, "Name")),
                brand=(str(getattr(row, "Brand")) if getattr(row, "Brand") is not None else None),
                description=(str(getattr(row, "Description")) if getattr(row, "Description") is not None else None),
                category=category,
                category_raw=(str(category_raw) if category_raw is not None else None),
                price=_estimate_price_ngn(
                    name=str(getattr(row, "Name")),
                    brand=(str(getattr(row, "Brand")) if getattr(row, "Brand") is not None else None),
                    category=category,
                    category_raw=(str(category_raw) if category_raw is not None else None),
                    tags=tags,
                ),
                tags=tags or None,
                average_rating=float(getattr(row, "Rating") or 0.0),
                review_count=int(float(getattr(row, "ReviewCount") or 0)),
                image_urls=_parse_image_urls(getattr(row, "ImageURL", None)) or None,
            )
        )

    print(f"Inserting products: {len(products)}")
    db = SessionLocal()
    try:
        db.bulk_save_objects(products)
        db.commit()

        inserted_products = db.query(Product).order_by(Product.review_count.desc(), Product.id.asc()).all()
        by_category: dict[str, list[Product]] = {}
        for product in inserted_products:
            by_category.setdefault(product.category or "unknown", []).append(product)

        user_specs = [
            {
                "username": "ada_beauty",
                "email": "ada@example.com",
                "first_name": "Ada",
                "last_name": "Okafor",
                "preferences": ["beauty", "premium"],
            },
            {
                "username": "musa_health",
                "email": "musa@example.com",
                "first_name": "Musa",
                "last_name": "Ibrahim",
                "preferences": ["health", "personal"],
            },
            {
                "username": "chioma_glam",
                "email": "chioma@example.com",
                "first_name": "Chioma",
                "last_name": "Adeleke",
                "preferences": ["beauty", "personal"],
            },
            {
                "username": "tunde_style",
                "email": "tunde@example.com",
                "first_name": "Tunde",
                "last_name": "Balogun",
                "preferences": ["premium", "beauty"],
            },
            {
                "username": "zainab_wellness",
                "email": "zainab@example.com",
                "first_name": "Zainab",
                "last_name": "Sani",
                "preferences": ["health", "beauty"],
            },
            {
                "username": "ifeanyi_essentials",
                "email": "ifeanyi@example.com",
                "first_name": "Ifeanyi",
                "last_name": "Nwosu",
                "preferences": ["personal", "health"],
            },
        ]

        users = [
            User(
                username=spec["username"],
                email=spec["email"],
                hashed_password="seeded-password",
                first_name=spec["first_name"],
                last_name=spec["last_name"],
                is_active=True,
            )
            for spec in user_specs
        ]
        db.add_all(users)
        db.commit()

        db_users = db.query(User).order_by(User.id.asc()).all()
        rng = random.Random(42)
        interactions: list[UserProductInteraction] = []
        now = datetime.now(timezone.utc)
        interaction_weights = {
            "view": 1.0,
            "click": 2.0,
            "add_to_cart": 3.0,
            "purchase": 5.0,
        }

        def choose_products(categories: list[str], count: int) -> list[Product]:
            pool: list[Product] = []
            for category in categories:
                pool.extend(by_category.get(category, [])[:25])
            seen: set[int] = set()
            unique_pool: list[Product] = []
            for product in pool:
                if product.id not in seen:
                    unique_pool.append(product)
                    seen.add(product.id)
            rng.shuffle(unique_pool)
            return unique_pool[:count]

        for user, spec in zip(db_users, user_specs):
            favorites = choose_products(spec["preferences"], 10)
            exploratory_categories = [category for category in by_category if category not in spec["preferences"]]
            exploratory = choose_products(exploratory_categories[:2], 3)
            ordered_products = favorites + exploratory

            for index, product in enumerate(ordered_products):
                timestamp = now - timedelta(days=rng.randint(0, 12), hours=index)

                interactions.append(
                    UserProductInteraction(
                        user_id=user.id,
                        product_id=product.id,
                        interaction_type="view",
                        interaction_weight=interaction_weights["view"],
                        timestamp=timestamp,
                    )
                )

                if index < 8:
                    interactions.append(
                        UserProductInteraction(
                            user_id=user.id,
                            product_id=product.id,
                            interaction_type="click",
                            interaction_weight=interaction_weights["click"],
                            timestamp=timestamp + timedelta(minutes=5),
                        )
                    )

                if index < 5:
                    interactions.append(
                        UserProductInteraction(
                            user_id=user.id,
                            product_id=product.id,
                            interaction_type="add_to_cart",
                            interaction_weight=interaction_weights["add_to_cart"],
                            timestamp=timestamp + timedelta(minutes=12),
                        )
                    )

                if index < 3:
                    rating = float(product.average_rating or 4.0)
                    interactions.append(
                        UserProductInteraction(
                            user_id=user.id,
                            product_id=product.id,
                            interaction_type="purchase",
                            interaction_weight=interaction_weights["purchase"],
                            rating=max(3.5, min(5.0, rating)),
                            timestamp=timestamp + timedelta(minutes=25),
                        )
                    )

        print(f"Inserting users: {len(users)}")
        print(f"Inserting interactions: {len(interactions)}")
        db.bulk_save_objects(interactions)
        db.commit()
    finally:
        db.close()

    print("Done.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
