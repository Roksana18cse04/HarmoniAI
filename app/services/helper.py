def safe_float(val):
    try:
        return float(val)
    except (TypeError, ValueError):
        return None