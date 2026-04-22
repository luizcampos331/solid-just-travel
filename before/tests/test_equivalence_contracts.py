"""Equivalence contracts — behavior observable through the HTTP API.

These tests describe WHAT the system does, never HOW. They must pass identically
in `before/` (with its SOLID violations) and `after/` (after refactoring).
"""

from fastapi.testclient import TestClient


# ---------- Travelers ----------


def test_create_traveler_returns_201_and_persisted_shape(client: TestClient):
    response = client.post(
        "/travelers",
        json={
            "name": "Maria Silva",
            "email": "maria@example.com",
            "document": "12345678909",
        },
    )

    assert response.status_code == 201
    data = response.json()
    assert data["id"] > 0
    assert data["name"] == "Maria Silva"
    assert data["email"] == "maria@example.com"
    assert data["document"] == "12345678909"


def test_create_traveler_rejects_invalid_document(client_swallow_500: TestClient):
    response = client_swallow_500.post(
        "/travelers",
        json={
            "name": "Maria Silva",
            "email": "maria@example.com",
            "document": "123",  # too short
        },
    )

    assert response.status_code >= 400


def test_list_travelers_returns_created_items(client: TestClient):
    client.post(
        "/travelers",
        json={"name": "Ana", "email": "a@x.com", "document": "12345678901"},
    )
    client.post(
        "/travelers",
        json={"name": "Bob", "email": "b@x.com", "document": "12345678902"},
    )

    response = client.get("/travelers")

    assert response.status_code == 200
    data = response.json()
    names = {t["name"] for t in data}
    assert {"Ana", "Bob"} <= names


def test_get_traveler_returns_404_when_missing(client: TestClient):
    response = client.get("/travelers/9999")

    assert response.status_code == 404
