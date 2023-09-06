from flask import Flask, request, jsonify
from app import app, db
from app.models import User

@app.route('/register', methods=['POST'])
def register():
    data = request.get_json()
    hashwed_pw = User.hash_password(data['password'])
    new_user = User(email=data['email'], password=hashwed_pw)
    db.session.add(new_user)
    db.session.commit()
    return jsonify({"message": "User registered"}), 201

@app.route('/login', methods=['POST'])
def login():
    data = request.get_json()
    user = User.query.filter_by(email=data['email']).first()
    if user and User.verify_password(data['password'], user.password):
        # Session management, token generation, etc.
        return jsonify({"message": "Logged in"})
    return jsonify({"message": "Invalid credentials"}, 401)
