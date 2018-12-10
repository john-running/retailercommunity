#__init__.py
import os
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_login import LoginManager  #automate management of login

login_manager = LoginManager()

app = Flask(__name__)

app.config['SECRET_KEY'] = 'newco'
basedir = os.path.abspath(os.path.dirname(__file__))
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///'+os.path.join(basedir,'data.sqlite')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

Migrate(app,db)

login_manager.init_app(app)

login_manager.login_view = 'login' # sets the view user needs to go to in order to log in
