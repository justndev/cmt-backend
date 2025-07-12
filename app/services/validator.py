from fastapi import HTTPException


def validate_string_field(name: str, value: str, min_len: int = 1, max_len: int = 255):
    if not isinstance(value, str):
        raise HTTPException(status_code=400, detail=f"Field '{name}' must be a string")
    if not (min_len <= len(value) <= max_len):
        raise HTTPException(status_code=400, detail=f"Field '{name}' must be between {min_len} and {max_len} characters")

def validate_password(password: str):
    validate_string_field("password", password, min_len=8)