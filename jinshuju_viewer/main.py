import json, logging, requests
from flask import Flask, render_template, g
from flask_cors import CORS
import pymongo
from .utils import *


# initialization    
app = Flask(__name__)
CORS(app)
# read config
app.config.from_pyfile('config.py', silent=True)
# prepare for the database
db = pymongo.MongoClient(app.config["MONGODBSERVER"])['jinshuju']
# register routes
from .Form import BiggerlabCourseFeedback
app.register_blueprint(BiggerlabCourseFeedback.bp)
from .Form import LittleUnicornMentorshipReport
app.register_blueprint(LittleUnicornMentorshipReport.bp)
from .Form import Unseen


@app.route("/", methods=["GET"])
def home():
    '''The index page renderer.
    '''
    # need to traverse the db, return value includes 
    cols = db.list_collection_names()
    bots = getActiveBots(app.config["WECHATBOTSERVER"])
    for bot in bots:
        bot["HeadSource"] = "{}static/{}.png".format(app.config["WECHATBOTSERVER"], bot["NickName"])
    g.WECHATSERVER=app.config["WECHATBOTSERVER"]
    return render_template("index.html", forms=cols, bots=bots)


@app.route("/important", methods=["GET"])
def important():
    bots = getActiveBots(app.config["WECHATBOTSERVER"]) # get the alive bots
    for bot in bots:
        bot["HeadSource"] = "{}static/{}.png".format(app.config["WECHATBOTSERVER"], bot["NickName"]) # get the bots a head image.

    g.WECHATBOTSERVER = app.config["WECHATBOTSERVER"]
    return render_template("important.html", bots=bots)