from datetime import datetime, timezone


def _create_driver(client):
    return client.post(
        "/api/v1/drivers",
        json={"name": "Location Test Driver", "phone": "780-555-0300"},
    ).json()


def test_record_location(client):
    driver = _create_driver(client)

    response = client.post(
        "/api/v1/locations",
        json={
            "driver_id": driver["id"],
            "latitude": 53.5461,
            "longitude": -113.4938,
            "recorded_at": datetime.now(timezone.utc).isoformat(),
        },
    )
    assert response.status_code == 201
    data = response.json()
    assert data["driver_id"] == driver["id"]
    assert data["latitude"] == 53.5461
    assert data["longitude"] == -113.4938


def test_record_location_driver_not_found(client):
    response = client.post(
        "/api/v1/locations",
        json={
            "driver_id": "00000000-0000-0000-0000-000000000000",
            "latitude": 53.5461,
            "longitude": -113.4938,
            "recorded_at": datetime.now(timezone.utc).isoformat(),
        },
    )
    assert response.status_code == 404


def test_record_location_invalid_latitude(client):
    driver = _create_driver(client)
    response = client.post(
        "/api/v1/locations",
        json={
            "driver_id": driver["id"],
            "latitude": 999.0,          # invalid
            "longitude": -113.4938,
            "recorded_at": datetime.now(timezone.utc).isoformat(),
        },
    )
    assert response.status_code == 422


def test_get_latest_location(client):
    driver = _create_driver(client)
    client.post(
        "/api/v1/locations",
        json={
            "driver_id": driver["id"],
            "latitude": 53.5461,
            "longitude": -113.4938,
            "recorded_at": datetime.now(timezone.utc).isoformat(),
        },
    )

    response = client.get(f"/api/v1/locations/{driver['id']}/latest")
    assert response.status_code == 200
    assert response.json()["latitude"] == 53.5461


def test_get_latest_location_none(client):
    driver = _create_driver(client)
    response = client.get(f"/api/v1/locations/{driver['id']}/latest")
    assert response.status_code == 404


def test_location_history(client):
    driver = _create_driver(client)
    for i in range(3):
        client.post(
            "/api/v1/locations",
            json={
                "driver_id": driver["id"],
                "latitude": 53.5 + i * 0.01,
                "longitude": -113.5,
                "recorded_at": datetime.now(timezone.utc).isoformat(),
            },
        )

    response = client.get(f"/api/v1/locations/{driver['id']}/history")
    assert response.status_code == 200
    assert len(response.json()) == 3


def test_find_nearby(client):
    driver = _create_driver(client)
    client.post(
        "/api/v1/locations",
        json={
            "driver_id": driver["id"],
            "latitude": 53.5461,
            "longitude": -113.4938,
            "recorded_at": datetime.now(timezone.utc).isoformat(),
        },
    )

    response = client.get(
        "/api/v1/locations/nearby",
        params={"latitude": 53.5461, "longitude": -113.4938, "radius_km": 5},
    )
    assert response.status_code == 200
    results = response.json()
    assert len(results) >= 1
    assert any(r["driver_id"] == driver["id"] for r in results)


def test_find_nearby_outside_radius(client):
    driver = _create_driver(client)
    # Edmonton
    client.post(
        "/api/v1/locations",
        json={
            "driver_id": driver["id"],
            "latitude": 53.5461,
            "longitude": -113.4938,
            "recorded_at": datetime.now(timezone.utc).isoformat(),
        },
    )

    # Query from Calgary (~280km away) with a 5km radius
    response = client.get(
        "/api/v1/locations/nearby",
        params={"latitude": 51.0447, "longitude": -114.0719, "radius_km": 5},
    )
    assert response.status_code == 200
    assert response.json() == []