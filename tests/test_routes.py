import pytest
from app.app import create_app
from app import db


@pytest.fixture(autouse=True)
def reset_db():
    """Reset in-memory store before every test."""
    db._users.clear()
    db._next_id = 1
    yield
    db._users.clear()
    db._next_id = 1


@pytest.fixture
def client():
    app = create_app()
    app.config["TESTING"] = True
    app.config["PROPAGATE_EXCEPTIONS"] = False
    with app.test_client() as c:
        yield c


def _create(client, name="Alice", email="alice@example.com", password="secret", **kwargs):
    return client.post("/api/users", json={"name": name, "email": email, "password": password, **kwargs})


# ---------------------------------------------------------------------------
# Happy path
# ---------------------------------------------------------------------------

def test_list_empty(client):
    r = client.get("/api/users")
    assert r.status_code == 200
    assert r.get_json() == []


def test_create_returns_201(client):
    r = _create(client)
    assert r.status_code == 201
    body = r.get_json()
    assert body["id"] == 1
    assert body["name"] == "Alice"
    assert body["email"] == "alice@example.com"
    assert body["role"] == "user"


def test_create_with_custom_role(client):
    r = _create(client, role="admin")
    assert r.get_json()["role"] == "admin"


def test_list_returns_all_created_users(client):
    _create(client, name="Alice", email="a@x.com")
    _create(client, name="Bob", email="b@x.com")
    r = client.get("/api/users")
    assert r.status_code == 200
    assert len(r.get_json()) == 2


def test_update_existing_user(client):
    _create(client)
    r = client.put("/api/users/1", json={"role": "admin"})
    assert r.status_code == 200
    assert r.get_json()["role"] == "admin"


def test_update_returns_404_for_missing_user(client):
    r = client.put("/api/users/99", json={"role": "admin"})
    assert r.status_code == 404


def test_delete_removes_user(client):
    _create(client)
    client.delete("/api/users/1")
    assert client.get("/api/users").get_json() == []


# ---------------------------------------------------------------------------
# Bug documentation — these tests assert the *current* (buggy) behaviour.
# When a bug is fixed, update the assertion to the correct expectation.
# ---------------------------------------------------------------------------

def test_get_user_by_id(client):
    _create(client, name="Alice", email="a@x.com")
    _create(client, name="Bob", email="b@x.com")

    r = client.get("/api/users/1")
    assert r.status_code == 200
    body = r.get_json()
    assert isinstance(body, dict)
    assert body["id"] == 1
    assert body["name"] == "Alice"


def test_get_user_by_id_not_found(client):
    r = client.get("/api/users/99")
    assert r.status_code == 404


def test_bug_create_missing_field_returns_500(client):
    """BUG: missing required field causes unhandled KeyError → 500 instead of 400."""
    r = client.post("/api/users", json={"name": "Alice"})  # no email / password
    assert r.status_code == 500   # should be 400 when fixed


def test_bug_delete_nonexistent_user_returns_200(client):
    """BUG: DELETE on a non-existent id returns 200 instead of 404."""
    r = client.delete("/api/users/999")
    assert r.status_code == 200   # should be 404 when fixed


def test_password_not_exposed_in_response(client):
    r = _create(client, password="s3cr3t")
    body = r.get_json()
    assert "password" not in body
    assert "password_hash" not in body
