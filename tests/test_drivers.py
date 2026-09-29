def test_create_driver(client):
    response = client.post(
        "/api/v1/drivers",
        json={"name": "Test Driver", "phone": "780-555-0100"},
    )
    assert response.status_code == 201
    data = response.json()
    assert data["name"] == "Test Driver"
    assert data["phone"] == "780-555-0100"
    assert "id" in data
    assert "created_at" in data


def test_create_driver_without_phone(client):
    response = client.post(
        "/api/v1/drivers",
        json={"name": "No Phone Driver"},
    )
    assert response.status_code == 201
    assert response.json()["phone"] is None


def test_create_driver_missing_name(client):
    response = client.post(
        "/api/v1/drivers",
        json={"phone": "780-555-0100"},
    )
    assert response.status_code == 422


def test_get_driver(client):
    created = client.post(
        "/api/v1/drivers",
        json={"name": "Find Me", "phone": "780-555-0200"},
    ).json()

    response = client.get(f"/api/v1/drivers/{created['id']}")
    assert response.status_code == 200
    assert response.json()["name"] == "Find Me"


def test_get_driver_not_found(client):
    response = client.get("/api/v1/drivers/00000000-0000-0000-0000-000000000000")
    assert response.status_code == 404


def test_list_drivers(client):
    client.post("/api/v1/drivers", json={"name": "Driver A"})
    client.post("/api/v1/drivers", json={"name": "Driver B"})

    response = client.get("/api/v1/drivers")
    assert response.status_code == 200
    assert len(response.json()) == 2