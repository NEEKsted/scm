from datetime import datetime
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import Enum

db = SQLAlchemy()

class User(db.Model):
    __tablename__ = "user"
    
    user_id = db.Column(db.Integer, autoincrement=True, primary_key=True)
    user_fname = db.Column(db.String(100), nullable=False)
    user_lname = db.Column(db.String(100), nullable=False)
    user_name = db.Column(db.String(100), nullable=True)
    user_likes = db.Column(db.Integer, nullable=True)
    user_email = db.Column(db.String(120), nullable=False, unique=True)
    user_phone = db.Column(db.String(120), nullable=True)
    user_password = db.Column(db.String(255), nullable=False)
    user_address = db.Column(db.String(1000), nullable=True)
    user_state = db.Column(db.Integer, db.ForeignKey("states.id"), nullable=True)  # Fixed ForeignKey reference
    user_country = db.Column(db.Integer, db.ForeignKey("countries.id"), nullable=True)  # Fixed ForeignKey reference
    user_gen = db.Column(db.String(255), nullable=True,unique=True)
    user_pix = db.Column(db.String(120), nullable=True)
    user_datereg = db.Column(db.DateTime(), default=datetime.utcnow)
    user_status = db.Column(db.String(50),Enum('pending', 'enable', 'disable'), default='pending')  # Using Enum class for user status

    # Relationships
    usercountry = db.relationship('Country', backref='users')
    userstate = db.relationship('State', backref='users')

# Country Model
class Country(db.Model):
    __tablename__ = "countries"
    id = db.Column(db.Integer, primary_key=True)
    country_name = db.Column(db.String(150), nullable=False)
    # Define a relationship with the State model
    states = db.relationship('State', backref='country', lazy=True)

# State Model
class State(db.Model):
    __tablename__ = "states"
    id = db.Column(db.Integer, autoincrement=True, primary_key=True)
    country_id = db.Column(db.Integer, db.ForeignKey('countries.id'), nullable=False)  # Corrected table reference
    state_name = db.Column(db.String(150), nullable=False)
    
# Audio model
class Audio(db.Model):
    __tablename__="audios"
    audio_id = db.Column(db.Integer, autoincrement=True,primary_key=True)
    uploader = db.Column(db.Integer,db.ForeignKey('user.user_id'))
    lyricist = db.Column(db.String(120))
    audio = db.Column(db.String(120),nullable=False)
    lyric_title = db.Column(db.String(100),nullable=False)
    album = db.Column(db.String(120))
    likes = db.Column(db.Integer)
    dislikes = db.Column(db.Integer)
    quotes = db.Column(db.String(20))
    producer = db.Column(db.String(100))
    audio_status = db.Column(db.Enum("pending","bann","active"),default="pending")
    date_uploaded = db.Column(db.DateTime(), default=datetime.utcnow)

    #set foreignkey
    songuploader = db.relationship('User',backref='userratings')

# Admin model
class Scm_admin(db.Model):
    __tablename__="scmadmin"
    admin_id=db.Column(db.Integer, autoincrement=True,primary_key=True)
    admin_username=db.Column(db.String(20),nullable=False)
    admin_pwd=db.Column(db.String(200),nullable=False)