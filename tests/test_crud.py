def test_create_provider(client):
    response = client.post("/api/cmt/providers", json={
        "name": "My Ads"
    })
    assert response.status_code == 200
    data = response.json()
    assert data["name"] == "My Ads"

def test_create_placement(client):
    response = client.post("/api/cmt/placements", json={
        "country": "Germany",
        "imp_price_in_eur": 150,
        "provider_id": 1
    })
    assert response.status_code == 200
    data = response.json()
    assert data["country"] == "Germany"
    assert data["imp_price_in_eur"] == 150


def test_create_campaign(client):
    placement_response = client.get("/api/cmt/placements")
    assert placement_response.status_code == 200
    placements = placement_response.json()
    assert placements

    placement_ids = [placements[0]["id"]]

    login_response = client.post("/api/auth/login", json={
        "username": "testuser1",
        "password": "testpass123"
    })
    token = login_response.json()["access_token"]

    response = client.post("/api/cmt/campaigns", json={
        "title": "Test Campaign",
        "url": "http://example.com",
        "placement_ids": placement_ids
    }, headers={
        'Authorization': f'Bearer {token}'
    })
    assert response.status_code == 200
    data = response.json()
    assert data["title"] == "Test Campaign"
    assert data["url"] == "http://example.com"
    assert len(data["placements"]) > 0


def test_filter_campaigns(client):
    login_response = client.post("/api/auth/login", json={
        "username": "testuser1",
        "password": "testpass123"
    })
    token = login_response.json()["access_token"]

    response = client.get("/api/cmt/campaigns/filter?search=Test", headers={
        'Authorization': f'Bearer {token}'
    })

    assert response.status_code == 200
    campaigns = response.json()
    assert isinstance(campaigns, list)


def test_toggle_campaign_status(client):
    login_response = client.post("/api/auth/login", json={
        "username": "testuser1",
        "password": "testpass123"
    })
    token = login_response.json()["access_token"]

    campaigns = client.get("/api/cmt/campaigns", headers={
        'Authorization': f'Bearer {token}'
    }).json()
    assert campaigns
    campaign_id = campaigns[0]["id"]

    response = client.patch(f"/api/cmt/campaigns/{campaign_id}/status", json={"is_active": False}, headers={
        'Authorization': f'Bearer {token}'
    })
    assert response.status_code == 200
    assert not response.json()["is_active"]


def test_delete_campaign(client):
    login_response = client.post("/api/auth/login", json={
        "username": "testuser1",
        "password": "testpass123"
    })
    token = login_response.json()["access_token"]

    campaigns = client.get("/api/cmt/campaigns", headers={
        'Authorization': f'Bearer {token}'
    }).json()
    assert campaigns
    campaign_id = campaigns[0]["id"]

    response = client.delete("/api/cmt/campaigns", params={"campaign_id": campaign_id}, headers={
        'Authorization': f'Bearer {token}'
    })
    assert response.status_code == 200
    assert response.json()["is_archived"] is True