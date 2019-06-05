def parseBiggerlabCourseFeedback(blob):
    info = {}
    
    info["teacherName"] = blob["field_4"]
    info["teacherComment"] = blob["field_19"]

    info["courseName"] = blob["field_8"]
    info["courseStartDate"] = blob["field_9"]
    info["courseCapturelink"] = blob["field_32"]

    info["studentName"] = blob["field_6"] + blob["field_31"]
    info["studentLearnt"] = blob["field_13"]

    info["rateAttendance"] = blob["field_14"]
    info["rateUnderstanding"] = blob["field_15"]
    info["rateAssignmentCompletion"] = blob["field_16"]
    info["rateGeneral"] = blob["field_17"]

    info["projScreenshot"] = blob["field_18"]

    info["sentToWechat"] = False
    return info

translation = {
    "biggerlab course feedback" : parseBiggerlabCourseFeedback
}