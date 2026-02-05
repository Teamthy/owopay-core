import pytest
from server.app import app, db, Wallet

@pytest.fixture
def client():
    app.config['TESTING'] = True
    app.config['SQLALCHEMY_DATABASE_URI'] = "sqlite:///:memory:"  # in‑memory DB
    with app.test_client() as client:
        with app.app_context():
            db.create_all()
        yield client
        with app.app_context():
            db.drop_all()


def test_create_wallet(client):
    response = client.post("/api/v1/wallets", json={"user_id": 1, "currency": "USD"})
    assert response.status_code == 201
    data = response.get_json()
    assert data["status"] == "success"
    assert data["user_id"] == 1
    assert data["currency"] == "USD"


def test_list_wallets(client):
    # First create a wallet
    client.post("/api/v1/wallets", json={"user_id": 2, "currency": "USD"})

    response = client.get("/api/v1/wallets")
    assert response.status_code == 200
    data = response.get_json()
    assert isinstance(data, list)
    assert len(data) >= 1
    assert data[0]["currency"] == "USD"


def test_get_wallet(client):
    # Create a wallet
    post_resp = client.post("/api/v1/wallets", json={"user_id": 3, "currency": "USD"})
    wallet_id = post_resp.get_json()["wallet_id"]

    # Fetch it back
    response = client.get(f"/api/v1/wallets/{wallet_id}")
    assert response.status_code == 200
    data = response.get_json()
    assert data["wallet_id"] == wallet_id
    assert data["user_id"] == 3
