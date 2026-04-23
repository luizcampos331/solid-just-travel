# before/app/services/package_service.py — OCP violation
def calculate_price(package, discount_type: str) -> float:
    price = package.base_price
    if discount_type == "seasonal":
        price *= 0.85
    elif discount_type == "black_friday":
        price *= 0.70
    elif discount_type == "corporate":
        price = max(0.0, price - 200.0)
    elif discount_type == "cyber_monday":
        # Added last week; now four branches and counting.
        price *= 0.75 if package.base_price > 5000 else 0.90
    elif discount_type == "none":
        price = price
    else:
        raise ValueError(f"unknown discount_type: {discount_type}")
    return round(price, 2)
