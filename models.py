"""SQLAlchemy models for Scribcraft"""
import datetime

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
                          server_default=db.func.current_timestamp())
    about_me = db.Column(
        db.Text, default="Edit profile to write bio!")
    password = db.Column(db.String(150), nullable=False)
    scribs = db.relationship('Scrib', backref="user")
    comments = db.relationship("Comment", backref="user")

    def __repr__(self):
        """for debugging purposes return clear user string"""
        return f"<User #{self.id}: {self.username}, {self.email}>"

    def serialize_user(self):
        """return dictionary representation of user object"""

        return {
            "id": self.id,
            "username": self.username,
            "email": self.email,
            "image_url": self.image_url,
            "timestamp": self.date_time,
            "bio": self.about_me,
            "scribs": [scrib.serialize_scrib() for scrib in self.scribs]
        }

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
    title = db.Column(db.Text, nullable=False, unique=True)
    prompt = db.Column(db.Text, nullable=False)
    scrib_text = db.Column(db.Text, nullable=False)
    date_time = db.Column(db.DateTime(timezone=True),
                          server_default=db.func.current_timestamp())
    concept_images = db.relationship('ConceptImage', backref="scrib")
    user_id = db.Column(db.Integer, db.ForeignKey(
        'users.id', ondelete='CASCADE'), nullable=False)

    def serialize_scrib(self):
        """return dictionary representation of user object"""

        return {
            "id": self.id,
            "title": self.title,
            "prompt": self.prompt,
            "scrib_text": self.scrib_text,
            "timestamp": self.date_time,
            "concept_images": [concept_image.concept_image_url for concept_image in self.concept_images],
            "user_id": self.user_id,
            "user_username": self.user.username,
            "user_image_url": self.user.image_url
        }


class ConceptImage(db.Model):
    """Model for generated AI images to be stored"""
    __tablename__ = "concept_images"

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    concept_image_url = db.Column(db.Text, nullable=False)
    scrib_id = db.Column(db.Integer, db.ForeignKey(
        'scribs.id', ondelete='CASCADE'), nullable=False)


class Comment(db.Model):
    """Model for comments left on scribs"""
    __tablename__ = "comments"

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    comment_text = db.Column(db.Text, nullable=False)
    date_time = db.Column(db.DateTime(timezone=True),
                          server_default=db.func.current_timestamp())
    user_id = db.Column(db.Integer, db.ForeignKey(
        'users.id', ondelete='CASCADE'), nullable=False)
    scrib_id = db.Column(db.Integer, db.ForeignKey(
        'scribs.id', ondelete='CASCADE'), nullable=False)
