import re


_RULES: list[tuple[str, re.Pattern[str]]] = [
    ("Fuel", re.compile(r"\b(fuel|petrol|diesel|gas\s*station)\b", re.I)),
    ("Rent", re.compile(r"\b(rent|landlord|lease)\b", re.I)),
    ("Groceries", re.compile(r"\b(grocery|supermarket|market|walmart|costco|aldi)\b", re.I)),
    ("Restaurant", re.compile(r"\b(restaurant|cafe|coffee|pizza|burger|dinner|lunch)\b", re.I)),
    ("EMI", re.compile(r"\b(emi|installment|loan\s*payment|mortgage)\b", re.I)),
    ("Transport", re.compile(r"\b(uber|lyft|taxi|bus|metro|train|transport)\b", re.I)),
    ("Phone", re.compile(r"\b(phone|mobile|recharge|top\s*up|airtime)\b", re.I)),
]


def apply_rules(description: str) -> tuple[str, float, str, str] | None:
    desc = (description or "").strip()
    if not desc:
        return None

    for label, pattern in _RULES:
        if pattern.search(desc):
            return (label, 0.95, "rules", f"Matched rule: {label}")

    return None
