from flask import (
    Blueprint, flash, g, redirect, render_template, request, session, url_for
)
from wechat_autoreply import app, db, utils

class Form():

    unseenForms = db["UnseenForms"]
    
    @staticmethod
    @app.route("/jinshujuIN", methods=["POST"])
    def jinshujuIN():
        '''Processes what jinshuju posts to the server via webhook.
        This one is specifically for those forms that are either
        generic or not defined within our program.
        '''
        
        if not request.is_json:
        logging.warning("/jinshujuIN received non-json data.")
        return "400 BAD REQUEST: Data is not a json, rejecting.", 400

        jsonObj = json.loads(json.dumps(request.json, ensure_ascii=False))    

        # formNameTranslation.translation[jsonObj["form"]] # get the unique form name
        form = jsonObj["form"]
        
        if len(Form.ununseenForms.find_one({"form": form})) == 0:
            Form.unseenForms.insert_one({"form": form, "formName": jsonObj["form_name"]})

        id = int(jsonObj["entry"]["serial_number"])

        rawInfo = jsonObj["entry"]
        rawInfo.update({"jsjid" : id})

        col = db[form]

        try:
            col.insert_one(rawInfo) # try inserting,
        except pymongo.errors.DuplicateKeyError: # if duplicate,
            return "400 you fked up: Duplicate Key", 400 # then err out;
            # we can also do a query instead of trying to insert, # TODO

        mInfo = Form.mParse(rawInfo)
        # jinshuju id, this is probably not the main key, so we don't use "_id"

        mCol = db["meta" + form]

        try:
            mCol.insert_one(metaInfo) # try inserting,
        except pymongo.errors.DuplicateKeyError: # if duplicate,
            return "400 you fked up: Duplicate Key", 400 # then err out;

        return "200 OK", 200 # otherwise we are good


    @staticmethod
    @app.route("/<form>", methods=["GET"])
    def getPage(form):
        '''This method renders The main page where you
        will view the information about the whole
        collection, as well as a list of entries.
        This one is specifically for those forms that are either
        generic or not defined within our program.
        '''
        idStart = request.args.get("idStart")
        idEnd = request.args.get("idEnd")
        if idStart or idEnd:
            try:
                idEnd = int(idEnd) if idEnd else None
                idStart = int(idStart) if idStart else None
            except:
                logging.warning("/getPage received an invalid id range.")
                return "400 BAD REQUEST: id is not valid.", 400
        logging.info("Page requested.")
        col = db[form]
        docs = col.find()
        chosen, prevID, nextID = getIDList(docs, idStart=idStart, idEnd=idEnd)

    
    @staticmethod
    @app.route("/<form>/getDoc", methods=["GET"])
    def getDoc(form):
        '''This method queries the database and returns the related
        information according to the id.
        '''
        id = int(request.args.get("id"))
        col = db[form]
        info = col.find({"jsjid": id})[0]
        logging.info("Information requested.")
        return jsonify(info)

    
    @staticmethod
    def mParse(rawInfo):
        '''This is a method that makes the initial metaInfo to
        insert into the meta database.
        '''
        mInfo = {}

        mInfo["jsjid"] = rawInfo["serial_number"]
        mInfo["viewed"] = False

        return mInfo


class ParsedForm(Form):

    @staticmethod
    def parse(rawInfo):
        '''This is a method that parses out jinshuju nonsense data blob.
        From the original "field_1" to meaningful names like "studentName"
        '''
        raise NotImplementedError
    


class ToWechatForm(ParsedForm):

    @staticmethod
    def genMessage(info):
        '''Since this is a class where documents are destined for a wechat
        dialogue, it's very likely that a default message can be automatically
        generated from the document.'''
        raise NotImplementedError

    
    @staticmethod
    def sendToWechat():
        '''this method calls the configured wechat server.'''
        raise NotImplementedError