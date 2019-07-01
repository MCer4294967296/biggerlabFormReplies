class Form():
    
    @staticmethod
    def jinshujuIN():
        '''Processes what jinshuju posts to the server via webhook.
        This one is specifically for those forms that are either
        generic or not defined within our program.
        '''
        raise NotImplementedError


    @staticmethod
    def getPage(form):
        '''This method renders The main page where you
        will view the information about the whole
        collection, as well as a list of entries.
        This one is specifically for those forms that are either
        generic or not defined within our program.
        '''
        raise NotImplementedError
    
    @staticmethod
    def getDoc(form):
        '''This method queries the database and returns the related
        information according to the id.
        '''
        raise NotImplementedError

    
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