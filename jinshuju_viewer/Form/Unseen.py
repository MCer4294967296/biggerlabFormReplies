import functools
from flask import (
    Blueprint, flash, g, jsonify, make_response, redirect, render_template, request, session, url_for
)
from .. import form, main, utils


class Unseen(form.Form):

    app = main.app
    db = main.db
    unseenForms = db["UnseenForms"]
    
    @staticmethod
    @app.route("/jinshujuIN", methods=["POST"])
    def jinshujuIN():        
        if not request.is_json:
            #logging.warning("/jinshujuIN received non-json data.")
            return make_response(("Data is not a json, rejecting.", 400))

        jsonObj = json.loads(json.dumps(request.json, ensure_ascii=False))    

        # formNameTranslation.translation[jsonObj["form"]] # get the unique form name
        form = jsonObj["form"]
        
        if len(Unseen.unseenForms.find_one({"form": form})) == 0:
            Form.unseenForms.insert_one({"form": form, "formName": jsonObj["form_name"]})

        id = int(jsonObj["entry"]["serial_number"])

        rawInfo = jsonObj["entry"]
        rawInfo.update({"jsjid" : id})

        col = Unseen.db[form]

        try:
            col.insert_one(rawInfo) # try inserting,
        except pymongo.errors.DuplicateKeyError: # if duplicate,
            return make_response(("Duplicate Key", 400)) # then err out;
            # we can also do a query instead of trying to insert, # TODO

        mInfo = Form.mParse(rawInfo)

        mCol = Unseen.db["meta" + form]

        try:
            mCol.insert_one(metaInfo) # try inserting,
        except pymongo.errors.DuplicateKeyError: # if duplicate,
            return make_response(("Duplicate Key", 400)) # then err out;

        return make_response(("Document saved.", 200)) # otherwise we are good


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
                #logging.warning("/getPage received an invalid id range.")
                return make_response(("id is not valid.", 400))
        #logging.info("Page requested.")
        col = Unseen.db[form]
        docs = col.find()
        chosen, prevID, nextID = utils.getIDList(docs, idStart=idStart, idEnd=idEnd, key="jsjid")
        return render_template()

    
    @staticmethod
    @app.route("/<form>/getDoc", methods=["GET"])
    def getDoc(form):
        '''This method queries the database and returns the related
        information according to the id.
        '''
        id = int(request.args.get("id"))
        col = Unseen.db[form]
        info = col.find({"jsjid": id})[0]
        #logging.info("Information requested.")
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

