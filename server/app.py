import os
from flask import Flask, jsonify, request
from flask_cors import CORS
from dotenv import load_dotenv
# New Imports:
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate

load_dotenv()

app = Flask(__name__)
# Configure the database connection string from your .env file
app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('DATABASE_URL')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)
migrate = Migrate(app, db) # Tool for managing database changes

# --- Week 2: Define the Wallet Data Model ---
class Wallet(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, unique=True, nullable=False)
    balance = db.Column(db.Float, nullable=False, default=0.0)
    currency = db.Column(db.String(10), nullable=False, default=os.getenv('DEFAULT_CURRENCY'))
    created_at = db.Column(db.DateTime, server_default=db.func.now())
    updated_at = db.Column(db.DateTime, server_default=db.func.now(), onupdate=db.func.now())

    def __repr__(self):
        return f'<Wallet {self.user_id}: {self.balance} {self.currency}>'


# --- Week 3: Define the Transaction Data Model ---
class Transaction(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    wallet_id = db.Column(db.Integer, db.ForeignKey('wallet.id'), nullable=False)
    amount = db.Column(db.Numeric(precision=12, scale=2), nullable=False)
    currency = db.Column(db.String(3), nullable=False)
    type = db.Column(db.String(10), nullable=False)  # "credit" or "debit"
    status = db.Column(db.String(20), nullable=False, default="pending")
    created_at = db.Column(db.DateTime, server_default=db.func.now())

    wallet = db.relationship('Wallet', backref=db.backref('transactions', lazy=True))

    def __repr__(self):
        return f'<Transaction {self.id}: {self.type} {self.amount} {self.currency}>'


# --- API Routes ---

@app.route('/api/v1/wallets', methods=['POST'])
def create_wallet():
    data = request.get_json()
    if not data or 'user_id' not in data or 'currency' not in data:
        return jsonify({"error": "Missing required fields"}), 400

    try:
        new_wallet = Wallet(
            user_id=data['user_id'],
            balance=data.get('balance', 0.0),
            currency=data['currency']  # ✅ ensure currency is set
        )
        db.session.add(new_wallet)
        db.session.commit()

        return jsonify({
            "status": "success",
            "wallet_id": new_wallet.id,
            "user_id": new_wallet.user_id,
            "balance": str(new_wallet.balance),
            "currency": new_wallet.currency
        }), 201

    except Exception as e:
        db.session.rollback()
        return jsonify({"error": "Failed to create wallet", "details": str(e)}), 500


@app.route('/api/v1/wallets', methods=['GET'])
def list_wallets():
    wallets = Wallet.query.all()
    return jsonify([
        {
            "wallet_id": w.id,
            "user_id": w.user_id,
            "balance": str(w.balance),
            "currency": w.currency
        } for w in wallets
    ]), 200


@app.route('/api/v1/wallets/<int:wallet_id>', methods=['GET'])
def get_wallet(wallet_id):
    wallet = Wallet.query.get(wallet_id)
    if not wallet:
        return jsonify({"error": "Wallet not found"}), 404

    return jsonify({
        "wallet_id": wallet.id,
        "user_id": wallet.user_id,
        "balance": str(wallet.balance),
        "currency": wallet.currency
    }), 200


if __name__ == '__main__':
    app.run(debug=True, port=int(os.getenv('OWOPAY_PORT', 5000)))
