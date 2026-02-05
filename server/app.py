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

# (Keep your existing health check and validation routes below here)
# ...

if __name__ == '__main__':
    app.run(debug=True, port=int(os.getenv('OWOPAY_PORT', 5000)))

# ... (inside server/app.py, near the bottom)

@app.route('/api/v1/wallets', methods=['POST'])
def create_wallet():
    data = request.get_json()
    if not data or 'user_id' not in data:
        return jsonify({"error": "Missing user_id"}), 400

    # --- Week 3: DB Interaction ---
    # Create a new Wallet object using your data model
    new_wallet = Wallet(user_id=data['user_id'], balance=0.0)

    try:
        # Add to the database session
        db.session.add(new_wallet)
        # Commit the transaction to save it permanently
        db.session.commit()
        
        return jsonify({
            "status": "success", 
            "wallet_id": new_wallet.id, 
            "user_id": new_wallet.user_id,
            "balance": new_wallet.balance
        }), 201

    except Exception as e:
        db.session.rollback() # CRITICAL: Undo changes if it fails
        return jsonify({"error": "Failed to create wallet", "details": str(e)}), 500

# (Keep your if __name__ == '__main__': ... block below)
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
