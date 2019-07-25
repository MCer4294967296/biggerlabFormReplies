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

        for doc in chosen:
            del doc["_id"]

        chosen = chosen[offset:count+offset]
        return jsonify(chosen)

    
    @staticmethod
    def parse(rawInfo):

        info = {}

        info["jsjid"] = rawInfo["serial_number"]

        info["teacherName"] = rawInfo["field_23"] # 导师姓名
        info["teacherRole"] = rawInfo["field_1"] # 导师角色
        info["teacherPhone"] = rawInfo["field_20"] # 导师手机

        info["studentName"] = rawInfo["field_63"] # 学生姓名
        info["projectType"] = rawInfo["field_6"] # 项目类型
        
        info["submissionCategory"] = rawInfo["field_31"] # 提交类型 # array

        # 提交类型 为 导师技术Demo提交
        info["teacherTechDemoLink"] = rawInfo["field_64"] # 导师技术Demo提交链接
        info["teacherDemoVideo"] = rawInfo["field_37"] # 导师Demo展示视频 # array

        # 提交类型 为 课时提交Course Time Submission
        info["projectStage"] = rawInfo["field_39"] # 项目阶段Stage Of the Project
        info["projectStageCompletion"] = rawInfo["field_28"] # 当前阶段完成进度（%）Stage Completion
        info["dateEventHappened"] = rawInfo["field_3"] # 发生日期 Date the event happened
        info["sessionStartTime"] = rawInfo["field_4"] # 辅导开始时间 Session started at
        info["sessionEndTime"] = rawInfo["field_24"] # 辅导结束时间 Session ended at
        info["sessionSummary"] = rawInfo["field_8"] # 本次辅导小结 Summary of the session
        info["sessionRelatedFiles"] = rawInfo["field_10"] # 上传辅导相关文件 Please upload related files here # array
        info["documentationLink"] = rawInfo["field_43"] # 学生博客链接 Link to student's documentation blog
        info["ifStudentHasHomework"] = rawInfo["field_46"] # 有无学生课后作业？
        info["ifteacherFinishedTeaching"] = rawInfo["field_47"] # 该导师授课内容是否完结？

        # 提交类型 为 头脑风暴文档验收Brainstorm Document Submission
        # info["projectStage"] = rawInfo["field_39"] # 项目阶段Stage Of the Project
        # info["projectStageCompletion"] = rawInfo["field_28"] # 当前阶段完成进度（%）Stage Completion
        # info["dateEventHappened"] = rawInfo["field_3"] # 发生日期 Date the event happened
        info["brainstormDocument"] = rawInfo["field_38"] # 头脑风暴文档 Brainstorm Document # array
        info["endOfMentorshipSummary"] = rawInfo["field_12"] # 导师阶段性结课内容总结 End-of-mentorship summary
        info["endOfMentorshipFeedback"] = rawInfo["field_11"] # 导师阶段性结课学生评价 End-of-mentorship feedback of the student
        # info["ifteacherFinishedTeaching"] = rawInfo["field_47"] # 该导师授课内容是否完结？

        # 提交类型 为 项目文档验收Project Document Submissions
        # info["projectStage"] = rawInfo["field_39"] # 项目阶段Stage Of the Project
        # info["projectStageCompletion"] = rawInfo["field_28"] # 当前阶段完成进度（%）Stage Completion
        # info["dateEventHappened"] = rawInfo["field_3"] # 发生日期 Date the event happened
        info["projectDocument"] = rawInfo["field_34"] # 项目文档 Project Document # array
        # info["endOfMentorshipSummary"] = rawInfo["field_12"] # 导师阶段性结课内容总结 End-of-mentorship summary
        # info["endOfMentorshipFeedback"] = rawInfo["field_11"] # 导师阶段性结课学生评价 End-of-mentorship feedback of the student
        info["studentDocumentationBlogLink"] = rawInfo["field_43"] # 学生博客链接 Link to student's documentation blog
        # info["ifStudentHasHomework"] = rawInfo["field_46"] # 有无学生课后作业？
        # info["ifteacherFinishedTeaching"] = rawInfo["field_47"] # 该导师授课内容是否完结？

        # 提交类型 为 学生技术实现阶段性汇报Technical Realization Stage Report
        # info["projectStage"] = rawInfo["field_39"] # 项目阶段Stage Of the Project
        # info["projectStageCompletion"] = rawInfo["field_28"] # 当前阶段完成进度（%）Stage Completion
        # info["dateEventHappened"] = rawInfo["field_3"] # 发生日期 Date the event happened
        info["completedFunctionsDescription"] = rawInfo["field_40"] # 完成功能描述Description of Functions Completed
        info["githubRepoLink"] = rawInfo["field_53"] # 项目目录链接 Link to Github Repo
        # info["teacherDemoVideo"] = rawInfo["field_37"] # 导师Demo展示视频
        # info["studentDocumentationBlogLink"] = rawInfo["field_43"] # 学生博客链接 Link to student's documentation blog
        # info["ifStudentHasHomework"] = rawInfo["field_46"] # 有无学生课后作业？

        # 提交类型 为 项目发布验收(项目完结)Project Publication(End of Project)
        # info["projectStage"] = rawInfo["field_39"] # 项目阶段Stage Of the Project
        # info["projectStageCompletion"] = rawInfo["field_28"] # 当前阶段完成进度（%）Stage Completion
        # info["dateEventHappened"] = rawInfo["field_3"] # 发生日期 Date the event happened
        # info["endOfMentorshipSummary"] = rawInfo["field_12"] # 导师阶段性结课内容总结 End-of-mentorship summary
        # info["endOfMentorshipFeedback"] = rawInfo["field_11"] # 导师阶段性结课学生评价 End-of-mentorship feedback of the student
        # info["teacherDemoVideo"] = rawInfo["field_37"] # 导师Demo展示视频
        info["publishedPageLink"] = rawInfo["field_36"] # 发布链接Link to Published Page
        # info["studentDocumentationBlogLink"] = rawInfo["field_43"] # 学生博客链接 Link to student's documentation blog
        # info["ifStudentHasHomework"] = rawInfo["field_46"] # 有无学生课后作业？
        # info["ifteacherFinishedTeaching"] = rawInfo["field_47"] # 该导师授课内容是否完结？

        # 提交类型 为 学生情况反馈（当学生出现问题时填写）Student Feedback (When the student fail to meet expectations)
        info["problemsEncountered"] = rawInfo["field_13"] # 本次学生辅导项目当前情况以及出现的问题 Current project status and problems encountered

        # 有无作业 为 有
        info["homeworkName"] = rawInfo["field_66"] # 学生作业名称
        info["homeworkList"] = rawInfo["field_9"] # 学生课后作业 Student's to-do list after the session:
        info["homeworkETF"] = rawInfo["field_26"] # 作业预计完成时间Estimate Time to finish to-do tasks:
        info["homeworkDDL"] = rawInfo["field_67"] # 作业截止日期
        info["homeworkDDLOther"] = rawInfo["field_68"] # 作业截止日期(其他)

        # 授课完结 为 否
        info["nextSessionDate"] = rawInfo["field_32"] # 下次课程日期Date for the next session
        info["nextSessionTime"] = rawInfo["field_35"] # 下次课程时间Schedule Time for the next session
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
        raise NotImplementedError
        

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
