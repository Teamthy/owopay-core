import pytest
from server.app import app, db, Wallet, Transaction

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


def test_create_transaction(client):
    # First create a wallet to attach the transaction
    wallet_resp = client.post("/api/v1/wallets", json={"user_id": 1, "currency": "USD"})
    wallet_id = wallet_resp.get_json()["wallet_id"]

    # Create a transaction
    tx_resp = client.post("/api/v1/transactions", json={
        "wallet_id": wallet_id,
        "amount": 100,
        "type": "credit",
        "currency": "USD"
    })
    assert tx_resp.status_code == 201
    data = tx_resp.get_json()
    assert data["status"] == "success"
    assert data["wallet_id"] == wallet_id
    assert data["amount"] == "100"
    assert data["type"] == "credit"


def test_list_transactions(client):
    # Create wallet + transaction
    wallet_resp = client.post("/api/v1/wallets", json={"user_id": 2, "currency": "USD"})
    wallet_id = wallet_resp.get_json()["wallet_id"]
    client.post("/api/v1/transactions", json={"wallet_id": wallet_id, "amount": 50, "type": "debit", "currency": "USD"})

    # List transactions
    resp = client.get("/api/v1/transactions")
    assert resp.status_code == 200
    data = resp.get_json()
    assert isinstance(data, list)
    assert len(data) >= 1
    assert data[0]["currency"] == "USD"


def test_get_transaction(client):
    # Create wallet + transaction
    wallet_resp = client.post("/api/v1/wallets", json={"user_id": 3, "currency": "USD"})
    wallet_id = wallet_resp.get_json()["wallet_id"]
    tx_resp = client.post("/api/v1/transactions", json={"wallet_id": wallet_id, "amount": 75, "type": "credit", "currency": "USD"})
    tx_id = tx_resp.get_json()["transaction_id"]

    # Fetch transaction by ID
    resp = client.get(f"/api/v1/transactions/{tx_id}")
    assert resp.status_code == 200
    data = resp.get_json()
    assert data["transaction_id"] == tx_id
    assert data["wallet_id"] == wallet_id
    assert data["amount"] == "75"
