from datetime import datetime
from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

class User(db.Model):
    user_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    fname = db.Column(db.String(64), nullable=False)
    lname = db.Column(db.String(64), nullable=False)
    address = db.Column(db.String(200), nullable=False)
    city = db.Column(db.String(64), nullable=False)
    zipcode = db.Column(db.String(64), nullable=False)
    btc_balance = db.Column(db.String(64), nullable=False)
    eth_balance = db.Column(db.String(64), nullable=False)
    freezed_balance = db.Column(db.String(64), nullable=False)
    regdate = db.Column(db.DateTime, default=datetime.utcnow)
    email = db.Column(db.String(100), nullable=False)
    ssn = db.Column(db.String(50), nullable=True)  # Consider encrypting this field
    password = db.Column(db.String(225), nullable=False)
    otp = db.Column(db.String(225), nullable=True)
    
    user_transactions = db.relationship("Transaction", back_populates="user", cascade='all, delete-orphan')
    user_upload = db.relationship("Upload", back_populates="user", cascade='all, delete-orphan')

class Transaction(db.Model):
    trans_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    trans_name = db.Column(db.String(64), nullable=False)
    trans_amount = db.Column(db.Numeric, nullable=False)
    trans_filename = db.Column(db.String(64), nullable=True)
    trans_plan = db.Column(db.String(64), nullable=False)
    trans_status = db.Column(db.String(64), nullable=False)
    trans_action = db.Column(db.String(64), nullable=False)
    trans_date = db.Column(db.DateTime, default=datetime.utcnow)
    trans_user_id = db.Column(db.Integer, db.ForeignKey('user.user_id'))
    user = db.relationship("User", back_populates="user_transactions")


class Check(db.Model):
    check_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    check_name = db.Column(db.String(64), nullable=False)
    check_amount = db.Column(db.Numeric, nullable=False)
    check_user_id = db.Column(db.Integer, db.ForeignKey('user.user_id'))

class Upload(db.Model):
    upload_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    upload_date = db.Column(db.DateTime, default=datetime.utcnow)
    upload_user_id = db.Column(db.Integer, db.ForeignKey('user.user_id'))
    user = db.relationship("User", back_populates="user_upload")

class Adminreg(db.Model):
    admin_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    admin_username = db.Column(db.String(20), unique=True, nullable=False)
    admin_pwd = db.Column(db.String(200), nullable=False)
