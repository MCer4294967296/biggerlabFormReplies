class CourseFeedback():
    templates = {
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
    def message(info):
        if info["reasonFilling"] not in CourseFeedback.templates.keys():
            return # it was "other"

        message = CourseFeedback.templates[info["reasonFilling"]].format(
            teacherName = info["teacherName"],
            teacherComment = info["teacherComment"],
            studentName = info["studentName"],
            courseName = info["courseName"],
            courseStartDate = info["courseStartDate"],
            courseEndDate = info["courseEndDate"],
            courseContent = info["courseContent"],
            courseCapturelink = info["courseCapturelink"],
            projectScreenshot = info["projectScreenshot"],
            rateAttendance = info["rateAttendance"],
            rateUnderstanding = info["rateUnderstanding"],
            rateAssignmentCompletion = info["rateAssignmentCompletion"],
            rateGeneral = info["rateGeneral"],
            reasonChanging = info["reasonChanging"],
            nextTeacher = info["nextTeacher"],
            classType = info["classType"],
            classStartTime = info["classStartTime"],
            classEndTime = info["classEndTime"],
            hoursTaught = info["hoursTaught"],
            awardReceived = info["awardReceived"],
            awardType = info["awardType"],
            projectDescription = info["projectDescription"],
            teacherNotes = info["teacherNotes"],
            awardEvidence = info["awardEvidence"],
            competitionName = info["competitionName"],
            prizeReceived = info["prizeReceived"],
            projectPublishEvidence = info["projectPublishEvidence"],
            copyrightEvidence = info["copyrightEvidence"],
            projectLink = info["projectLink"],
            sourceCode = info["sourceCode"],
            admissionEvidence = info["admissionEvidence"],
            schoolName = info["schoolName"],
            profession = info["profession"],
            awardOthers = info["awardOthers"])
        return message
        

translation = {
    "BiggerlabCourseFeedback" : CourseFeedback.message
}