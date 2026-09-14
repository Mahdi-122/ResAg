def is_valid_source(text: str) -> bool:
    if len(text) < 200:
        return False

    lowered = text.lower()

    blocked_indicators = [
        "access restricted",
        "we've detected unusual activity",
        "you don't have permission to access",
        "temporarily restricted",
    ]

    matches = sum(
        phrase in lowered
        for phrase in blocked_indicators
    )

    if matches >= 2 and len(text) < 2000:
        return False

    return True