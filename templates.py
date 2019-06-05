def courseFeedbackMessage(info):
    try:
        message = \
        u"""{}家长您好，导师{}对您的孩子于{}开始的{}作出了月度课程反馈。
        课堂参与度：{}
        知识点理解情况：{}
        课堂任务完成情况：{}
        综合：{}
        您可以点击{}来查看您的孩子的项目进展。
        这是您的孩子最近正在学的课程内容：{}
        这是导师对您的孩子作出的评价：{}""".format(
        info["studentName"], info["teacherName"], info["courseStartDate"], info["courseName"],
        info["rateAttendance"],
        info["rateUnderstanding"],
        info["rateAssignmentCompletion"],
        info["rateGeneral"],
        info["projScreenshot"],
        info["studentLearnt"],
        info["teacherComment"])
    except KeyError:
        pass
    return message