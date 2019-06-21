import json, os, subprocess, time, random, signal, sys
from flask import Flask, abort, request, render_template, jsonify, Response
from flask_cors import CORS
import pymongo, itchat
import parseForms, templates, formNameTranslation, metaInitializer
from utils import *


app = Flask(__name__)
CORS(app)

signal.signal(signal.SIGINT, handler)


@app.route("/jinshujuIN", methods=["POST"])
def jinshujuIN():
    # 群组test只有一个群的时候，搜索出错。
    if not request.is_json:
        return "400 BAD REQUEST: Data is not a json, rejecting.", 400

    jsonObj = json.loads(json.dumps(request.json, ensure_ascii=False))

    form = formNameTranslation.translation[jsonObj["form"]] # get the unique form name
    id = int(jsonObj["entry"]["serial_number"])


    parser = parseForms.translation[form] # from the unique form name, we get the parser.
    info = parser(jsonObj["entry"]) # parse the information out,
    info.update({"_id" : id})
    col = db[form] # access the database.

    try:
        col.insert_one(info) # try inserting,
    except pymongo.errors.DuplicateKeyError: # if duplicate,
        return "400 you fked up: Duplicate Key", 400 # then err out;
        # we can also do a query instead of trying to insert, # TODO

    metaInit = metaInitializer.translation[form]
    metaInfo = metaInit(jsonObj["entry"])
    metaInfo.update({"jsjid" : id}) # jinshuju id, this is probably not the main key, so we don't use "_id"
    meta = db["meta" + form]
    try:
        meta.insert_one(metaInfo) # try inserting,
    except pymongo.errors.DuplicateKeyError: # if duplicate,
        return "400 you fked up: Duplicate Key", 400 # then err out;

    return "200 OK", 200 # otherwise we are good

    #itchat.send_msg(msg=message, toUserName="filehelper")
    #itchat.send_msg(msg=message, toUserName=itchat.search_friends(name="Rock大石头")[0]["UserName"])


@app.route("/sendToWechat", methods=["POST"])
def sendToWechat():
    if not request.is_json:
        return "400 BAD REQUEST: Data is not a json, rejecting.", 400
    jsonObj = json.loads(json.dumps(request.json, ensure_ascii=False))
    if jsonObj["form"] == "" or jsonObj["id"] is None or int(jsonObj["id"]) <= 0:
        return "400 BAD REQUEST: Unexpected data.", 400

    if not itchat.originInstance.alive:
        return "401 UNAUTHORIZED: You need to log in first.", 401

    form = jsonObj["form"] # get the unique form name
    id = int(jsonObj["id"])

    targetList = jsonObj["targetList"]
    userNameList = []
    for target in targetList:
        if " || " in target:
            nickName, remarkName = target.split(" || ")
            remarkName = remarkName if remarkName != "" else None
            userNameList.append(itchat.search_friends(nickName=nickName, remarkName=remarkName)[0]["UserName"])
        else:
            userNameList.append(itchat.search_chatrooms(name=target)[0]["UserName"])

    mCol = db["meta" + form]
    try:
        message = jsonObj["message"]
    except:
        message = mInfo["message"]
        if message == "":
            message = genMessage(form, id)
            mCol.update_one({"jsjid": id}, {"$set": {"message": message}})

    for userName in userNameList:
        itchat.send(msg=message, toUserName=userName)
    # target = "filehelper" # placeholder, should be from info

    # itchat.send(msg=message, toUserName=target) # send the message
    mCol.update_one({'jsjid': id}, {'$set': {'sentToWechat': True}}) # update the database

    return "200 OK", 200


@app.route("/getPage/<form>", methods=["GET"])
def getPage(form=""):
    idStart = request.args.get("idStart")
    idEnd = request.args.get("idEnd")
    if idStart or idEnd:
        try:
            idEnd = int(idEnd) if idEnd else None
            idStart = int(idStart) if idStart else None
        except:
            return "400 BAD REQUEST: id is not valid.", 400
    col = db[form]
    docs = col.find()
    chosen, prevID, nextID = getIDList(docs, idStart=idStart, idEnd=idEnd)
    
    meta = db["meta" + form]
    leftList = []
    for i in range(len(chosen)):
        doc = chosen[i]
        id = doc["_id"]
        metainfo = meta.find({"jsjid": id})[0]
        item = {"id": id, "studentName": doc["studentName"] + (" (已发送)" if metainfo["sentToWechat"] else "")}
        leftList.append(item)

    wechatInfo = {}
    wechatInfo["wechatLoggingIn"] = itchat.originInstance.isLogging
    wechatInfo["wechatLoggedIn"] = itchat.originInstance.alive
    if wechatInfo["wechatLoggedIn"]:
        wechatInfo["wechatNickName"] = itchat.get_friends()[0]["NickName"]
        wechatInfo["wechatContactList"] = []
        for friend in itchat.get_friends():
            if "/" not in friend["NickName"] and "/" not in friend["RemarkName"]:
                wechatInfo["wechatContactList"].append(friend["NickName"] + " || " + friend["RemarkName"])
        for chatroom in itchat.get_chatrooms():
            if "/" not in chatroom["NickName"]:
                wechatInfo["wechatContactList"].append(chatroom["NickName"])
    elif wechatInfo["wechatLoggingIn"]:
        wechatInfo["loadedHeadPercentage"] = "{}/{}".format(len(os.listdir("static/wechatStuff"))-2, len(itchat.get_chatrooms()) + len(itchat.get_friends()))
    formName = form

    if len(leftList) == 0:
        return render_template("viewDocu.html", wechatInfo=wechatInfo, formName=formName)
    prevLink = "{base_url}?idEnd={prevID}".format(base_url=request.base_url, prevID=prevID) if prevID is not None else None
    nextLink = "{base_url}?idStart={nextID}".format(base_url=request.base_url, nextID=nextID) if nextID is not None else None
    return render_template("viewDocu.html", leftList=leftList, prevLink=prevLink, nextLink=nextLink, wechatInfo=wechatInfo, formName=formName)


@app.route("/saveToDB", methods=["POST"])
def saveToDB():
    if not request.is_json:
        return "400 BAD REQUEST: Data is not a json, rejecting.", 400
    jsonObj = json.loads(json.dumps(request.json, ensure_ascii=False))
    if jsonObj["form"] == "" or jsonObj["id"] is None or int(jsonObj["id"]) <= 0:
        return "400 BAD REQUEST: Unexpected data.", 400

    form = jsonObj["form"] # get the unique form name
    id = int(jsonObj["id"])
    messageToSave = jsonObj["message"]

    if messageToSave != genMessage(form, id):
        meta = db["meta" + form] # access the database
        try:
            result = meta.update_one({"jsjid": id}, {"$set": {"message": messageToSave, "edited": True}})
        except:
            return "400 BAD REQUEST: ? I don't know what's bad but yea.", 400
        return "200 OK: Message Saved.", 200
    else:
        return "200 OK: Message is not modified.", 200


@app.route("/getInfo/<form>/<id>", methods=["GET"])
def getInfo(form, id):
    id = int(id)
    col = db[form]
    mCol = db["meta" + form]
    info = col.find({"_id": id})[0]
    mInfo = mCol.find({"jsjid": id})[0]
    
    message = mInfo["message"]
    if message == "":
        message = genMessage(form, id)
        mCol.update_one({"jsjid": id}, {"$set": {"message": message}})
    return jsonify({"id": id,
                    "message": message,
                    "studentName": info["studentName"],
                    "teacherName": info["teacherName"],
                    "reasonFilling": info["reasonFilling"],
                    "messageEdited": mInfo["edited"]})


def genMessage(form, id):
    return templates.translation[form](db[form].find({"_id": id})[0])


def lc():
    myNickName = itchat.search_friends()["NickName"].replace("/", "")
    itchat.get_head_img(picDir="static/wechatStuff/{}.png".format(myNickName))
    subprocess.run(["convert", "static/wechatStuff/{}.png".format(myNickName), "-resize", "50x50", "static/wechatStuff/{}.png".format(myNickName)])
    contactList = []
    for chatroom in itchat.get_chatrooms():
        if "/" not in chatroom["NickName"]:
            fName = chatroom["NickName"]
            contactList.append({"type": "chatroom", "fName": fName, "UserName": chatroom["UserName"]})
    for friend in itchat.get_friends():
        if "/" not in friend["NickName"] and "/" not in friend["RemarkName"]:
            fName = friend["NickName"] + " || " + friend["RemarkName"]
            contactList.append({"type": "friend", "fName": fName, "UserName": friend["UserName"]})
    try:
        os.listdir("haha")
    except FileExistsError:
        pass
        
    dirContent = os.listdir("static/wechatStuff/{}".format(myNickName))

    for contact in contactList:
        if (contact["fName"] in dirContent):
            contactList.remove(contact)

    def func(elem):
        if elem["type"] == "friend":
            itchat.get_head_img(userName=elem["UserName"], picDir="static/wechatStuff/{}/{}.jpg".format(myNickName, fName))
        elif elem["type"] == "chatroom":
            itchat.get_head_img(chatroomUserName=elem["UserName"], picDir="static/wechatStuff/{}/{}.jpg".format(myNickName, fName))

    multiThreadMap(func, contactList, 2)

    def func(elem):
        if elem.endswith(".jpg"):
            subprocess.run(["convert", "static/wechatStuff/{}.jpg".format(f), "-resize", "50x50", "static/wechatStuff/{}.jpg".format(f)])

    multiThreadMap(func, dirContent)


def ec():
    print("Calling exit callback function.")
    try:
        os.remove("QR.png")
    except FileNotFoundError:
        pass


@app.route("/login", methods=["GET"])
def login():
    if itchat.originInstance.alive:
        return "400 BAD REQUEST: it's already logged in.", 400
    if "QR.png" in os.listdir():
        return "400 BAD REQUEST: you are logging in.", 400
    itchat.auto_login(loginCallback=lc, exitCallback=ec)

    return "200 OK: login complete.", 200
    

@app.route("/logout", methods=["GET"])
def logout():
    itchat.logout()
    return "200 OK: logout complete."
    

if __name__ == '__main__':
    # itchat.auto_login(hotReload=True, loginCallback=lambda : print("Login Successful."), enableCmdQR=2)
    # login when starting the server instead of doing it when data arrives
    db = pymongo.MongoClient("mongodb://localhost:27017/")['jinshuju']
    # prepare for the database
    rand = random.Random()

    def send(self, msg, toUserName=None, mediaId=None):
        global lastSentMsgTimestamp
        while time.time() - lastSentMsgTimestamp < 3:
            sleep(rand.random() + 1)
        lastSentMsgTimestamp = time.time()
        self.send(msg, toUserName, mediaId)

    itchat.send = send
    print("---Server has started---") # ¯¯¯¯\_(ツ)_/¯¯¯¯
    app.run(host='0.0.0.0', port=5050, debug=True, use_reloader=False)