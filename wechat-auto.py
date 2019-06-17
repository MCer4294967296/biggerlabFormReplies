import json, os, subprocess, time, random
from flask import Flask, abort, request, render_template, jsonify
from flask_cors import CORS
import pymongo, itchat
import parseForms, templates, formNameTranslation, metaInitializer


app = Flask(__name__)
CORS(app)


def getroom_message(n):
    #获取群的username，对群成员进行分析需要用到
    itchat.dump_login_status() # 显示所有的群聊信息，默认是返回保存到通讯录中的群聊
    RoomList =  itchat.search_chatrooms(name=n)
    if RoomList:
        return RoomList[0]['UserName']
    else:
        print("%s group is not found!" % (name))


@app.route("/jinshujuIN", methods=["POST"])
def jinshujuIN():
    if not request.is_json:
        return "400 BAD REQUEST: Data is not a json, rejecting.", 400

    jsonObj = json.loads(json.dumps(request.json, ensure_ascii=False))

    form = formNameTranslation.translation[jsonObj["form"]] # get the unique form name
    id = int(jsonObj["entry"]["serial_number"])

    # bot = Bot(console_qr=True, cache_path=True)
    # 群组不活跃的情况下，群组搜索出错。
    # 群组test只有一个群的时候，搜索出错。
    # 群组搜索下如何命名微信群
    # target_group = bot.groups(update=True, contact_only=False).search('test')[0]

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

    """
    groupName = 'BP-' + beforeSend['field_2'] +'-'
    group = itchat.search_chatrooms(name=groupName)
    if group:
        itchat.send_msg(msg = afterSend,toUserName=getroom_message(groupName))
    else:
        itchat.send('Could not find the group', toUserName='filehelper')
        itchat.send_msg(msg = afterSend, toUserName='filehelper')
    #print (data + ' sendCompleted')
    #避免微信发消息过于频繁，延时
    time.sleep(0.5)

    #1小时后itchat刷新，维持在线状态

    #afterSend未定义，if判断未执行状态下，会报错建议写入if条件下
    #target_group.send(afterSend)
    #bot.join()
    """


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
            nickName, remarkName = target.split(" || ")[0]
        userNameList.append(itchat.search_friends(nickName=nickName, remarkName=remarkName)[0]["UserName"])

    col = db[form] # access the database
    info = col.find({"_id": id})[0] # retrieve the information

    message = jsonObj["message"]
    for userName in userNameList:
        itchat.send(msg=message, toUserName=userName)
    # target = "filehelper" # placeholder, should be from info

    # itchat.send(msg=message, toUserName=target) # send the message
    meta = db["meta" + form]
    meta.update_one({'jsjid': id}, {'$set': {'sentToWechat': True}}) # update the database

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
    chosen = []
    if idStart and idEnd:
        chosen = list(docs.where("this['_id'] >= {idStart} && this['_id'] <= {idEnd}").format(idStart=idStart, idEnd=idEnd).sort("_id", pymongo.DESCENDING))
        prevID = idStart - 1
        nextID = idEnd + 1
    elif idStart:
        match = list(docs.where("this['_id'] >= {idStart}".format(idStart=idStart)).sort("_id", pymongo.DESCENDING))
        chosen = match[-10:]
        prevID = idStart - 1
        nextID = chosen[0]["_id"] + 1 if len(match) > 10 else None
    elif idEnd:
        match = list(docs.where("this['_id'] <= {idEnd}".format(idEnd=idEnd)).sort("_id", pymongo.DESCENDING))
        chosen = match[:10]
        prevID = chosen[-1]["_id"] - 1 if len(match) > 10 else None
        nextID = idEnd + 1
    else:
        match = list(docs.sort("_id", pymongo.DESCENDING))
        chosen = match[:10]
        prevID = chosen[-1]["_id"] - 1 if len(match) > 10 else None
        nextID = None

    meta = db["meta" + form]
    leftList = []
    for i in range(len(chosen)):
        doc = chosen[i]
        id = doc["_id"]
        metainfo = meta.find({"jsjid": id})[0]
        item = {"id": id, "studentName": doc["studentName"] + (" (已发送)" if metainfo["sentToWechat"] else "")}
        leftList.append(item)

    wechatInfo = {}
    wechatInfo["wechatLoggedIn"] = itchat.originInstance.alive
    if wechatInfo["wechatLoggedIn"]:
        wechatInfo["wechatNickName"] = itchat.get_friends()[0]["NickName"] if wechatInfo["wechatLoggedIn"] else ""
        wechatInfo["wechatContactList"] = [friend["NickName"] + " || " + friend["RemarkName"] for friend in itchat.get_friends()]
        wechatInfo["wechatContactList"].extend([chatroom["NickName"] for chatroom in itchat.get_chatrooms()])
    

    if len(leftList) == 0:
        return render_template("viewDocu.html", wechatInfo=wechatInfo)
    prevLink = "{base_url}?idEnd={prevID}".format(base_url=request.base_url, prevID=prevID) if prevID is not None else None
    nextLink = "{base_url}?idStart={nextID}".format(base_url=request.base_url, nextID=nextID) if nextID is not None else None
    return render_template("viewDocu.html", leftList=leftList, prevLink=prevLink, nextLink=nextLink, wechatInfo=wechatInfo)


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

    meta = db["meta" + form] # access the database
    try:
        result = meta.update_one({"jsjid": id}, {"$set": {"message": messageToSave, "edited": True}})
    except:
        return "400 BAD REQUEST: ? I don't know what's bad but yea.", 400
    return "200 OK: Message Saved.", 200



@app.route("/getMessage/<form>/<id>", methods=["GET"])
def getMessage(form, id):
    id = int(id)
    meta = db["meta" + form]
    message = meta.find({"jsjid": id})[0]["message"]
    if message == "":
        info = db[form].find({"_id": id})[0]
        message = templates.translation[form](info)
        meta.update_one({"jsjid": id}, {"$set": {"message": message}})
    return jsonify({"id": id, "message": message})


@app.route("/regenMessage", methods=["POST"])
def regenMessage():
    pass


def lc():
    itchat.get_head_img(picDir="static/wechatStuff/me.jpg")
    for chatroom in itchat.get_chatrooms(update=True):
        itchat.get_head_img(chatroomUserName=chatroom["UserName"], picDir="static/wechatStuff/{}.jpg".format(chatroom["NickName"]))
    for friend in itchat.get_friends(update=True):
        itchat.get_head_img(userName=friend["UserName"], picDir="static/wechatStuff/{}.jpg".format(friend["NickName"] + " || " + friend["RemarkName"]))
    os.remove("QR.png")
    for f in os.listdir("static/wechatStuff"):
        if f.endswith(".jpg"):
            subprocess.run(["convert", "static/wechatStuff/{}".format(f), "-resize", "100x100", "static/wechatStuff/{}".format(f)])


def ec():
    for f in os.listdir("static/wechatStuff"):
        os.remove("static/wechatStuff/{}".format(f))


@app.route("/login", methods=["GET"])
def login():
    if itchat.originInstance.alive:
        return "400 BAD REQUEST: it's already logged in.", 400
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
    rand = random.Random()

    def send(self, msg, toUserName=None, mediaId=None):
        global lastSentMsgTimestamp
        while time.time() - lastSentMsgTimestamp < 3:
            sleep(rand.random() + 1)
        lastSentMsgTimestamp = time.time()
        self.send(msg, toUserName, mediaId)
    itchat.originInstance.send = send
    # prepare for the database
    print("---Server has started---") # ¯¯¯¯\_(ツ)_/¯¯¯¯
    app.run(host='0.0.0.0', port=5050, debug=False)
