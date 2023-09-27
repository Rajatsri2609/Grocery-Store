from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash,check_password_hash
db=SQLAlchemy()
from datetime import *


class User(db.Model):
    __tablename__='user'
    id=db.Column(db.Integer,primary_key=True)
    username = db.Column(db.String(40),unique=True,nullable=False)
    password_hash=db.Column(db.String(100),nullable=False)
    name = db.Column(db.String(50),nullable=True)
    is_admin=db.Column(db.Boolean,nullable=False,default=False)

    @property
    def password(self):
        raise AttributeError('password is not a readable attribute')
    
    @password.setter
    def password(self,password):
        self.password_hash=generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash,password)

class Category(db.Model):
    __tablename__ = 'category'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), nullable=False)
    is_deleted = db.Column(db.Boolean, nullable=False, default=False)

    products = db.relationship('Product', backref='Category', lazy=True)

class Product(db.Model):
    __tablename__ = 'product'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), nullable=False)
    price = db.Column(db.Float, nullable=False)
    quantity = db.Column(db.Integer, nullable=False)
    category_id = db.Column(db.Integer, db.ForeignKey('category.id'), nullable=False)
    availability = db.Column(db.Integer, nullable=True)
    manufacturing_date = db.Column(db.Date, nullable=False)
    is_deleted = db.Column(db.Boolean, nullable=False, default=False)

    c = db.relationship('Cart', backref='product', lazy=True)
    ord = db.relationship('Order', backref='product', lazy=True)

    
class Cart(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    product_id = db.Column(db.Integer, db.ForeignKey('product.id'), nullable=False)
    quantity = db.Column(db.Integer, nullable=False)

class Payment(db.Model):
    payment_id=db.Column(db.Integer,primary_key=True)
    payment_date_time=db.Column(db.DateTime,nullable=False,default=datetime.utcnow)
    user_id=db.Column(db.Integer,db.ForeignKey('user.id'),nullable=False)
    amount=db.Column(db.Float,nullable=False)

    orders = db.relationship('Order', backref='payment', lazy=True)


class Order(db.Model):
    id=db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer,db.ForeignKey('user.id'),nullable=False)
    product_id = db.Column(db.Integer,db.ForeignKey('product.id'),nullable=False)
    quantity=db.Column(db.Integer,nullable=False)
    Price=db.Column(db.Float,nullable=False)
    datetime=db.Column(db.String)
    payment_id = db.Column(db.Integer, db.ForeignKey('payment.payment_id'), nullable=False)
