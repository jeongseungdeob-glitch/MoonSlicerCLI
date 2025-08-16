PROHIBITED_TOKENS = [
    "os.",
    "io.",
    "require(",
    "dofile(",
    "loadfile(",
    "package.",
]


class ValidationError(Exception):
    pass


def validate(code: str):
    """Raise ValidationError if code contains disallowed patterns."""
    lowered = code.lower()
    for token in PROHIBITED_TOKENS:
        if token.lower() in lowered:
            raise ValidationError(f"Prohibited token detected: {token}")
    # TODO: add loop detection/static analysis
    return True