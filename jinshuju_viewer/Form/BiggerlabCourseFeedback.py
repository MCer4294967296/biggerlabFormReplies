import functools, json, requests
from flask import (
    Blueprint, flash, g, jsonify, make_response, redirect, render_template, request, session, url_for
)
from .. import form, main, utils


bp = Blueprint('BiggerlabCourseFeedback', __name__, url_prefix='/BiggerlabCourseFeedback')

class BiggerlabCourseFeedback(form.ToWechatForm):

    form = "BiggerlabCourseFeedback"
    col = main.db[form]
    mCol = main.db["meta" + form]


    @staticmethod
    @bp.route("/", methods=["GET"])
    def getPage():
        bots = utils.getActiveBots(main.app.config["WECHATBOTSERVER"])
        for bot in bots:
            bot["HeadSource"] = "{}static/{}.png".format(main.app.config["WECHATBOTSERVER"], bot["NickName"])
        
        idStart = request.args.get("idStart")
        idEnd = request.args.get("idEnd")
        if idStart or idEnd:
            try:
                idEnd = int(idEnd) if idEnd else None
                idStart = int(idStart) if idStart else None
            except:
                return make_response(("id is not valid.", 400))

        docs = BiggerlabCourseFeedback.col.find()
        chosen, prevID, nextID = utils.getIDList(docs, idStart=idStart, idEnd=idEnd)

        leftList = []
        for i in range(len(chosen)):
            doc = chosen[i]
            id = doc["_id"]
            mInfo = BiggerlabCourseFeedback.mCol.find({"jsjid": id})[0]
            item = {"id": id, "studentName": doc["studentName"] + (" (已发送)" if mInfo["sentToWechat"] else "")}
            leftList.append(item)

        prevLink = "{base_url}?idEnd={prevID}".format(base_url=request.base_url, prevID=prevID) if prevID is not None else None
        nextLink = "{base_url}?idStart={nextID}".format(base_url=request.base_url, nextID=nextID) if nextID is not None else None

        return render_template("Form/BiggerlabCourseFeedback.html", prevLink=prevLink, nextLink=nextLink, leftList=leftList, bots=bots, WECHATBOTSERVER=main.app.config["WECHATBOTSERVER"])


    @staticmethod
    @bp.route("/jinshujuIN", methods=["POST"])
    def jinshujuIN():
        if not request.is_json:
            logging.warning("/jinshujuIN received non-json data.")
            return make_response(("Data is not a json, rejecting.", 400))

        jsonObj = json.loads(json.dumps(request.json, ensure_ascii=False))    

        # formNameTranslation.translation[jsonObj["form"]] # get the unique form name
        #id = jsonObj["entry"]["serial_number"])

        rawInfo = jsonObj["entry"]

        info = BiggerlabCourseFeedback.parse(rawInfo) # parse the information out,

        try:
            col.insert_one(info) # try inserting,
        except pymongo.errors.DuplicateKeyError: # if duplicate,
            return "400 you fked up: Duplicate Key", 400 # then err out;
            # we can also do a query instead of trying to insert, # TODO

        mInfo = BiggerlabCourseFeedback.mParse(rawInfo)

        try:
            mCol.insert_one(metaInfo) # try inserting,
        except pymongo.errors.DuplicateKeyError: # if duplicate,
            return "400 you fked up: Duplicate Key", 400 # then err out;

        logging.info("Entry added to databases.")
        return "200 OK", 200 # otherwise we are good


    @staticmethod
    @bp.route("/getDoc", methods=["GET"])
    def getDoc():
        id = int(request.args.get("id"))
        #print(list(BiggerlabCourseFeedback.col.find()))
        info = BiggerlabCourseFeedback.col.find({"_id": id})[0]
        mInfo = BiggerlabCourseFeedback.mCol.find({"jsjid": id})[0]
        message = mInfo["message"]
        if message == "":
            message = BiggerlabCourseFeedback.genMessage(id)
            BiggerlabCourseFeedback.mCol.update_one({"jsjid": id}, {"$set": {"message": message}})
        return jsonify({"id": id,
                        "message": message,
                        "studentName": info["studentName"],
                        "teacherName": info["teacherName"],
                        "reasonFilling": info["reasonFilling"],
                        "messageEdited": mInfo["edited"]})


    @staticmethod
    def parse(rawInfo):

        def deDownload(linkArr):
            return "" if len(linkArr) == 0 else (linkArr[0][:-9] if linkArr[0].endswith("&download") else linkArr[0])
        # 有些link最后会带一个"&download" 这会导致它默认下载而不是预览，所以我们扔掉它。

        info = {}

        info["_id"] = rawInfo["serial_number"]

        info["reasonFilling"] = rawInfo["field_5"] # 填表原因

        info["teacherName"] = rawInfo["field_4"] # 导师姓名
        info["teacherComment"] = rawInfo["field_19"] # 导师评价

        info["studentName"] = rawInfo["field_6"] + rawInfo["field_31"] # 学生姓名

        info["courseName"] = rawInfo["field_8"] # 课程名
        info["courseStartDate"] = rawInfo["field_9"] # 课程开始日期
        info["courseEndDate"] = rawInfo["field_12"] # 课程结束日期
        info["courseContent"] = rawInfo["field_13"] # 已上课程内容
        info["courseCapturelink"] = rawInfo["field_32"] # 课程视频链接
        info["projectScreenshot"] = utils.shorten(deDownload(rawInfo["field_18"])) # 项目作品截图

        info["rateAttendance"] = rawInfo["field_14"] # 学生课堂参与度
        info["rateUnderstanding"] = rawInfo["field_15"] # 知识点理解情况
        info["rateAssignmentCompletion"] = rawInfo["field_16"] # 课堂任务完成情况
        info["rateGeneral"] = rawInfo["field_17"] # 综合评价

        info["reasonChanging"] = rawInfo["field_20"] # 交接原因
        info["nextTeacher"] = rawInfo["field_21"] # 接手导师姓名
        info["classType"] = rawInfo["field_23"] # 上课形式
        info["classStartTime"] = rawInfo["field_10"] # 上课时间
        info["classEndTime"] = rawInfo["field_11"] # 下课时间
        info["hoursTaught"] = rawInfo["field_25"] # 已上课时数

        info["awardReceived"] = rawInfo["field_33"] # 学生是否获得相应荣誉
        info["awardType"] = rawInfo["field_37"] # 荣誉类型
        info["projectDescription"] = rawInfo["field_42"] # 学生项目描述/所学内容
        info["teacherNotes"] = rawInfo["field_46"] # 导师对该学生的评语

        info["awardEvidence"] = utils.shorten(deDownload(rawInfo["field_40"])) # 竞赛获奖证明截图
        info["competitionName"] = rawInfo["field_34"] # 比赛名称
        info["prizeReceived"] = rawInfo["field_35"] # 获得的奖项

        info["projectPublishEvidence"] = utils.shorten(deDownload(rawInfo["field_47"])) # 项目发布证明截图
        info["copyrightEvidence"] = utils.shorten(deDownload(rawInfo["field_48"])) # 著作权证明截图
        info["projectLink"] = rawInfo["field_43"] # 项目链接
        info["sourceCode"] = utils.shorten(deDownload(rawInfo["field_36"])) # 源代码文件

        info["admissionEvidence"] = utils.shorten(deDownload(rawInfo["field_49"])) # 名校录取证明截图
        info["schoolName"] = rawInfo["field_44"] # 学校名称
        info["profession"] = rawInfo["field_45"] # 专业名称

        info["awardOthers"] = utils.shorten(deDownload(rawInfo["field_50"])) # 其他荣誉证明截图
        return info

    
    @staticmethod
    def mParse(rawInfo):
        mInfo = {}

        mInfo["jsjid"] = rawInfo["serial_number"]
        
        mInfo["viewed"] = False
        mInfo["sentToWechat"] = False
        mInfo["message"] = ""
        mInfo["edited"] = False

        return mInfo

    
    messageTemplates = {
        "试听课反馈，由课程顾问复述给家长" :
"""{studentName}家长您好，导师{teacherName}对您的孩子于{courseStartDate}试听的{courseName}作出了反馈。
课堂参与度：{rateAttendance}
知识点理解情况：{rateUnderstanding}
课堂任务完成情况：{rateAssignmentCompletion}
综合：{rateGeneral}

这是您的孩子所学的课程内容：{courseContent}
您可以点击{projectScreenshot}来查看您孩子的作品。
这是导师对您的孩子作出的评价：{teacherComment}""",
        "月度课程反馈，给家长" : 
"""{studentName}家长您好，导师{teacherName}对您的孩子于{courseStartDate}开始的{courseName}作出了月度课程反馈。
课堂参与度：{rateAttendance}
知识点理解情况：{rateUnderstanding}
课堂任务完成情况：{rateAssignmentCompletion}
综合：{rateGeneral}

您可以点击{projectScreenshot}来查看您的孩子的项目进展。
这是您的孩子最近正在学的课程内容：{courseContent}
这是导师对您的孩子作出的评价：{teacherComment}""",
        "阶段性+续费课程反馈，给家长" :
"""{studentName}家长您好，导师{teacherName}对您的孩子于{courseStartDate}开始的{courseName}作出了反馈。
课堂参与度：{rateAttendance}
知识点理解情况：{rateUnderstanding}
课堂任务完成情况：{rateAssignmentCompletion}
综合：{rateGeneral}

您可以点击{projectScreenshot}来查看您的孩子的项目进展。
这是您的孩子最近正在学的课程内容：{courseContent}
这是导师对您的孩子作出的评价：{teacherComment}"""
    }


    @staticmethod
    def genMessage(id):
        
        info = BiggerlabCourseFeedback.col.find({"_id": id})[0]

        if info["reasonFilling"] not in BiggerlabCourseFeedback.messageTemplates.keys():
            return "" # it was "other"

        message = BiggerlabCourseFeedback.messageTemplates[info["reasonFilling"]].format(**info)
        return message


    @staticmethod
    @bp.route("/sendToWechat", methods=["POST"])
    def sendToWechat():
        if not request.is_json:
            return make_response(("Data is not a json, rejecting.", 400))
        id = request.json.get("id", None)

        bots = utils.getActiveBots(main.app.config["WECHATBOTSERVER"])
        if not bots:
            return make_response(("There are no bots alive.", 400))
        
        try:
            targetList = request.json["targetList"]
            message = request.json["message"]
        except:
            return make_response(("TargetList or Message is not specified.", 400))
        
        fail = False
        for target in targetList:
            if " || " in target:
                remarkName, nickName = target.split(" || ")
                #remarkName = remarkName if remarkName != "" else None
                #userNameList.append(itchat.search_friends(nickName=nickName, remarkName=remarkName)[0]["UserName"])
            else:
                nickName = target
                remarkName = ""
                #userNameList.append(itchat.search_chatrooms(name=target)[0]["UserName"])
            resp = requests.post(main.app.config["WECHATBOTSERVER"] + "send", json={
                    "message": message,
                    "NickName": nickName,
                    "hintRemarkName": remarkName
            })
            if resp.status_code != 200:
                fail = True
            else:
                try:
                    id = int(id)
                    BiggerlabCourseFeedback.mCol.update_one({'jsjid': id}, {'$set': {'sentToWechat': True}}) # update the database
                except:
                    pass

        if fail:
            return make_response(("There were problems sending some of the messages.", 500))
        else:
            return make_response(("Message is sent.", 200))