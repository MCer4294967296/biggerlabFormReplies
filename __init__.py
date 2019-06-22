from flask import Flask
from flask_cors import CORS

def create_app():
    app = Flask(__name__, )
    CORS(app)
    db = pymongo.MongoClient("mongodb://localhost:27017/")['jinshuju']
    return app

if __name__ == '__main__':
    # itchat.auto_login(hotReload=True, loginCallback=lambda : print("Login Successful."), enableCmdQR=2)
    # login when starting the server instead of doing it when data arrives
    db = pymongo.MongoClient("mongodb://localhost:27017/")['jinshuju']
    # prepare for the database
    rand = random.Random()

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