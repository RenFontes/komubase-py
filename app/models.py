#app/models.py
from app import db
from app.model_utils import BigIntegerType
from passlib.hash import pbkdf2_sha256 as sha256

class User(db.Model):
    id = db.Column(BigIntegerType, primary_key=True, autoincrement=True)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(120), nullable=False)
    email_confirmed = db.Column(db.Boolean, nullable=False, default=False)

    @classmethod
    def hash_password(cls, password):
        return sha256.hash(password)

    @classmethod
    def verify_password(cls, password, hash):
        return sha256.verify(password, hash)

    def __repr__(self):
        return f"User('{self.email}')"

