import functools

from flask import (Blueprint, flash, g, jsonify, make_response, redirect,
                   render_template, request, session, url_for)

from .. import form, main, utils


class Unseen(form.Form):

    app = main.app
    db = main.db
    unseenForms = db["UnseenForms"]
    
    @staticmethod
    @app.route("/jinshujuIN", methods=["POST"])
    def jinshujuIN():
        '''The handler of data from jinshuju.
        :returns: A helpful message and a status code.
        '''
        if not request.is_json:
            return make_response(("Data is not a json, rejecting.", 400))

        jsonObj = json.loads(json.dumps(request.json, ensure_ascii=False))

        form = jsonObj["form"] # get the form id
        
        if len(Unseen.unseenForms.find_one({"form": form})) == 0: # if we haven't seen this form before,
            Unseen.unseenForms.insert_one({"form": form, "formName": jsonObj["form_name"]}) # we 

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
        '''The renderer of the viewer page of general forms
        :params form: the form name.
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
        return render_template("Form/Unseen.html")

    
    @staticmethod
    @app.route("/<form>/getDoc", methods=["GET"])
    def getDoc(form):
        '''This method queries the database and finds one document that matches the id.
        :params form: the form name;
        :returns: the information as a json.
        '''
        id = int(request.args["id"])
        key = request.args.get("key", "jsjid")
        col = Unseen.db[form]
        info = col.find({key: id})[0]
        #logging.info("Information requested.")
        return jsonify(info)

    
    @staticmethod
    def mParse(rawInfo):
        '''This is a method that makes the initial metaInfo to
        insert into the meta database.
        :params rawInfo: a dict that should include a key "serial_number";
        :returns: the initial meta infomation as a dict.
        '''
        mInfo = {}

        mInfo["jsjid"] = rawInfo["serial_number"]
        mInfo["viewed"] = False

        return mInfo
