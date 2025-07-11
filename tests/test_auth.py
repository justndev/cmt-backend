def test_register_user(client):
    response = client.post("/api/auth/register", json={
        "username": "testuser1",
        "password": "testpass123"
    })
    assert response.status_code == 200
    data = response.json()
    assert data["username"] == "testuser1"
    assert "id" in data
    assert data["is_active"] is True


def test_register_existing_user(client):
    response = client.post("/api/auth/register", json={
        "username": "testuser1",  # same as before
        "password": "anotherpass"
    })
    assert response.status_code == 400
    assert response.json()["detail"] == "Username already registered"

def test_login_user(client):
    response = client.post("/api/auth/login", json={
        "username": "testuser1",
        "password": "testpass123"
    })
    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data
    assert data["token_type"] == "bearer"

def test_login_wrong_password(client):
    response = client.post("/api/auth/login", json={
        "username": "testuser1",
        "password": "wrongpass"
    })
    assert response.status_code == 401
    assert response.json()["detail"] == "Incorrect username or password"

