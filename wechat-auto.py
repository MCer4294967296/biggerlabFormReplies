# coding:utf-8
import sys
import time
import re
import json
from flask import Flask, abort, request, render_template
from parseForms import *
from templates import *
import itchat
from itchat.content import *

lc = lambda : print("Login Successful.")
ec = lambda : print("Logout Successful.")

def getroom_message(n):
    #获取群的username，对群成员进行分析需要用到
    itchat.dump_login_status() # 显示所有的群聊信息，默认是返回保存到通讯录中的群聊
    RoomList =  itchat.search_chatrooms(name=n)
    if RoomList:
        return RoomList[0]['UserName']
    else:
        print("%s group is not found!" % (name))

app = Flask(__name__)
@app.route('/jinshujuIN', methods=['POST'])
def jinshujuIN():
    if not request.is_json:
        abort(400)
        print("Data is not a json, rejecting.")

    entry = json.loads(json.dumps(request.json, ensure_ascii=False))['entry']
    
    # linux如何实现登陆
    # qr_path = 'static/QR.png'
    # bot = Bot(console_qr=True, cache_path=True)
    # 群组不活跃的情况下，群组搜索出错。
    # 群组test只有一个群的时候，搜索出错。
    # 群组搜索下如何命名微信群
    # target_group = bot.groups(update=True, contact_only=False).search('test')[0]
    #itchat.auto_login(hotReload=True, loginCallback=lc, exitCallback=ec, enableCmdQR=2)
    #itchat.run()
    parser = parseBiggerlabCourseFeedback
    info = parser(entry)
    template = courseFeedbackMessage
    message = template(info)
    
    itchat.send_msg(msg=message, toUserName="filehelper")
    #itchat.send_msg(msg=entry, toUserName="filehelper")
    #itchat.send_msg(msg=message, toUserName=itchat.search_friends(name="Rock大石头")[0]["UserName"])
    #itchat.send_msg(msg=[], toUserName="filehelper")
    return "ahhh it's not okay"
    return "200 OK", 200
    #提交类型判断需有修改,当前只有Course Time Submission后执行推送
    """
    submitTypes = ['Course Time Submission','Brainstorm Document Submission','Project Document Submission','Technical Realization Stage Report','Project Publication(End of Project)']
    
    for data in datas:
        pass
        #print data
        for submitType in submitTypes:
            #print submitType
            if(submitType in data):
                studentName = beforeSend['field_2']
                teacherJob = beforeSend['field_1']
                teacherName = beforeSend['field_23']
                teachDate = beforeSend['field_3']
                teachStart = beforeSend['field_4']
                teachEnd = beforeSend['field_24']
                teachSum = beforeSend['field_8']
                teachProb = beforeSend['field_13']
                hw = beforeSend['field_9']
                hwTime = beforeSend['field_26']

                afterSend = u'%s的%s-%s,在%s, 从%s, 到%s, 进行了如下内容的授课:\n %s \n %s \n 课后作业为:%s, 预计可以在%s内完成。\n ' % (studentName, teacherJob, teacherName, teachDate, teachStart, teachEnd, teachSum, teachProb, hw, hwTime)
                groupName = 'BP-' + beforeSend['field_2'] +'-'
                group = itchat.search_chatrooms(name=groupName)
                if group:
                    itchat.send_msg(msg = afterSend,toUserName=getroom_message(groupName))
                else:
                    itchat.send('Could not find the group', toUserName='filehelper')
                    itchat.send_msg(msg = afterSend, toUserName='filehelper')
                #print (data + ' sendCompleted')
                #避免微信发消息过于频繁，延时
                time.sleep(0.5)

    return 'message'
    #1小时后itchat刷新，维持在线状态
    
    #afterSend未定义，if判断未执行状态下，会报错建议写入if条件下
    #target_group.send(afterSend)
    #堵塞进程后无法执行后续代码，res.status(200)无法返回，
    #金数据要求：该服务器需在2秒内返回2XX（200，201等）作为应答。不然会重试最多6次post请求
    #bot.join()
    #print 'sendCompleted'
    #return 'message'
    """


if __name__ == '__main__':
    itchat.auto_login(hotReload=True, loginCallback=lc, exitCallback=ec, enableCmdQR=2)
    print("hah")
    app.run(host='0.0.0.0', port=5050, debug=True)
