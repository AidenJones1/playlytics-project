def _is_missing(value):
    if value is None:
        return True
    if isinstance(value, str) and not value.strip():
        return True
    try:
        return value != value
    except Exception:
        return False

def to_nullable_int(value):
    """Convert a value to an integer, returning None if the value is missing or invalid."""
    if _is_missing(value):
        return None
    try:
        return int(value)
    except (TypeError, ValueError):
        return None

def safe_div(numerator, denominator):
    return numerator / denominator if denominator > 0 else 0