"""Equivalence contracts for `after/` — the same 13 HTTP tests from `before/`
plus 1 new test that describes the graceful cancel-all behavior.

These tests exist in two places (before/ and after/) on purpose: they are
the formal proof that the SOLID refactoring did NOT change observable
behavior. The only test that CHANGES between before/ and after/ is the
LSP-trap one: before/ asserts 5xx; after/ asserts the partial-result
payload.
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


def test_create_traveler_rejects_invalid_document(client: TestClient):
    response = client.post(
        "/travelers",
        json={
            "name": "Maria Silva",
            "email": "maria@example.com",
            "document": "123",
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


# ---------- Packages ----------


def _create_traveler(client: TestClient, email: str = "default@example.com") -> int:
    r = client.post(
        "/travelers",
        json={"name": "Default", "email": email, "document": "12345678909"},
    )
    assert r.status_code == 201
    return r.json()["id"]


def test_create_package_returns_persisted(client: TestClient):
    traveler_id = _create_traveler(client)
    response = client.post(
        "/packages",
        json={
            "name": "Cancún 7 noites",
            "destination": "Cancún",
            "base_price": 5500.00,
            "kind": "standard",
            "traveler_id": traveler_id,
        },
    )
    assert response.status_code == 201
    data = response.json()
    assert data["id"] > 0
    assert data["name"] == "Cancún 7 noites"
    assert data["base_price"] == 5500.00
    assert data["status"] == "active"
    assert data["kind"] == "standard"


def test_list_packages_returns_created_items(client: TestClient):
    traveler_id = _create_traveler(client)
    for i in range(3):
        client.post(
            "/packages",
            json={
                "name": f"pkg-{i}",
                "destination": "X",
                "base_price": 1000.0,
                "kind": "standard",
                "traveler_id": traveler_id,
            },
        )

    response = client.get("/packages")

    assert response.status_code == 200
    names = {p["name"] for p in response.json()}
    assert {"pkg-0", "pkg-1", "pkg-2"} <= names


# ---------- Price calculation ----------


def _create_package(client: TestClient, base_price: float) -> int:
    traveler_id = _create_traveler(client)
    r = client.post(
        "/packages",
        json={
            "name": "pkg",
            "destination": "X",
            "base_price": base_price,
            "kind": "standard",
            "traveler_id": traveler_id,
        },
    )
    assert r.status_code == 201
    return r.json()["id"]


def test_price_without_discount_equals_base(client: TestClient):
    pkg_id = _create_package(client, 1000.0)
    response = client.post(
        f"/packages/{pkg_id}/price", json={"discount_type": "none"}
    )
    assert response.status_code == 200
    data = response.json()
    assert data["base_price"] == 1000.0
    assert data["final_price"] == 1000.0


def test_price_with_seasonal_discount_is_15_percent_off(client: TestClient):
    pkg_id = _create_package(client, 1000.0)
    response = client.post(
        f"/packages/{pkg_id}/price", json={"discount_type": "seasonal"}
    )
    assert response.status_code == 200
    assert response.json()["final_price"] == 850.0


def test_price_with_black_friday_is_30_percent_off(client: TestClient):
    pkg_id = _create_package(client, 1000.0)
    response = client.post(
        f"/packages/{pkg_id}/price", json={"discount_type": "black_friday"}
    )
    assert response.status_code == 200
    assert response.json()["final_price"] == 700.0


def test_price_with_corporate_subtracts_200(client: TestClient):
    pkg_id = _create_package(client, 1000.0)
    response = client.post(
        f"/packages/{pkg_id}/price", json={"discount_type": "corporate"}
    )
    assert response.status_code == 200
    assert response.json()["final_price"] == 800.0


def test_price_with_cyber_monday_for_high_price_applies_25_percent(client: TestClient):
    pkg_id = _create_package(client, 6000.0)
    response = client.post(
        f"/packages/{pkg_id}/price", json={"discount_type": "cyber_monday"}
    )
    assert response.status_code == 200
    assert response.json()["final_price"] == 4500.0


def test_price_with_cyber_monday_for_low_price_applies_10_percent(client: TestClient):
    pkg_id = _create_package(client, 2000.0)
    response = client.post(
        f"/packages/{pkg_id}/price", json={"discount_type": "cyber_monday"}
    )
    assert response.status_code == 200
    assert response.json()["final_price"] == 1800.0


# ---------- Cancel-all (LSP cure) ----------


def test_cancel_all_cancels_standard_packages(client: TestClient):
    traveler_id = _create_traveler(client, email="owner@example.com")
    for i in range(3):
        client.post(
            "/packages",
            json={
                "name": f"std-{i}",
                "destination": "X",
                "base_price": 100.0,
                "kind": "standard",
                "traveler_id": traveler_id,
            },
        )

    response = client.delete(f"/travelers/{traveler_id}/packages")

    assert response.status_code == 200
    data = response.json()
    assert data["cancelled"] == 3
    assert data["skipped_ids"] == []


def test_cancel_all_skips_non_refundable_and_reports_partial_result(client: TestClient):
    """LSP cure contract — after/ ONLY.

    Replaces `test_cancel_all_fails_when_any_package_is_non_refundable` from
    `before/`. The 500 is gone; we get a 200 with structured cancelled/skipped
    info. That is the whole point of the LSP refactor.
    """
    traveler_id = _create_traveler(client, email="mix@example.com")
    client.post(
        "/packages",
        json={
            "name": "std-1",
            "destination": "X",
            "base_price": 100.0,
            "kind": "standard",
            "traveler_id": traveler_id,
        },
    )
    client.post(
        "/packages",
        json={
            "name": "non-refundable-1",
            "destination": "X",
            "base_price": 100.0,
            "kind": "non_refundable",
            "traveler_id": traveler_id,
        },
    )

    response = client.delete(f"/travelers/{traveler_id}/packages")

    assert response.status_code == 200
    data = response.json()
    assert data["cancelled"] == 1
    assert len(data["skipped_ids"]) == 1
