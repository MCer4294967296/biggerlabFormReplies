import os, requests, sys
import itchat, pymongo


def shorten(URL):
    if URL == "":
        return ""

    service = "https://tinyurl.com/api-create.php"
    return requests.get(url=service, params={"url" : URL}).text


def getIDList(docs, count=10, idStart=None, idEnd=None, key="_id"):
    '''returns a list of documents with the provided ID range and count,
    as well as the previous and next possible ID that's outside of the returned
    range. If there are no more, None is returned. '''

    if idStart or idEnd:
        try:
            idEnd = int(idEnd) if idEnd else None
            idStart = int(idStart) if idStart else None
        except:
            return []

    chosen = []
    if idStart and idEnd:
        chosen = list(docs.where("this['{key}'] >= {idStart} && this['{key}'] <= {idEnd}").format(idStart=idStart, idEnd=idEnd, key=key).sort(key, pymongo.DESCENDING))
        prevID = idStart - 1
        nextID = idEnd + 1
    elif idStart:
        match = list(docs.where("this['{key}'] >= {idStart}".format(idStart=idStart, key=key)).sort(key, pymongo.DESCENDING))
        chosen = match[-count:]
        prevID = idStart - 1
        nextID = chosen[0][key] + 1 if len(match) > count else None
        if count <= 0:
            chosen = match
            nextID = None
    elif idEnd:
        match = list(docs.where("this['{key}'] <= {idEnd}".format(idEnd=idEnd, key=key)).sort(key, pymongo.DESCENDING))
        chosen = match[:count]
        prevID = chosen[-1][key] - 1 if len(match) > count else None
        nextID = idEnd + 1
        if count <= 0:
            chosen = match
            prevID = None
    else:
        match = list(docs.sort(key, pymongo.DESCENDING))
        chosen = match[:count]
        prevID = chosen[-1][key] - 1 if len(match) > count else None
        nextID = None

    return chosen, prevID, nextID

def handlerSIGINT(signal, frame):
    itchat.logout()
    try:
        os.remove("static/wechatStuff/loggingIn.png")
    except FileNotFoundError:
        pass

    try:
        os.remove("QR.png")
    except FileNotFoundError:
        pass
    sys.exit(0)