import logging, requests
from flask import Flask, render_template
from flask_cors import CORS
import pymongo


# initialization    
app = Flask(__name__)
CORS(app)
# read config
app.config.from_pyfile('jinshuju_viewer/config.py', silent=True)
# register routes
db = pymongo.MongoClient("mongodb://localhost:27017/")['jinshuju']
# prepare for the database

from . import form

from .Form import BiggerlabCourseFeedback
app.register_blueprint(BiggerlabCourseFeedback.bp)


@app.route("/", methods=["GET"])
def home():
    # need to traverse the db, return value includes 
    cols = db.list_collection_names()
    bots = json.loads(requests.get(app.config["WechatBotServer"], params={"json" : True}).content)
    for bot in bots:
        bot["HeadSource"] = "{}static/{}.png".format(app.config["WechatBotServer"], bot["NickName"])
    render_template("index.html", forms=cols, bots=bots)
