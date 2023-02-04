from app import db
from models import User, Scrib, connect_db


db.drop_all()
db.create_all()
