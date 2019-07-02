import datetime, functools, json, requests
from flask import (Blueprint, flash, g, jsonify, make_response, redirect,
                   render_template, request, session, url_for)
import pymongo
from .. import form, main, utils


bp = Blueprint('LittleUnicornMentorshipReport', __name__, url_prefix='/LittleUnicornMentorshipReport')

class LittleUnicornMentorshipReport(form.ToWechatForm):

    form = "LittleUnicornMentorshipReport"
    col = main.db[form]
    mCol = main.db["meta" + form]


    @staticmethod
    @bp.route("/", methods=["GET"])
    def getPage():
        raise NotImplementedError
        '''The renderer of the viewer page. 
        :returns: the rendered page or 400.
        '''
        bots = utils.getActiveBots(main.app.config["WECHATBOTSERVER"]) # get the alive bots
        for bot in bots:
            bot["HeadSource"] = "{}static/{}.png".format(main.app.config["WECHATBOTSERVER"], bot["NickName"]) # get the bots a head image.
        
        idStart = request.args.get("idStart")
        idEnd = request.args.get("idEnd")
        if idStart or idEnd:
            try:
                idEnd = int(idEnd) if idEnd else None
                idStart = int(idStart) if idStart else None
            except:
                return make_response(("id is not valid.", 400))
        # parse out the id range limiters.

        docs = BiggerlabCourseFeedback.col.find() # query the database,
        chosen, prevID, nextID = utils.getIDList(docs, idStart=idStart, idEnd=idEnd) # and choose documents as wanted.

        leftList = [] # initialize the message list on the left.
        for i in range(len(chosen)): # for each chosen document,
            doc = chosen[i]
            id = doc["_id"]
            mInfo = BiggerlabCourseFeedback.mCol.find({"jsjid": id})[0]
            item = {"id": id, "studentName": doc["studentName"] + (" (已发送)" if mInfo["sentToWechat"] else "")}
            # construct the individual item.
            leftList.append(item)

        prevLink = "{base_url}?idEnd={prevID}".format(base_url=request.base_url, prevID=prevID) if prevID is not None else None
        nextLink = "{base_url}?idStart={nextID}".format(base_url=request.base_url, nextID=nextID) if nextID is not None else None
        # calculate the previous and next link's id range limiter.
        g.WECHATBOTSERVER = main.app.config["WECHATBOTSERVER"]
        return render_template("Form/BiggerlabCourseFeedback.html", prevLink=prevLink, nextLink=nextLink, leftList=leftList, bots=bots, WECHATBOTSERVER=main.app.config["WECHATBOTSERVER"])
        #return render_template("wechatted.html", prevLink=prevLink, nextLink=nextLink, leftList=leftList, bots=bots, WECHATBOTSERVER=main.app.config["WECHATBOTSERVER"])


    @staticmethod
    @bp.route("/jinshujuIN", methods=["POST"])
    def jinshujuIN():
        raise NotImplementedError
        '''the jinshuju data handler.
        :returns: A helpful message and a status code.
        '''
        if not request.is_json:
            logging.warning("/jinshujuIN received non-json data.")
            return make_response(("Data is not a json, rejecting.", 400))

        jsonObj = json.loads(json.dumps(request.json, ensure_ascii=False))    

        # formNameTranslation.translation[jsonObj["form"]] # get the unique form name
        #id = jsonObj["entry"]["serial_number"])

        rawInfo = jsonObj["entry"]

        info = BiggerlabCourseFeedback.parse(rawInfo) # parse the information out,

        try:
            BiggerlabCourseFeedback.col.insert_one(info) # try inserting,
        except pymongo.errors.DuplicateKeyError: # if duplicate,
            return "400 you fked up: Duplicate Key", 400 # then err out;
            # we can also do a query instead of trying to insert, # TODO

        mInfo = BiggerlabCourseFeedback.mParse(rawInfo)

        try:
            BiggerlabCourseFeedback.mCol.insert_one(mInfo) # try inserting,
        except pymongo.errors.DuplicateKeyError: # if duplicate,
            return "400 you fked up: Duplicate Key", 400 # then err out;

        return "200 OK", 200 # otherwise we are good


    @staticmethod
    @bp.route("/getDoc", methods=["GET"])
    def getDoc():
        raise NotImplementedError
        id = int(request.args.get("id"))
        #print(list(BiggerlabCourseFeedback.col.find()))
        info = BiggerlabCourseFeedback.col.find({"_id": id})[0]
        mInfo = BiggerlabCourseFeedback.mCol.find({"jsjid": id})[0]
        message = mInfo["message"]
        if message == "":
            message = BiggerlabCourseFeedback.genMessage(id)
            BiggerlabCourseFeedback.mCol.update_one({"jsjid": id}, {"$set": {"message": message}})
        BiggerlabCourseFeedback.mCol.update_one({"jsjid": id}, {"$set": {"viewed": True}})
        return jsonify({"id": id,
                        "message": message,
                        "studentName": info["studentName"],
                        "teacherName": info["teacherName"],
                        "reasonFilling": info["reasonFilling"],
                        "messageEdited": mInfo["edited"]})


    @staticmethod
    @bp.route("/getDocs", methods=["POST"])
    def getDocs():
        raise NotImplementedError
        if request.is_json:
            data = request.json
        else:
            data = request.args
        
        idStart = data.get("idStart", None)
        idEnd = data.get("idEnd", None)
        timeFilledStart = data.get("timeFilledStart", None)
        timeFilledEnd = data.get("timeFilledEnd", None)
        reasonFillingList = data.get("reasonFillingList", None)
        count = int(data.get("count", 100))
        offset = int(data.get("offset", 0))

        queryString = "true"
        if idStart:
            queryString += "&& this['_id'] >= {idStart}".format(idStart=idStart)
            # docs = docs.where("this['_id'] >= {idStart}".format(idStart=idStart))
        if idEnd:
            queryString += "&& this['_id'] <= {idEnd}".format(idEnd=idEnd)
            # docs = docs.where("this['_id'] <= {idEnd}".format(idEnd=idEnd))
        docs = BiggerlabCourseFeedback.col.find().where(queryString)
        chosen = []
        while True:
            try:
                chosen.append(docs.next())
            except StopIteration:
                break
        mQueryString = "true"
        if timeFilledStart:
            mQueryString += "&& this['timeFilled'] >= {timeFilledStart}".format(timeFilledStart=timeFilledStart)
            # docs = docs.where("this['timeFilled'] >= {timeFilledStart}".format(timeFilledStart=timeFilledStart))
        if timeFilledEnd:
            mQueryString += "&& this['timeFilled'] <= {timeFilledEnd}".format(timeFilledEnd=timeFilledEnd)
            # docs = docs.where("this['timeFilled'] <= {timeFilledEnd}".format(timeFilledEnd=timeFilledEnd))
        print(mQueryString)
        mDocs = BiggerlabCourseFeedback.mCol.find().where(mQueryString)
        mChosen = []
        while True:
            try:
                mChosen.append(mDocs.next())
            except StopIteration:
                break
        #chosen = list(docs.where(queryString))
        
        if reasonFillingList:
            for doc in list(chosen):
                if doc["reasonFilling"] not in reasonFillingList:
                    chosen.remove(doc)
        
        mChosenID = [mDoc["jsjid"] for mDoc in mChosen]
        for doc in list(chosen):
            if doc["_id"] not in mChosenID:
                chosen.remove(doc)

        chosen = chosen[offset:count+offset]
        return jsonify(chosen)


    @staticmethod
    def parse(rawInfo):

        def deDownload(linkArr):
            return "" if len(linkArr) == 0 else (linkArr[0][:-9] if linkArr[0].endswith("&download") else linkArr[0])
        # 有些link最后会带一个"&download" 这会导致它默认下载而不是预览，所以我们扔掉它。

        info = {}

        info["jsjid"] = rawInfo["serial_number"]

        #info["reasonFilling"] = rawInfo["field_5"] # 填表原因

        info["teacherName"] = rawInfo["field_23"] # 导师姓名
        info["teacherRole"] = rawInfo["field_1"] # 导师角色
        info["teacherPhone"] = rawInfo["field_20"] # 导师手机
        #info["teacherComment"] = rawInfo["field_19"] # 导师评价

        info["studentName"] = rawInfo["field_63"] # 学生姓名

        info["projectType"] = rawInfo["field_6"] # 项目类型
        
        info["submissionCategory"] = rawInfo["field_31"] # 提交类型

        info["teacherTechDemoLink"] = rawInfo["field_64"] # 导师技术Demo提交链接
        info["teacherDemoVideo"] = rawInfo["field_37"] # 导师Demo展示视频

        info["projectStage"] = rawInfo["field_39"] # 项目阶段Stage Of the Project
        info["projectStageCompletion"] = rawInfo["field_28"] # 当前阶段完成进度（%）Stage Completion
        info["dateEventHappened"] = rawInfo["field_3"] # 发生日期 Date the event happened
        info["sessionStartTime"] = rawInfo["field_4"] # 辅导开始时间 Session started at
        info["sessionEndTime"] = rawInfo["field_24"] # 辅导结束时间 Session ended at
        info["sessionSummary"] = rawInfo["field_8"] # 本次辅导小结 Summary of the session
        info["sessionRelatedFiles"] = rawInfo["field_10"] # 上传辅导相关文件 Please upload related files here
        info["ifStudentHasHomework"] = rawInfo["field_46"] # 有无学生课后作业？
        info["ifteacherFinishedTeaching"] = rawInfo["field_47"] # 该导师授课内容是否完结？

        #info["courseName"] = rawInfo["field_8"] # 课程名
        #info["courseStartDate"] = rawInfo["field_9"] # 课程开始日期
        #info["courseEndDate"] = rawInfo["field_12"] # 课程结束日期
        #info["courseContent"] = rawInfo["field_13"] # 已上课程内容
        #info["courseCapturelink"] = rawInfo["field_32"] # 课程视频链接
        #info["projectScreenshot"] = utils.shorten(deDownload(rawInfo["field_18"])) # 项目作品截图

        #info["rateAttendance"] = rawInfo["field_14"] # 学生课堂参与度
        #info["rateUnderstanding"] = rawInfo["field_15"] # 知识点理解情况
        #info["rateAssignmentCompletion"] = rawInfo["field_16"] # 课堂任务完成情况
        #info["rateGeneral"] = rawInfo["field_17"] # 综合评价

        #info["reasonChanging"] = rawInfo["field_20"] # 交接原因
        #info["nextTeacher"] = rawInfo["field_21"] # 接手导师姓名
        #info["classType"] = rawInfo["field_23"] # 上课形式
        #info["classStartTime"] = rawInfo["field_10"] # 上课时间
        #info["classEndTime"] = rawInfo["field_11"] # 下课时间
        #info["hoursTaught"] = rawInfo["field_25"] # 已上课时数

        #info["awardReceived"] = rawInfo["field_33"] # 学生是否获得相应荣誉
        #info["awardType"] = rawInfo["field_37"] # 荣誉类型
        #info["projectDescription"] = rawInfo["field_42"] # 学生项目描述/所学内容
        #info["teacherNotes"] = rawInfo["field_46"] # 导师对该学生的评语

        #info["awardEvidence"] = utils.shorten(deDownload(rawInfo["field_40"])) # 竞赛获奖证明截图
        #info["competitionName"] = rawInfo["field_34"] # 比赛名称
        #info["prizeReceived"] = rawInfo["field_35"] # 获得的奖项

        #info["projectPublishEvidence"] = utils.shorten(deDownload(rawInfo["field_47"])) # 项目发布证明截图
        #info["copyrightEvidence"] = utils.shorten(deDownload(rawInfo["field_48"])) # 著作权证明截图
        #info["projectLink"] = rawInfo["field_43"] # 项目链接
        #info["sourceCode"] = utils.shorten(deDownload(rawInfo["field_36"])) # 源代码文件

        #info["admissionEvidence"] = utils.shorten(deDownload(rawInfo["field_49"])) # 名校录取证明截图
        #info["schoolName"] = rawInfo["field_44"] # 学校名称
        #info["profession"] = rawInfo["field_45"] # 专业名称

        #info["awardOthers"] = utils.shorten(deDownload(rawInfo["field_50"])) # 其他荣誉证明截图
        return info

    
    @staticmethod
    def mParse(rawInfo):
        mInfo = {}

        mInfo["jsjid"] = rawInfo["serial_number"]
        
        mInfo["viewed"] = False
        mInfo["sentToWechat"] = False
        mInfo["message"] = ""
        mInfo["edited"] = False
        mInfo["timeFilled"] = datetime.datetime.now()

        return mInfo


    @staticmethod
    def messageTemplatesTmp(**info):
        reasonFilling = info["reasonFilling"]
        if reasonFilling == "阶段性+续费课程反馈，给家长":
            template = \
"""{studentName}家长您好，导师{teacherName}对您的孩子于{courseStartDate}开始的{courseName}作出了反馈。
课堂参与度：{rateAttendance}
知识点理解情况：{rateUnderstanding}
课堂任务完成情况：{rateAssignmentCompletion}
综合：{rateGeneral}

您可以点击{projectScreenshot}来查看您的孩子的项目进展。
这是您的孩子最近正在学的课程内容：{courseContent}
这是导师对您的孩子作出的评价：{teacherComment}"""
        elif reasonFilling == "月度课程反馈，给家长":
            template = \
"""{studentName}家长您好，导师{teacherName}对您的孩子于{courseStartDate}开始的{courseName}作出了月度课程反馈。
课堂参与度：{rateAttendance}
知识点理解情况：{rateUnderstanding}
课堂任务完成情况：{rateAssignmentCompletion}
综合：{rateGeneral}

您可以点击{projectScreenshot}来查看您的孩子的项目进展。
这是您的孩子最近正在学的课程内容：{courseContent}
这是导师对您的孩子作出的评价：{teacherComment}"""
        elif reasonFilling == "试听课反馈，由课程顾问复述给家长":
            template = \
"""{studentName}家长您好，导师{teacherName}对您的孩子于{courseStartDate}试听的{courseName}作出了反馈。
课堂参与度：{rateAttendance}
知识点理解情况：{rateUnderstanding}
课堂任务完成情况：{rateAssignmentCompletion}
综合：{rateGeneral}

这是您的孩子所学的课程内容：{courseContent}
您可以点击{projectScreenshot}来查看您孩子的作品。
这是导师对您的孩子作出的评价：{teacherComment}"""
        elif reasonFilling == "学生获奖/录取/荣誉反馈":
            awardType = info["awardType"]
            if awardType == "竞赛获奖":
                template = \
"""{studentName}家长您好，您的孩子在{competitionName}中获得了{prizeReceived}的成绩！这是获奖证明{awardEvidence}
这是您孩子所做的项目：{projectDescription}
这是{teacherName}导师对您孩子的评语：{teacherNotes}"""
            elif awardType == "项目发布":
                template = \
"""{studentName}家长您好，您的孩子发布了自己的项目{projectLink}！这是项目发布证明{projectPublishEvidence}
这是您孩子所做的项目：{projectDescription}
这是{teacherName}导师对您孩子的评语：{teacherNotes}"""
            elif awardType == "名校录取":
                template = \
"""{studentName}家长您好，您的孩子被{schoolName}的{profession}录取了！这是录取通知书{admissionEvidence}
这是{teacherName}导师对您孩子的评语：{teacherNotes}"""
            elif awardType == "著作权":
                template = \
"""{studentName}家长您好，您的孩子申请著作权成功了！这是登记证书{copyrightEvidence}
这是您孩子项目的截图：{projectScreenshot}
这是{teacherName}导师对您孩子的评语：{teacherNotes}"""
            else:
                return ""
        else:
            return ""

        return template.format(**info)



    @staticmethod
    def genMessage(id):
        info = BiggerlabCourseFeedback.col.find({"_id": id})[0]

        #message = BiggerlabCourseFeedback.messageTemplates[info["reasonFilling"]].format(**info)
        message = BiggerlabCourseFeedback.messageTemplatesTmp(**info)
        return message


    @staticmethod
    @bp.route("/sendToWechat", methods=["POST"])
    def sendToWechat():
        raise NotImplementedError
        if not request.is_json:
            return make_response(("Data is not a json, rejecting.", 400))
        id = request.json.get("id", None)

        bots = utils.getActiveBots(main.app.config["WECHATBOTSERVER"])
        if not bots:
            return make_response(("There are no bots alive.", 403))
        
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
