from app.services.security import get_password_hash, verify_password, create_access_token, verify_token


def test_password_hash_and_verify():
    raw = "s3cr3t"
    hashed = get_password_hash(raw)
    assert hashed != raw
    assert verify_password(raw, hashed)

def test_create_and_verify_token():
    token = create_access_token({"sub": "testuser"})
    username = verify_token(token)
    assert username == "testuser"