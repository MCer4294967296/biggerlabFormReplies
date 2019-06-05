import json
from flask import Flask, abort, request, render_template
import parseForms
import templates
import formNameTranslation
import pymongo
import itchat

lc = lambda : print("Login Successful.")
ec = lambda : print("Logout Successful.")

app = Flask(__name__)

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

    parser = parseForms.translation[form] # from the unique form name, we get the parser
    # we surely can do it in one step, but this doesn't really matter
    info = parser(jsonObj["entry"]).update({"_id" : int(jsonObj["entry"]["serial_number"])}) # parse the info out
    
    col = db[form] # access the database

    '''entry = { "_id": int(jsonObj['serial_number']), 
              "studentName": info["studentName"],
              "teacherName": info["teacherName"],
              "courseStartDate": info["courseStartDate"],
              "courseName": info["courseName"],
              "rateAttendance": info["rateAttendance"],
              "rateUnderstanding": info["rateUnderstanding"],
              "rateAssignmentCompletion": info["rateAssignmentCompletion"],
              "rateGeneral": info["rateGeneral"],
              "projScreenshot": info["projScreenshot"],
              "studentLearnt": info["studentLearnt"],
              "teacherComment": info["teacherComment"] }
              '''
    try:
        col.insert_one(info) # try inserting,
    except pymongo.errors.DuplicateKeyError: # if duplicate,
        return "500 Internal Server Error: Duplicate Key", 500 # then err out
        # we can also do a query instead of trying to insert, # TODO
    return "200 OK", 200 # otherwise we are good

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
    #堵塞进程后无法执行后续代码，res.status(200)无法返回，
    #金数据要求：该服务器需在2秒内返回2XX（200，201等）作为应答。不然会重试最多6次post请求
    #bot.join()
    """

@app.route("/sendToWechat", methods=["POST"])
def sendToWechat():
    if not request.is_json():
        abort(400)
        print("Data is not a json, rejecting.")
    jsonObj = json.loads(json.dumps(request.json, ensure_ascii=False))
    if jsonObj['form'] == "" or jsonObj['id'] <= 0:
        abort(400)
        print("Unexpected data.")

    form = jsonObj['form'] # get the unique form name
    
    col = db[form] # access the database

    info = col.find({"_id": jsonObj['id']}) # retrieve the information
    template = templates.translation[form] # grab the template
    message = template(info) # formulate the message
    target = "filehelper" # placeholder, should be from info

    itchat.send(msg=message, toUserName=target) # send the message
    col.update_one({'_id': jsonObj['id']}, {'$set': {'sentToWechat': True}}) # update the database
    
    return "200 OK", 200


if __name__ == '__main__':
    itchat.auto_login(hotReload=True, loginCallback=lc, exitCallback=ec, enableCmdQR=2)
    # login when starting the server instead of doing it when data arrives
    db = pymongo.MongoClient("mongodb://localhost:27017/")['jinshuju']
    # prepare for the database
    print("hah") # ¯¯¯¯\_(ツ)_/¯¯¯¯
    app.run(host='0.0.0.0', port=5050, debug=True)
