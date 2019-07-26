## 金数据微信推送平台
## [源码链接 source code](https://drive.google.com/open?id=1V6MtCsigzePHRqEnqRMddcCZLVVWbs5i)


### Background
The functionality wanted is to notify a child’s parents of a teacher making a comment on a course that the child took.

The existing solution is to use the built-in notification functionality of 金数据 to send a phone message with a link to a 金数据 page, where one can fill in the name of a student and see what comment has been made.

The problems with the existing solution is that the parents have to
1. check phone messages, which might be a little bit spammy.
2. click on a link, and fill in the same-for-everyone auth on the webpage, then enter the student name.

The desired solution is to push messages directly to a parents’ or a group chat.

### External Libraries Used
* [Bootstrap](https://getbootstrap.com/docs/4.3/getting-started/introduction/), to build our ugly frontend page;
* [Flask](http://flask.pocoo.org/docs/1.0/api/) with python3, as our backend server;
* MongoDB with [pymongo](http://api.mongodb.com/python/current/api/pymongo/index.html), as our database;
* ~~[itchat](https://itchat.readthedocs.io/zh/latest/), as the interface with web wechat;~~
* A separate proxy wechat bot server;


### How to Deploy
1. Download the source directory, open it in terminal, and do  
    `make`  
   Alternatively, if you do not have make installed, you can do  
    `vendor/venv-update venv= -ppython3 venv install= -r requirements.txt`  
   This will install the required dependency under the directory venv.
2. You can then do  
    `source .activate.sh`  
   to activate the virtual environment.
3. After this, you should configure the depended server location specified in  
    `jinshuju_viewer/config.py`
4. After this, you can safely start the server, do  
    `flask run --host *host* --port *port*`  
   This will start a server listening on *host* port *port*.


### Data Flow
#### Influx
By specifying a webhook for every form we want to view on jinshuju, jinshuju will send an HTTP POST when a new record is filed. The flask route for this should be `*/jinshujuIN`.  
The server, on receiving a new record, will save the record to the database as specified in `jinshuju_viewer/config.py`, with appropriate meta information saved as well.

#### Outflux
Users can visit the site with a web browser and view any forms that has ever had a document in the database. A user can also send messages via wechat in those allowed forms.  
On user request, the server will send an HTTP request to the wechat bot server, providing the nickname and remark name of the target contact, and the wechat bot server will do its job.


### Project Structure
`./run.py`  
The script that can start the server. The proper way though, is still via `flask run`.

`./Makefile, ./requirements.py, ./vendor/venv-update`  
The files that deploys the server.

`./jinshuju_viewer/`  
The directory that most codes live.

`./jinshuju_viewer/__init__.py, ./jinshuju_viewer/config.py`  
The module init file, and the server config file.

`./jinshuju_viewer/utils.py`  
Some functions that makes our lives easier.

`./jinshuju_viewer/form.py`  
The file that defines several abstract form classes. One should not directly instantiate an object of these classes. *(Even if you do, you can’t really do anything with that.)*

`./jinshuju_viewer/main.py`  
The file that actually initiates the application. Setup the app, the database, register all the various routes.

`./jinshuju_viewer/static/*`  
The directory where static files lie.

`./jinshuju_viewer/templates/`  
The directory where jinja template files that get rendered as web pages lie.

`./jinshuju_viewer/templates/base.html`  
The base abstract template, vendor css and js are imported here. There are two blocks that can be extended - `{% block body %}` and `{% block script %}`.

`./jinshuju_viewer/templates/index.html`  
The home page template.

`./jinshuju_viewer/templates/wechatted.html`  
The wechatted abstract template. The wechat contact list is defined here in `{% block wechatList %}`, and a whole bunch of functions.

`./jinshuju_viewer/templates/Form/*`  
The directory where various defined form templates live.

`./jinshuju_viewer/Form/*`  
The directory where various defined form backends live. Every one of these files will define a class and extend one of the abstract classes defined in `./jinshuju_viewer/form.py`.  
The reason why that `form.py` is not in this directory is that I spent so long trying to figure out how to import it from other scripts and still I failed so I gave up.


### Specifications for Existing Flask Routes:
`/jinshujuIN`   
```
Defined in: ./Form/Unseen.py
Accepted methods: POST  
Accepted data carrier: JSON  
Expected format:
{
    "form": string, // "hopuFU"
    "form_name": string, // "BiggerlabCourseFeedback"
    "entry": {
        "serial_number": int, // 381
    },
}
Returns:
    200, if successfully saved;
    400, if data is not a json;
```
This is where data of general forms, those that do not have a corresponding class file, will go. This is built as per the specifications of jinshuju. The method will put records from different forms into different collections in the database, not changing anything apart from attaching a `jsjid` key to the record. Meta information is also saved, although it's basically no information at all.  
*Note that this method will not return a 400 because of a duplication key error, since we did not specify the `_id` key in the data.*

`/<form>`
```
Defined in: ./Form/Unseen.py
Accepted methods: GET
Accepted data carrier: URL args
Expected format:
    args["idStart"]: optional string // "381"
    args["idEnd"]: optional string // "381"
Returns:
    An html page.
```
This is the viewer's page of general forms. If one of the two id range limiters are defined, we get 10 documents that's closest to the boundary; if both of them are defined, we get everything that's within the range; if neither are defined, we get the 10 last documents.  
It's currently not implemented.

`/<form>/getDoc`
```
Defined in: ./Form/Unseen.py
Accepted methods: GET
Accepted data carrier: URL args
Expected format:
    args["id"]: string // "381"
    args["key"]: optional string // "jsjid"
Returns:
    A json that includes the raw data.
```
This method gets the document with the specified id from the specified form in the database.

`/BiggerlabCourseFeedback`
```
Defined in: ./Form/BiggerlabCourseFeedback.py
Accepted Methods: GET
Accepted data carrier: URL args
Expected format:
    args["idStart"]: optional string
    args["idEnd"]: optional string
Returns:
    200 and an html page, if succeed;
    400, if an invalid id range limiter is provided;
```
This is a specified version of `/<form>`. It has the same id range limiters behavior as specified for`/<form>`. It renders the template `./templates/Form/BiggerlabCourseFeedback.html`.


`/BiggerlabCourseFeedback/jinshujuIN`
```
Defined in: ./Form/BiggerlabCourseFeedback.py
Accepted methods: POST  
Accepted data carrier: JSON  
Expected format:
{
    "form": string, // "hopuFU"
    "form_name": string, // "BiggerlabCourseFeedback"
    "entry": {
        "serial_number": int, // 381
        // And all other information as specified in the parser.
    },
}
Returns:
    200, if successfully saved;
    400, if the request is not a json;
    400, if there is duplication in key when inserting into main db;
```
This is a specified version of `/jinshujuIN`. This parses out the raw information from jinshuju as defined in the parse method. It also sets the meta information.  
*Note that this form will set the `_id` key of the document that goes into the db, and therefore it can actually throw a duplicate key error.*

`/BiggerlabCourseFeedback/getDoc`
```
Defined in: ./Form/BiggerlabCourseFeedback.py
Accepted methods: GET
Accepted data carrier: URL args
Expected format:
    args["id"]: string // "381"
Returns: JSON
{
    "id": int, // 381
    "message": string, // "Hello, world"
    "studentName": string, // "Billy"
    "teacherName": string, // "Rock"
    "reasonFilling": string, // "月度课程反馈，给家长"
    "messageEdited": bool, // False
}
```
This method gets the document with the specified id from the specified form in the database.

`/BiggerlabCourseFeedback/sendToWechat`
```
Defined in: ./Form/BiggerlabCourseFeedback.py
Accepted methods: POST
Accepted data carrier: JSON
Expected format:
{
    "id": optional string, // "381"
    "targetList": list, // ["Rock || 大石头", " || 我", "一个群组"]
    "message": string, // "Hello World!"
}
Returns:
    200, if message is successfully sent to every target;
    400, if the request is not a json;
    400, if the json does not meet the expected format;
    403, if there are no wechat bots alive;
    500, if the upstream wechat bot server encountered some problems and not all messages are successfully sent.
```
This method does the send to wechat work. It parses out each target using the separator that's added on the frontend. If `id` is provided, modify the `sentToWechat` key of the corresponding meta document as well.  
*TODO: do not use the separator at all.* 


### Specifications for Existing Mongo Collections:
#### _All information about main keys is talking apart from the default `_id` key of Mongodb._
`BiggerlabCourseFeedback`  
The collection storing information of the form __Biggerlab 课程反馈表__ (form id: 34dBQf).  
Main key: None. `_id` is the same as `serial_number` when jinshuju pushed.  
*TODO: change this to `jsjid` and leave `_id` as default.*
Captured information: all.

`metaBiggerlabCourseFeedback`  
The collection storing meta information of the form __Biggerlab 课程反馈表__ (form id: 34dBQf).  
Main key: `jsjid`, the same as `serial_number`  
Captured information:
* the generated message
* whether the message related to the entry is sent to wechat
* whether the message is ever edited after it's generated (not used)
* whether the message is viewed (not used)
* when the data is pushed from jinshuju  
  *TODO: change this to rawInfo["created_at"].*


### Known Issues:
* When creating a list from a pyMongo.cursor object, it sometimes errors. This is currently worked around by manually
  iterating through the cursor and append to the list - an imaginable drop in efficiency.
* Now the main keys are default to `jsjid`, which leave the `_id` field default, which is
  not serializable by json and need to exclude that field whenever a whole database document
  is sent. Thus the database needs more designing.

### Future Seeable Improvements:
* Somehow use json to specify parser for forms, so as to be able to hot reload the server.
* Store information about forms into the database. For example, the main key.
* Use single-instance mode and not purely static stuff. I don't know how flask routes will
  work with that. Doing that has the advantage of not specifying the classname when we 
  want to refer to static stuff like `col` and `mCol`.
* I'm thinking about use purely query-like arguments as routes - `/getPage?form=hopuFU`
  or something similar in JSON. Since it looks like there aren't much difference between
  forms apart from the parser and meta parser. This will have the advantage of less repeated codes.