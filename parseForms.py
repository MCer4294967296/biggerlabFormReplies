from shortener import shorten

def parseBiggerlabCourseFeedback(blob):

    def deDownload(linkArr):
        return "" if len(linkArr) == 0 else (linkArr[0][:-9] if linkArr[0].endswith("&download") else linkArr[0])
    # 有些link最后会带一个"&download" 这会导致它默认下载而不是预览，所以我们扔掉它。

    info = {}

    info["reasonFilling"] = blob["field_5"] # 填表原因

    info["teacherName"] = blob["field_4"] # 导师姓名
    info["teacherComment"] = blob["field_19"] # 导师评价

    info["studentName"] = blob["field_6"] + blob["field_31"] # 学生姓名

    info["courseName"] = blob["field_8"] # 课程名
    info["courseStartDate"] = blob["field_9"] # 课程开始日期
    info["courseEndDate"] = blob["field_12"] # 课程结束日期
    info["courseContent"] = blob["field_13"] # 已上课程内容
    info["courseCapturelink"] = blob["field_32"] # 课程视频链接
    info["projectScreenshot"] = shorten(deDownload(blob["field_18"])) # 项目作品截图

    info["rateAttendance"] = blob["field_14"] # 学生课堂参与度
    info["rateUnderstanding"] = blob["field_15"] # 知识点理解情况
    info["rateAssignmentCompletion"] = blob["field_16"] # 课堂任务完成情况
    info["rateGeneral"] = blob["field_17"] # 综合评价

    info["reasonChanging"] = blob["field_20"] # 交接原因
    info["nextTeacher"] = blob["field_21"] # 接手导师姓名
    info["classType"] = blob["field_23"] # 上课形式
    info["classStartTime"] = blob["field_10"] # 上课时间
    info["classEndTime"] = blob["field_11"] # 下课时间
    info["hoursTaught"] = blob["field_25"] # 已上课时数

    info["awardReceived"] = blob["field_33"] # 学生是否获得相应荣誉
    info["awardType"] = blob["field_37"] # 荣誉类型
    info["projectDescription"] = blob["field_42"] # 学生项目描述/所学内容
    info["teacherNotes"] = blob["field_46"] # 导师对该学生的评语

    info["awardEvidence"] = shorten(deDownload(blob["field_40"])) # 竞赛获奖证明截图
    info["competitionName"] = blob["field_34"] # 比赛名称
    info["prizeReceived"] = blob["field_35"] # 获得的奖项

    info["projectPublishEvidence"] = shorten(deDownload(blob["field_47"])) # 项目发布证明截图
    info["copyrightEvidence"] = shorten(deDownload(blob["field_48"])) # 著作权证明截图
    info["projectLink"] = blob["field_43"] # 项目链接
    info["sourceCode"] = shorten(deDownload(blob["field_36"])) # 源代码文件

    info["admissionEvidence"] = shorten(deDownload(blob["field_49"])) # 名校录取证明截图
    info["schoolName"] = blob["field_44"] # 学校名称
    info["profession"] = blob["field_45"] # 专业名称

    info["awardOthers"] = shorten(deDownload(blob["field_50"])) # 其他荣誉证明截图
    return info

translation = {
    "BiggerlabCourseFeedback" : parseBiggerlabCourseFeedback
}