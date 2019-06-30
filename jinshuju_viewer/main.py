import json, logging, requests
from flask import Flask, render_template
from flask_cors import CORS
import pymongo
from .utils import *


# initialization    
app = Flask(__name__)
CORS(app)
# read config
app.config.from_pyfile('config.py', silent=True)
# register routes
db = pymongo.MongoClient(app.config["MONGODBSERVER"])['jinshuju']
# prepare for the database

from .Form import BiggerlabCourseFeedback
app.register_blueprint(BiggerlabCourseFeedback.bp)
from .Form import Unseen


@app.route("/", methods=["GET"])
def home():
    # need to traverse the db, return value includes 
    cols = db.list_collection_names()
    bots = getActiveBots(app.config["WECHATBOTSERVER"])
    for bot in bots:
        bot["HeadSource"] = "{}static/{}.png".format(app.config["WECHATBOTSERVER"], bot["NickName"])
    return render_template("index.html", forms=cols, bots=bots)
