def parseBiggerlabCourseFeedback(blob):
    ret = {}

    ret["Form Type"] = "Biggerlab Course Feedback"
    
    ret["teacherName"] = blob["field_4"]
    ret["teacherComment"] = blob["field_19"]

    ret["courseName"] = blob["field_8"]
    ret["courseStartDate"] = blob["field_9"]
    ret["courseCapturelink"] = blob["field_32"]

    ret["studentName"] = blob["field_6"] + blob["field_31"]
    ret["studentLearnt"] = blob["field_13"]

    ret["rateAttendance"] = blob["field_14"]
    ret["rateUnderstanding"] = blob["field_15"]
    ret["rateAssignmentCompletion"] = blob["field_16"]
    ret["rateGeneral"] = blob["field_17"]

    ret["projScreenshot"] = blob["field_18"]

    return ret