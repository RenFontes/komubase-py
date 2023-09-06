from flask import request, jsonify
import jwt
import datetime
from app import app, db
from app.models import User

@app.route('/register', methods=['POST'])
def register():
    data = request.get_json()

    user = User.query.filter_by(email=data['email']).first()
    if user:
        return jsonify({"message": "User already exists"})

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

        token = jwt.encode({
            'user_id': user.id,
            'exp': datetime.datetime.utcnow() + datetime.timedelta(hours=720)
        }, app.config["SECRET_KEY"], algorithm='HS256')

        return jsonify({'token': token})
    return jsonify({"message": "Invalid credentials"}), 401
