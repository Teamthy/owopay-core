import os
from flask import Flask, jsonify, request
from flask_cors import CORS
from dotenv import load_dotenv
from marshmallow import Schema, fields, ValidationError

load_dotenv()

app = Flask(__name__)
CORS(app)

@app.route('/api/v1/health', methods=['GET'])
def health():
    return jsonify({
        "status": "active",
        "service": "OwoPay-Core",
        "version": "1.0.0"
    }), 200

@app.route('/api/v1/transfer/validate', methods=['POST'])
def validate_transfer():
    json_data = request.get_json()
    if not json_data:
        return jsonify({"error": "No data provided"}), 400
    
    # Simple Week 1 Logic: check if keys exist
    if 'sender_wallet' not in json_data or 'amount' not in json_data:
        return jsonify({"error": "Missing required fields"}), 422

    return jsonify({"status": "valid", "message": "OwoPay validated"}), 200

if __name__ == '__main__':
    app.run(debug=True, port=5000)
