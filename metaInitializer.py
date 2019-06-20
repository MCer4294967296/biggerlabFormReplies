def parseBiggerlabCourseFeedback(blob):
    meta = {}
    
    meta["sentToWechat"] = False
    meta["message"] = ""
    meta["edited"] = False

    return meta
    

translation = {
    "BiggerlabCourseFeedback" : parseBiggerlabCourseFeedback
}