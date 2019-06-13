import json
from flask import Flask, abort, request, render_template
from flask_cors import CORS
import parseForms
import templates
import formNameTranslation
import pymongo
import itchat


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
        abort(400)
        print("Data is not a json, rejecting.")

    jsonObj = json.loads(json.dumps(request.json, ensure_ascii=False)) 

    form = formNameTranslation.translation[jsonObj["form"]] # get the unique form name
    # if form != translator.translate(jsonObj["form_name"]): THEN WE PROBABLY NEED TO MAINTAIN THE DICTIONARY

    # bot = Bot(console_qr=True, cache_path=True)
    # 群组不活跃的情况下，群组搜索出错。
    # 群组test只有一个群的时候，搜索出错。
    # 群组搜索下如何命名微信群
    # target_group = bot.groups(update=True, contact_only=False).search('test')[0]

    parser = parseForms.translation[form] # from the unique form name, we get the parser.
    info = parser(jsonObj["entry"]) # parse the information out,
    id = int(jsonObj["entry"]["serial_number"])
    info.update({"_id" : id})
    col = db[form] # access the database.

    try:
        col.insert_one(info) # try inserting,
    except pymongo.errors.DuplicateKeyError: # if duplicate,
        return "500 Internal Server Error: Duplicate Key", 500 # then err out;
        # we can also do a query instead of trying to insert, # TODO

    metaInit = metaInitializer.translation[form]
    meta = metaInit(jsonObj["entry"])
    meta.update({"jsjid" : id}) # jinshuju id, this is probably not the main key, so we don't use "_id"
    col = db["meta" + form]
    try:
        col.insert_one(meta) # try inserting,
    except pymongo.errors.DuplicateKeyError: # if duplicate,
        return "500 Internal Server Error: Duplicate Key", 500 # then err out;
        # we can also do a query instead of trying to insert, # TODO

    return None, 200 # otherwise we are good

    #itchat.send_msg(msg=message, toUserName="filehelper")
    #itchat.send_msg(msg=message, toUserName=itchat.search_friends(name="Rock大石头")[0]["UserName"])

    #提交类型判断需有修改,当前只有Course Time Submission后执行推送
    """
    submitTypes = ['Course Time Submission','Brainstorm Document Submission','Project Document Submission','Technical Realization Stage Report','Project Publication(End of Project)']
    
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
    if jsonObj['form'] == "" or int(jsonObj['id']) <= 0:
        return "400 BAD REQUEST: Unexpected data.", 400

    form = jsonObj['form'] # get the unique form name

    col = db[form] # access the database

    info = col.find({"_id": jsonObj['id']})[0] # retrieve the information
    template = templates.translation[form] # grab the template
    message = template(info) # formulate the message
    target = "filehelper" # placeholder, should be from info

    itchat.send(msg=message, toUserName=target) # send the message
    col = db["meta" + form]
    col.update_one({'id': jsonObj['id']}, {'$set': {'sentToWechat': True}}) # update the database

    return "200 OK", 200


@app.route("/getPage/<form>", methods=["GET"])
def sendPage(form=""):
    idStart = request.args.get("idStart")
    idEnd = request.args.get("idEnd")
    if not idStart and not idEnd:
        idStart = 0
        idEnd = 10
    elif not idStart:
        idEnd = int(idEnd)
        idStart = idEnd - 10
    elif not idEnd:
        idStart = int(idStart)
        idEnd = idStart + 10
    else:
        idStart = int(idStart)
        idEnd = int(idEnd)
    print(idStart, idEnd)
    #id = int(id)

    col = db[form]
    leftList = []
    for id in range(idStart, idEnd):
        info = col.find({"_id": id})[0]
        #message = templates.translation[form](info)
        item = {"id": info["_id"], "studentName": info["studentName"]}
        leftList.append(item)
    return render_template("viewDocu.html", leftList=leftList)

    '''
    message = ret[0]
    with open("templates/viewDocu.html", 'r') as f:
        docu = '\n'.join(f.readlines())
        docu = docu.replace("$message", message)\
                   .replace("$form", form)\
                   .replace("$previd", str(id - 1))\
                   .replace("$nextid", str(id + 1))\
                   .replace("$currid", str(id))\
                   .replace("$message", message)
    return docu, 200
    '''

@app.route("/vendor/<fileName>", methods=["GET"])
def vendor(fileName):
    vendors = {
        "bootstrap.min.css": "vendor/bootstrap/css/",
        "jquery.slim.min.js": "vendor/jquery/",
        "bootstrap.min.js": "vendor/bootstrap/js/",
        "popper.min.js": "vendor/"
    }
    file = open(vendors[fileName] + fileName, 'r')
    return ''.join(file.readlines), 200

ec = lambda : print("Logout Successful.")

if __name__ == '__main__':
    itchat.auto_login(hotReload=True, loginCallback=lambda : print("Login Successful."), enableCmdQR=2)
    # login when starting the server instead of doing it when data arrives
    db = pymongo.MongoClient("mongodb://localhost:27017/")['jinshuju']
    # prepare for the database
    print("hah") # ¯¯¯¯\_(ツ)_/¯¯¯¯
    app.run(host='0.0.0.0', port=5050, debug=False)
