import pytest
from server.app import db, Wallet, Transaction, app

@pytest.fixture
def test_client():
    app.config['TESTING'] = True
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
    with app.test_client() as client:
        with app.app_context():
            db.create_all()
        yield client
        with app.app_context():
            db.drop_all()

def test_transaction_insert(test_client):
    with app.app_context():
        wallet = Wallet(user_id=1, balance=0.0, currency="USD")
        db.session.add(wallet)
        db.session.commit()

        tx = Transaction(wallet_id=wallet.id, amount=100, currency="USD", type="credit", status="pending")
        db.session.add(tx)
        db.session.commit()

        assert tx.id is not None
        assert tx.wallet_id == wallet.id
        assert tx.amount == 100

def test_transaction_rollback(test_client):
    with app.app_context():
        wallet = Wallet(user_id=2, balance=0.0, currency="USD")
        db.session.add(wallet)
        db.session.commit()

        try:
            tx = Transaction(wallet_id=None, amount=50, currency="USD", type="debit", status="pending")
            db.session.add(tx)
            db.session.commit()
        except Exception:
            db.session.rollback()

        # Ensure no invalid transaction persisted
        assert Transaction.query.count() == 0
