import os
from flask import Flask
from os.path import join, dirname, realpath


from flask_pymongo import PyMongo

def create_app():
    app = Flask(__name__, static_folder='static')

    app.config['UPLOAD_FOLDER'] = join(dirname(realpath(__file__)), './static/uploads/')
    app.config["MONGO_URI"] = "mongodb+srv://tista:cornell2021@cluster0.9dx7j.mongodb.net/Tista"

    return app

