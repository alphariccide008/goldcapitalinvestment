from flask import Flask
from flask_migrate import Migrate
from flask_wtf.csrf import CSRFProtect
#instantiate the object of Flask
csrf =CSRFProtect()




def create_app():
    from pkg.models import db
    app=Flask(__name__)
    app.config.from_pyfile("config.py",silent=True)
    db.init_app(app)
    migrate= Migrate(app,db)
    csrf.init_app(app)
    return app

app=create_app()

#load routes from here 
from pkg import admin_routes, user_routes
from pkg.forms import*