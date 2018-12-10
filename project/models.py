# models.py

from project import db,login_manager
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin # provides built in attributes we can call during views

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(user_id)

class User(db.Model,UserMixin):
    __tablename__ = 'users'
    id = db.Column(db.Integer,primary_key = True)
    email = db.Column(db.String(64),unique=True)
    fname = db.Column(db.String(64))
    lname = db.Column(db.String(64))
    nickname = db.Column(db.String(64))
    rewardsid = db.Column(db.String(64))
    role = db.Column(db.String(64), nullable=True)
    active = db.Column(db.Boolean, nullable=True)
    password_hash = db.Column(db.String(128))

    def __init__(self,email,fname,lname,nickname,rewardsid,role,active,password):
        self.email = email
        self.fname = fname
        self.lname = lname
        self.nickname = nickname
        self.rewardsid = rewardsid
        self.role = role
        self.active = active
        self.password_hash = generate_password_hash(password)

    def check_password(self,password):
        return check_password_hash(self.password_hash,password)

class Product(db.Model):
    __tablename__ = 'products'
    id = db.Column(db.Integer,primary_key = True)
    name = db.Column(db.String(128))
    image = db.Column(db.String(128))
    price = db.Column(db.Float)
    producturl = db.Column(db.String(128))
    sku = db.Column(db.String(64), nullable=True)
    description = db.Column(db.Text, nullable=True)
    reviewpoints = db.Column(db.Integer, nullable=True)

    def __init__(self,name,image,price,producturl,sku,description,reviewpoints):
        self.name = name
        self.image = image
        self.price = price
        self.producturl = producturl
        self.sku = sku
        self.description = description
        self.reviewpoints = reviewpoints

class Purchase(db.Model):
    __tablename__ = 'purchases'
    id = db.Column(db.Integer,primary_key = True)
    product_id = db.Column(db.Integer,db.ForeignKey('products.id'))
    user_id = db.Column(db.Integer,db.ForeignKey('users.id'))
    hasreview= db.Column(db.Integer, nullable=True)
    product = db.relationship("Product")
    user = db.relationship("User")

    def __init__(self,product_id,user_id,hasreview):
        self.product_id = product_id
        self.user_id = user_id
        self.hasreview= hasreview

class Review(db.Model):
    __tablename__ = 'reviews'
    id = db.Column(db.Integer,primary_key = True)
    heading = db.Column(db.String(512))
    description = db.Column(db.Text)
    starrating = db.Column(db.Float)
    user_id = db.Column(db.Integer,db.ForeignKey('users.id'))
    status=db.Column(db.String(128), nullable=True)
    feedback=db.Column(db.Text, nullable=True)
    user = db.relationship("User")
    product_id = db.Column(db.Integer,db.ForeignKey('products.id'))
    product = db.relationship("Product")

    def __init__(self,heading,description,starrating,user_id,status,feedback,product_id):
        self.heading = heading
        self.description = description
        self.starrating= starrating
        self.user_id= user_id
        self.status= status
        self.product_id= product_id
        self.feedback= feedback
