"""SQLAlchemy models for Scribcraft"""

from sqlalchemy.sql import func
from flask_bcrypt import Bcrypt
from flask_sqlalchemy import SQLAlchemy

bcrypt = Bcrypt()
db = SQLAlchemy()


def connect_db(app):
    """connect db to provided flask app"""
    db.app = app
    db.init_app(app)

# CLASS MODELS


class User(db.Model):
    """User on the site"""

    __tablename__ = "users"

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    username = db.Column(db.String(20), nullable=False, unique=True)
    email = db.Column(db.String(100), nullable=False, unique=True)
    image_url = db.Column(
        db.String(150), default="/static/images/quill_and_ink.png")
    date_time = db.Column(db.DateTime(timezone=True),
                          server_default=func.now())
    about_me = db.Column(db.Text)
    password = db.Column(db.String(150), nullable=False)
    scribs = db.relationship('Scrib', backref="user")
    comments = db.relationship("Comment", backref="user")

    def __repr__(self):
        """for debugging purposes return clear user string"""
        return f"<User #{self.id}: {self.username}, {self.email}>"

    @classmethod
    def signup(cls, username, email, password, image_url):
        """Sign up user. Handles password hashing and db session adding logic"""
        hashed_pw = bcrypt.generate_password_hash(password).decode('UTF-8')

        user = User(username=username, email=email,
                    password=hashed_pw, image_url=image_url)

        db.session.add(user)
        return user

    @classmethod
    def authenticate(cls, username, password):
        """find and authenticate user from db with given username and password, returns false is authentication fails"""
        user = cls.query.filter_by(username=username).first()

        if user:
            is_auth = bcrypt.check_password_hash(user.password, password)
            if is_auth:
                return user

        return False


class Scrib(db.Model):
    """Model for scribs generated from AI API"""

    __tablename__ = "scribs"

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    title = db.Column(db.Text, nullable=False)
    prompt = db.Column(db.Text, nullable=False)
    scrib_text = db.Column(db.Text, nullable=False)
    date_time = db.Column(db.DateTime(timezone=True),
                          server_default=func.now())
    user_id = db.Column(db.Integer, db.ForeignKey(
        'users.id', ondelete='CASCADE'), nullable=False)


class Comment(db.Model):
    """Model for comments left on scribs"""
    __tablename__ = "comments"

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    comment_text = db.Column(db.Text, nullable=False)
    date_time = db.Column(db.DateTime(timezone=True),
                          server_default=func.now())
    user_id = db.Column(db.Integer, db.ForeignKey(
        'users.id', ondelete='CASCADE'), nullable=False)
    scrib_id = db.Column(db.Integer, db.ForeignKey(
        'scribs.id', ondelete='CASCADE'), nullable=False)
