import os
from flask import Flask
from os.path import join, dirname, realpath


from flask_pymongo import PyMongo

def create_app():
    app = Flask(__name__, static_folder='static')

    app.config['UPLOAD_FOLDER'] = join(dirname(realpath(__file__)), './static/uploads/')
    app.config["MONGO_URI"] = os.environ.get("MONGO_URL")

    return app

