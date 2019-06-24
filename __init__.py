import logging
from flask import Flask, render_template
from flask_cors import CORS
import pymongo
import BiggerlabCourseFeedback

def create_app():
    global app, db

    app = Flask(__name__)
    CORS(app)
    # initialization    
    app.config.from_pyfile('config.py', silent=True)
    # read config
    app.register_blueprint(BiggerlabCourseFeedback.bp)
    # register routes
    db = pymongo.MongoClient(app.config[MongoDBServer])['jinshuju']
    # prepare for the database
    return app


@app.route("/", methods=["GET"])
def home():
    # need to traverse the db, return value includes 
    pass


if __name__ == '__main__':

    #rand = random.Random()

    logging.basicConfig(format='%(asctime)s - %(message)s', datefmt='%d-%b-%y %H:%M:%S', level=logging.DEBUG)

    def limited_send(msg, toUserName=None, mediaId=None):
        global lastSentMsgTimestamp
        while time.time() - lastSentMsgTimestamp < 3:
            sleep(rand.random() + 1)
        lastSentMsgTimestamp = time.time()
        itchat.send(msg, toUserName, mediaId)

    itchat.limited_send = limited_send
    itchat.myNickName = ""
    print("---Server has started---") # ¯¯¯¯\_(ツ)_/¯¯¯¯
    #app.run(host='0.0.0.0', port=5050, debug=True, use_reloader=False)