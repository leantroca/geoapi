def clean_nones(kwargs: dict) -> dict:
    return {key: value for key, value in kwargs.items() if value not in [None, {}]}
