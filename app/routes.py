from flask import request, jsonify, url_for
import jwt
import datetime
from app import app, db, mail
from app.models import User
from app.decorators.jwt_decorators import token_required
from flask_mail import Message
from itsdangerous import URLSafeTimedSerializer

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

    if app.config['EMAIL_CONFIRMATION_REQUIRED']:
        token = create_confirmation_token(new_user.email)
        confirm_url = url_for('confirm_email', token=token, _external=True)
        msg = Message('Please confirm your email', recipients=[new_user.email])
        msg.body = f'Hi {new_user.email}, please confirm your email using the following link: {confirm_url}'

        try:
            mail.send(msg)
        except:
            # Handle your email sending failure here. For instance, log the error.
            return jsonify({"message": "Email sending failed. Please try again."}), 500

        # Only add and commit the user to the database after the email is successfully sent
        db.session.add(new_user)
        db.session.commit()

        return jsonify({"message": "User registered, please confirm your email"}), 201

    db.session.add(new_user)
    db.session.commit()
    return jsonify({"message": "User registered"}), 201

@app.route('/login', methods=['POST'])
def login():
    data = request.get_json()
    user = User.query.filter_by(email=data['email']).first()
    if user and User.verify_password(data['password'], user.password):

        if app.config['EMAIL_CONFIRMATION_REQUIRED'] and not user.email_confirmed:
            return jsonify({"message": "Please confirm your email before logging in."}), 401

        token = jwt.encode({
            'user_id': user.id,
            'exp': datetime.datetime.utcnow() + datetime.timedelta(hours=720)
        }, app.config["SECRET_KEY"], algorithm='HS256')

        return jsonify({'token': token})
    return jsonify({"message": "Invalid credentials"}), 401

@app.route('/validate', methods=['GET'])
@token_required
def validate():
    return jsonify({"message": "Token has been validated"})


@app.route('/confirm/<token>', methods=['GET'])
def confirm_email(token):
    token_email = confirm_token(token)
    if not token_email:
        return jsonify({"message": "The confirmation link is invalid or has expired."}), 400

    user = User.query.filter_by(email=token_email).first_or_404()
    if user.email_confirmed:
        return jsonify({"message": "Account already confirmed. Please login."}), 200

    user.email_confirmed = True
    db.session.add(user)
    db.session.commit()
    return jsonify({"message": "You have confirmed your account. Thanks!"}), 200


def create_confirmation_token(email):
    """Generate a secure token for account confirmation."""
    serializer = URLSafeTimedSerializer(app.config["SECRET_KEY"])
    return serializer.dumps(email, salt=app.config["SECURITY_PASSWORD_SALT"])

def confirm_token(token, expiration=3600):
    """Confirm the token, return email if valid, otherwise raise itsdangerous.exc.SignatureExpired."""
    serializer = URLSafeTimedSerializer(app.config["SECRET_KEY"])
    try:
        email = serializer.loads(
            token,
            salt=app.config["SECURITY_PASSWORD_SALT"],
            max_age=expiration
        )
    except:
        return False
    return email
