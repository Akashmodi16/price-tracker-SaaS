def clean_price(price_str: str) -> float:
    try:
        if not price_str:
            return 0.0

        # Remove currency symbols
        cleaned = price_str.replace("₹", "").replace("$", "")

        # Remove commas
        cleaned = cleaned.replace(",", "")

        # Remove whitespace + newlines
        cleaned = cleaned.replace("\n", "").strip()

        # Remove unwanted characters except digits and dot
        cleaned = "".join(c for c in cleaned if c.isdigit() or c == ".")

        # Fix multiple dots issue (rare cases)
        if cleaned.count(".") > 1:
            parts = cleaned.split(".")
            cleaned = parts[0] + "." + "".join(parts[1:])

        return float(cleaned)

    except Exception as e:
        print("Price cleaning error:", e)
        return 0.0