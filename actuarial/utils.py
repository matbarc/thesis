def generic_class_repr(inst: object, *, exclude: list[str] = []) -> str:
    attrstrings = [
        f"{key}: " + (f"{inst.__dict__[key]}" if key not in exclude else "...")
        for key in inst.__dict__
        if not key.startswith("_")
    ]
    return f"<{inst.__class__.__name__} | {' | '.join(attrstrings)}>"
