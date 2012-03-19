#!/usr/bin/python
#-*- coding:utf-8-*-
#code by HAWK.Li

import os,sys
import sitecustomize
import ConfigParser
import SocketServer,socket
import time,datetime
import base64
import threading,Queue

import MyUtil,DBUtil
import sitecustomize

def version(cmds,cmd):
    """IOMServer_version : 1.5_2012-03-12_Release
    """
    return version.__doc__

class IOMServer(SocketServer.BaseRequestHandler):
    """IOMS核心模块
    """
    def handle(self):
        user = ""
        userIp = ""
        print str(time.strftime('[%Y-%m-%d_%H:%M:%S]进入IOMS核心模块')).decode('utf-8').encode("gbk")
        while True:
            reStr = u""
            recvData = None            
            try:
                recvData = self.request.recv(sockSize)
                recvData = _3ds.Decrypt(recvData).decode('gbk').encode("utf-8")  
                userIp = str(self.client_address[0])
            except:
                writeLog("IOMServer.recvData Error:"+str(sys.exc_info()[0])+str(sys.exc_info()[1]))
                writeLog("|"+userIp+"| "+user+"Connection break. 断开连接！")
                if user in socketMap.keys():
                    socketMap.pop(user)
                break
            if not recvData:
                #因有时会发生一直读取到空消息的问题，所以先改成让服务休息一会避免CPU占用而卡死
                time.sleep(1)
                continue
            cmds = MyUtil.splitCmd(recvData)
            keys = cmds.keys()
            if  not (('parm=checkUser' in recvData) or ('cmd=login' in recvData)):
                p = str(time.strftime('[%Y-%m-%d_%H:%M:%S]Receviced command.收到命令: ')+recvData)
                print p.decode('utf-8').encode("gbk")                
                writeLog("|"+userIp+"| "+user+" "+recvData)
            else:
                recvData = "login"
                #continue
            #try:
            if 'cmd' in keys and cmds['cmd']=='login':
                """登录"""
                if 'user' in keys and 'pwd' in keys:
                    user = str(cmds['user'])
                    re = self.login(self.request, cmds['user'], cmds['pwd'])
                    if re == -1:
                        p = str(time.strftime('[%Y-%m-%d_%H:%M:%S]Receviced command.收到命令'+userIp+"| "+user+"Login failed! 登录失败！连接关闭！"))
                        print p.decode('utf-8').encode("gbk")                          
                        writeLog("|"+userIp+"| "+user+"Login failed 登录失败！连接关闭！")
                        self.request.close()
                        reStr = "Login failed.登录失败."
                        break
                    elif re == 1:
                        p = str(time.strftime('[%Y-%m-%d_%H:%M:%S]Receviced command.收到命令'+userIp+"| "+user+" : Login sucess! 连接！"))
                        print p.decode('utf-8').encode("gbk")   
                        writeLog("|"+userIp+"| "+user+" 连接！")
                        reStr = "Login sucess.登录成功."
            
            elif 'cmd' in keys and 'uploads' == cmds['cmd'] and 'file' in keys:
                """上传文件，把客户端接收到的数据直接转发到AutoUpdateServer上去"""
                writeLog("|"+userIp+"| "+user+" 请求上传文件！"+cmds['file'])
                sock = getSock(UpdateServerIP, int(UpdateServerPort))
                sock.sendall("au,"+recvData)
                self.request.sendall(sock.recv(sockSize))
                print "Begin updaload...开始上传。。。".decode('utf-8').encode("gbk")
                i = 0
                while True:
                    data = self.request.recv(10485760)
                    print "Receviced files...接受文件中。。。。".decode('utf-8').encode("gbk"),'  ',i
                    i+=1
                    if not data:
                        reStr = "Receviced complete.上传完成."
                        print "All File Receviced complete.文件全部接受完成".decode('utf-8').encode("gbk")
                        break
                    if str(data).endswith('4423718C61C4E8A4362D955BBC7B9711'):
                        data = data[:len(data)-len('4423718C61C4E8A4362D955BBC7B9711')]
                        reStr = "Receviced complete.上传完成."
                        print "All File Receviced complete.文件全部接受完成".decode('utf-8').encode("gbk")
                        break
                    while len(data) > 0:
                        intSent = sock.send(data)
                        data = data[intSent:]
                        print "Sending...发送文件中。。。".decode('utf-8').encode("gbk"),'  ',intSent
                    print "File Receviced complete.接受文件完成".decode('utf-8').encode("gbk")
                    #time.sleep(1)
                reStr = "Receviced complete.上传完成."
                sock.close()
                writeLog("|"+userIp+"| "+user+" 上传文件完成")
                if reStr=="":
                    reStr = "Receviced failed.上传失败."
            
            elif 'cmd' in keys and 'dir' == cmds['cmd']:
                """查看可以下载的文件"""
                sock = getSock(UpdateServerIP, int(UpdateServerPort))
                sock.sendall('au,'+recvData)
                self.response = sock.recv(sockSize)
                if self.response=='-1':
                    self.request.sendall('Not files can be download.没有可以下载的文件.')
                else:
                    self.request.sendall('Download files list:可下载文件列表:\n'+self.response)
                sock.close()
            
            elif 'cmd' in keys and 'remove' == cmds['cmd']:
                """删除文件"""
                if not 'file' in cmds.keys():
                    print "Lost file name.参数不完整，缺少文件名".decode('utf-8').encode("gbk")
                else:
                    sock = getSock(UpdateServerIP, int(UpdateServerPort))
                    sock.sendall('au,'+recvData)
                    self.response = sock.recv(sockSize)
                    if self.response=='1':
                        self.request.sendall('Delete complete.删除完成。')
                        #reStr = '删除完成。'
                    else:
                        self.request.sendall("File not found.文件不存在。")
                        #reStr = "文件不存在。"
                    sock.close()
            
            elif 'cmd' in keys and 'genmd5' == cmds['cmd']:
                """重新生成Md5码"""
                sock = getSock(UpdateServerIP, int(UpdateServerPort))
                sock.sendall('au,'+recvData)
                self.response = sock.recv(sockSize)
                if self.response=='1':
                    self.request.sendall('Rebuilding MD5 sucess.重新生成成功。')
                    #reStr = "重新生成成功。"
                elif self.response=='-1':
                    self.request.sendall('Rebuilding MD5 failed.生成失败。')
                    #reStr = '生成失败。'
                sock.close()
            elif 'cmd' in keys and 'dbutil' == cmds['cmd']:
                """进行数据库操作"""
                if cmds['parm'] != None:
                    parm = str(cmds['parm']).split(';')
                    if 'checkUser' == parm[0]:
                        if len(parm) == 3:
                            db_user = DBUtil.User()
                            checkRow = db_user.Check(parm[1], parm[2])
                            if not checkRow:
                                self.request.sendall("-2")
                            else:
                                self.request.sendall("1")
                    elif 'actionLog' == parm[0]:
                        if len(parm) == 5:
                            db_user = DBUtil.User()
                            db_user.actionLog(parm[1], parm[2], parm[3], parm[4])
                            #self.request.sendall(flag)
                    elif 'getAllServerList' == parm[0]:
                        db_server = DBUtil.Server()
                        _allServerList = db_server.getAllServerList()
                        serverListStr = ""
                        for _allServer in _allServerList:
                            for _server in _allServer:
                                serverListStr += str(_server) + ",,"
                            if serverListStr.endswith(",,"):
                                serverListStr = serverListStr[:len(serverListStr)-2]
                            serverListStr += ";;"
                        if serverListStr.endswith(";;"):
                            serverListStr = serverListStr[:len(serverListStr)-2]
                        if serverListStr == '':
                                serverListStr = 'None'                            	
                        self.request.sendall(serverListStr)
                    elif 'getAllActiveServerList' == parm[0]:
                        db_server = DBUtil.Server()
                        _allActiveServerList = db_server.getAllActiveServerList()
                        serverListStr = ""
                        for _allServer in _allActiveServerList:
                            for _server in _allServer:
                                serverListStr += str(_server) + ",,"
                            if serverListStr.endswith(",,"):
                                serverListStr = serverListStr[:len(serverListStr)-2]
                            serverListStr += ";;"
                        if serverListStr.endswith(";;"):
                            serverListStr = serverListStr[:len(serverListStr)-2]
                        if serverListStr == '':
                                serverListStr = 'None'                                
                        self.request.sendall(serverListStr)
                    elif 'updateServerInfo' == parm[0]:
                        if len(parm) == 9:
                            db_server = DBUtil.Server()
                            serverInfo = [None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None]
                            serverInfo[0] = parm[1]
                            serverInfo[13] = parm[2]
                            serverInfo[14] = parm[3]
                            serverInfo[15] = parm[4]
                            serverInfo[16] = parm[5]
                            serverInfo[17] = parm[6]
                            serverInfo[18] = parm[7]
                            serverDistribute = parm[8]
                            flag = db_server.updateServerInfo(serverInfo, serverDistribute)
                            self.request.sendall(str(flag))
                    elif 'updateServerGC' == parm[0]:
                        if len(parm) > 1:
                            db_server = DBUtil.Server()
                            serverGCList = ""
                            length = len(parm)
                            for i in range(length):
                                if i > 0:
                                    serverGCList += "'"
                                    serverGCList += parm[i]
                                    serverGCList += "'"
                                    if i < length - 1:
                                        serverGCList += ","
                                else:
                                    pass
                            serverDistribute = 2
                            flag = db_server.updateServerGC(serverGCList, serverDistribute)
                            self.request.sendall(str(flag))
                    elif 'serverCpuCurve' == parm[0]:
                        if len(parm) == 4:
                            db_server = DBUtil.Server()
                            serverCpuInfoList = db_server.getServerCpuInfo(parm[1], parm[2], parm[3])
                            serverListStr = ""
                            for _allServer in serverCpuInfoList:
                                for _server in _allServer:
                                    serverListStr += str(_server) + ",,"
                                if serverListStr.endswith(",,"):
                                    serverListStr = serverListStr[:len(serverListStr)-2]
                                serverListStr += ";;"
                            if serverListStr.endswith(";;"):
                                serverListStr = serverListStr[:len(serverListStr)-2]
                            serverListStr = serverListStr.decode('gbk').encode("utf-8")
                            if serverListStr == '':
                                serverListStr = 'None'
                            self.request.sendall(serverListStr)
                    elif 'getAllDirList' == parm[0]:
                        db_dir = DBUtil.Dir()
                        _allDirList = db_dir.getDirList()
                        dirListStr = ""
                        for _allDir in _allDirList:
                            for _dir in _allDir:
                                dirListStr += str(_dir) + ",,"
                            if dirListStr.endswith(",,"):
                                dirListStr = dirListStr[:len(dirListStr)-2]
                            dirListStr += ";;"
                        if dirListStr.endswith(";;"):
                            dirListStr = dirListStr[:len(dirListStr)-2]
                        if dirListStr == '':
                                dirListStr = 'None'                                
                        self.request.sendall(dirListStr)
                    elif 'getAllUnassignedServerList' == parm[0]:
                        db_server = DBUtil.Server()
                        _allServerList = db_server.getUnassignedServerList()
                        serverListStr = ""
                        for _allServer in _allServerList:
                            for _server in _allServer:
                                serverListStr += str(_server) + ",,"
                            if serverListStr.endswith(",,"):
                                serverListStr = serverListStr[:len(serverListStr)-2]
                            serverListStr += ";;"
                        if serverListStr.endswith(";;"):
                            serverListStr = serverListStr[:len(serverListStr)-2]
                        if serverListStr == '':
                                serverListStr = 'None'                                
                        self.request.sendall(serverListStr)
                    elif 'getPysicalServerList' == parm[0]:
                        if len(parm) == 2:
                            db_server = DBUtil.Server()
                            pysicalServerList = db_server.getPysicalServerList(parm[1])
                            serverListStr = ""
                            for _allServer in pysicalServerList:
                                for _server in _allServer:
                                    serverListStr += str(_server) + ",,"
                                if serverListStr.endswith(",,"):
                                    serverListStr = serverListStr[:len(serverListStr)-2]
                                serverListStr += ";;"
                            if serverListStr.endswith(";;"):
                                serverListStr = serverListStr[:len(serverListStr)-2]
                            serverListStr = serverListStr.decode('gbk').encode("utf-8")
                            if serverListStr == '':
                                serverListStr = 'None'
                            self.request.sendall(serverListStr)
                    elif 'getMonitorServerList' == parm[0]:
                        db_server = DBUtil.Server()
                        if len(parm) == 3:
                            _allServerList = db_server.getMonitorServerList(parm[1],parm[2])
                        else:
                            #保持参数一致，方法比较低端
                            _allServerList = db_server.getMonitorServerList("None","None")
                        serverListStr = ""
                        for _allServer in _allServerList:
                            for _server in _allServer:
                                serverListStr += str(_server) + ",,"
                            if serverListStr.endswith(",,"):
                                serverListStr = serverListStr[:len(serverListStr)-2]
                            serverListStr += ";;"
                        if serverListStr.endswith(";;"):
                            serverListStr = serverListStr[:len(serverListStr)-2]
                        if serverListStr == '':
                                serverListStr = 'None'                                
                        self.request.sendall(serverListStr)
                        
                else:
                    self.request.sendall("-1")
            elif 'cmd' in keys and 'help' == cmds['cmd']:
                self.request.sendall(HELP.__doc__)
            elif 'cmd' in keys and 'showversion' == cmds['cmd']:
                self.request.sendall(version.__doc__)
            elif 'cmd' in keys and cmds['cmd'] in agentCmds:
                #获取当前服务器完整列表
                initServerMap()
                param = ""
                db = DBUtil.DBUtil('ioms_monitor')
                if 'servertype' in keys:
                    param = cmds['servertype']
                    #取出指定服务器类型服务器的所有内网IP
                    IPList=changeTemplateToIP(db,param)
                    if not IPList:
                        output = "%s: servertype not found!服务器类型未找到或命令错误！"%(param)
                        self.request.sendall(output)
                        print output.decode('utf-8').encode("gbk")
                        continue
                elif 'serverip' in keys:
                    param = cmds['serverip']
                    IPList = param.split(';')
                else:
                    output = "Fill servertype or serverip parameter.参数不完整，请填写服务器类型或服务器ip"
                    print output.decode('utf-8').encode("gbk")
                    self.request.sendall(output)
                    continue

                reStr = ""
                if 'command' in keys:
                    initCommandList("1")
                    commandRunFlag = False  #该命令是否可以执行的标识
                    for commandName in commandList:
                        if cmds['command'].startswith(commandName):
                            commandRunFlag = True
                            break
                    if commandRunFlag:
                        pass
                    else :
                        output = "Command not executive.不能执行该命令."
                        print output.decode('utf-8').encode("gbk")
                        self.request.sendall(output)
                        continue
                #对发送的命令recvData做去IP处理，减少命令广播
                print "recvData=",recvData
                tmpcmds = MyUtil.splitCmd(recvData)
                tmpkeys = tmpcmds.keys()
                if 'serverip' in tmpkeys:
                    t=tmpcmds.pop('serverip')
                if 'servertype' in tmpkeys:
                    t=tmpcmds.pop('servertype')
                s=''
                for dkey in tmpcmds:
                    s+=dkey+"="+tmpcmds[dkey]+","
                recvData=s[:len(s)-1]
                recvData = _3ds.Encrypt(recvData)
                #初始化命令返回结果集，这个global好象会有问题，也许会导致多个客户端同时返回结果时的异常，待后期分析
                global receiveData
                receiveData={}

                #对发出数据库中有心跳的服务器发送命令
                result = isOnline(db)
                #对比当前所有活动的服务器和需要操作的服务器IP，并把结果放在ActiveIPList中
                ActiveIPList = []
                if result:
                    for r in result:
                        for j in IPList:
                            if r[0] in j:
                                ActiveIPList.append(r[0])
                #IP排重
                ActiveIPList = list(set(ActiveIPList))
                #多线程响应命令执行，默认10个线程
                wm = WorkerManager(10)
                i = 0
                for IP in ActiveIPList:
                    wm.add_job( CommandRunThread, i,IP,recvData)
                    i += 1
                wm.wait_for_complete()
                db.closeConn()
                
                #准备回显数据
                output =""
                for k in receiveData.keys():
                    s = receiveData[k]
                    output += s
                
                if output:
                    output += "All command run over.全部执行完毕."
                else:
                    output = "Command run failed.执行不正确."
                self.request.sendall(output)
                print output.decode('utf-8').encode("gbk")
            else:
                output = "Command not found.没有该命令."
                self.request.sendall(output)
                print output.decode('utf-8').encode("gbk")

            
    def login(self,socket,user,pwd):
        db = DBUtil.DBUtil('ioms_user')
        param = [[user,pwd]]
        sql = "select account,password from user where account=%s and password=%s"
        result = db.getData(sql,param)
        db.closeConn()
        if len(result)==1:
            socketMap[user] = socket
            socket.sendall('1')
            return 1
        else:
            socket.sendall('-1')
            return -1

class Worker(threading.Thread):
    """工作线程－工人模块
    """
    worker_count = 0
    def __init__( self, workQueue, resultQueue, timeout = 0, **kwds):
        threading.Thread.__init__( self, **kwds )
        self.id = Worker.worker_count
        Worker.worker_count += 1
        self.setDaemon( True )
        self.workQueue = workQueue
        self.resultQueue = resultQueue
        self.timeout = timeout
        self.start( )

    def run( self ):
        """the get-some-work, do-some-work main loop of worker threads
        """
        while True:
            try:
                callable, args, kwds = self.workQueue.get(timeout=self.timeout)
                res = callable(*args, **kwds)
                self.resultQueue.put( res )
            except Queue.Empty:
                break
            except :
                break
                   
class WorkerManager:
    """工作线程－工作管理模块
    """
    def __init__( self, num_of_workers=10, timeout = 1):
        self.workQueue = Queue.Queue()
        self.resultQueue = Queue.Queue()
        self.workers = []
        self.timeout = timeout
        self._recruitThreads( num_of_workers )

    def _recruitThreads( self, num_of_workers ):
        for i in range( num_of_workers ):
            worker = Worker( self.workQueue, self.resultQueue, self.timeout )
            self.workers.append(worker)

    def wait_for_complete( self):
        while len(self.workers):
            worker = self.workers.pop()
            worker.join( )
            if worker.isAlive() and not self.workQueue.empty():
                self.workers.append( worker )

    def add_job( self, callable, *args, **kwds ):
        self.workQueue.put( (callable, args, kwds) )
    
    def get_result( self, *args, **kwds ):
        return self.resultQueue.get( *args, **kwds )

def getSock(host,port):
    #这个timeout的长短会直接影响长命令的返回，包括下载大文件，只要超过这个时间的大文件下载会强制断开
    socket.setdefaulttimeout(300)
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.connect((host, port))
    return sock
    
def CommandRunThread(id,IP,sendCMD):
    """运行命令的线程模块
    """
    try:
        sock = getSock(IP, int(CmdServerPort))
        sock.sendall(sendCMD)
        TResponse = sock.recv(sockSize)
        receiveData[IP] = str(IP) +": " + TResponse
        sock.close()
    except:
        receiveData[IP] = str(IP) + ":Connect failed. 无法连接.\n"
        #print receiveData[IP]
    return id

def writeActionLog(param):
    sql = "insert into user_action_log(account,action,result,ip_address,time) values(%s,%s,%s,%s,now())"
    db = DBUtil.DBUtil('ioms_user')
    db.insert(sql, param)
    db.closeConn()

def writeLog(info):
    """记录日志方法
    """
    try:
        log.output(info)
        
    except:
        print "writeLog Error:"+str(sys.exc_info()[0])+str(sys.exc_info()[1])
        pass
   
def initServerMap():
    """初始化所有服务器集合
    """
    db = DBUtil.DBUtil('ioms_monitor')
    sql = "select server_ip_lan,server_template,agent_id from server_list"
    result = db.getData(sql, None)
    for r in result:
        if r[1]==None:
            continue
        serverMap[r[0]] = [r[0],r[1],r[2]]
    db.closeConn()
    
def initCommandList(status):
    """初始化可执行命令集合
    """
    commandList.clear()
    db = DBUtil.DBUtil('ioms_monitor')
    sql = "select commandName from command_list where commandStatus = %s"
    result = db.getData(sql, [[status]])
    for r in result:
        if r[0] != None:
            commandList[r[0]] = [r[0]]
    db.closeConn()

def isOnline(db):
    #检查数据库所有3分钟内在线的服务器，并返回所有在线服务器的agent_id和server_ip
    sql = "select server_IP from active_server where HB_time > now() - INTERVAL 3 MINUTE"
    result = db.getData(sql,None)
    if result==None or len(result)<1:
        return False
    else:
        return result

def changeTemplateToIP(db,server_template):
    #检查数据库符合条件的servertype，并返回IP表
    sql = "select agent_id,server_ip_lan from server_list where server_template like '%%%s%%';"%(server_template)
    result = db.getData(sql,None)
    if result==None or len(result)<1:
        return False
    else:
        return result
def HELP():
    """
集中运维管理系统客户端程序语法：
cmd=[help][showversion][dir][uploads][remove][genmd5][downloads][agentlist][command][cronlist][cronadd][cronremove] 

当cmd=uploads时，后续参数为:
,localpath=本地路径,file=本地文件名,servertype=服务器类型或服务器IP地址

当cmd=remove时，后续参数为:
,file=需要删除的文件名

当cmd=downloads时，后续参数为:
,file=下载文件名,path=下载至何目录,servertype=服务器类型或服务器IP地址

当cmd=agentlist时，后续参数为:
,servertype=服务器类型或服务器IP地址

当cmd=command时，后续参数为:
,command=执行的命令行指令,serverip=服务器IP地址（注意执行的指令必须事先在允许列表中）

当cmd=cronlist时，后续参数为:
,servertype=服务器类型或服务器IP地址

当cmd=cronadd时，后续参数为:
,cronadd=分;小时;日;月;周;绝对路径;进程名,servertype=服务器类型或服务器IP地址

当cmd=cronremove时，后续参数为:
,cronremove=分;小时;日;月;周;绝对路径;进程名,servertype=服务器类型或服务器IP地址

当cmd=password时，后续参数为:
password=密码（禁止空格，双引单引，少用特殊字符）,account=账号,servertype=服务器类型或服务器IP地址

当cmd=unzip时，后续参数为:
,unzipfile=需要解压的zip绝对路径名,path=准备解压至何目录 ;进程名,servertype=服务器类型或服务器IP地址
注意，必须使用\\，不可以使用/或\号

举例:
帮助                : cmd=help
帮助                : cmd=showversion
查看可下载文件      : cmd=dir
上传文件            : cmd=uploads,localpath=d:\,file=test.txt
删除文件            : cmd=remove,file=delete.txt
重新生成md5         : cmd=genmd5
下载文件            : cmd=downloads,file=down.txt,path=d:\,servertype=gameserver[serverip=172.18.166.4;172.18.166.1]
返回agent存活状态   : cmd=agentlist,servertype=gameserver[serverip=172.18.166.4;172.18.166.1]
执行命令            : cmd=command,command=systeminfo,servertype=gameserver[serverip=172.18.166.4;172.18.166.1]
返会守护程序集      : cmd=cronlist,servertype=gameserver[serverip=172.18.166.4;172.18.166.1]
增加定时作业       : cmd=cronadd,cronadd=*;*;*;*;*;c:\\WINDOWS\\NOTEPAD.EXE;NOTEPAD.EXE,servertype=gameserver[serverip=172.18.166.4;172.18.166.1]
删除定时作业       : cmd=cronremove,cronremove=*;*;*;*;*;c:\\WINDOWS\\NOTEPAD.EXE;NOTEPAD.EXE,servertype=gameserver[serverip=172.18.166.4;172.18.166.1]
自更新              :cmd=updateself,servertype=gameserver[serverip=172.18.166.4;172.18.166.1]
检查CMDServer版本   :cmd=version,servertype=gameserver[serverip=172.18.166.4;172.18.166.1]
更改操作系统密码      :cmd=password,password=1234,account=admin,servertype=gameserver[serverip=172.18.166.4;172.18.166.1]
解压zip文件       :cmd=unzip,unzipfile=c:\\a.zip,path=c:\\test,servertype=gameserver[serverip=172.18.166.4;172.18.166.1]
    """
            
if __name__ == "__main__":
    global socketMap,agentCmds,serverMap,sockSize,_3ds,commandList
    try:
        #服务端socksize设为640K，避免大小不够导致大数据时丢失。
        sockSize = 640000
        _3ds = MyUtil._secret()
        socketMap = {}
        serverMap = {}
        commandList = {}
        #CMDServer支持的命令列表
        agentCmds = ["downloads","cronlist","cronadd","cronremove",
                     "agentlist","command","updateself","version",
                     "password","unzip"]
        
        cf = ConfigParser.ConfigParser()
        cf.read(MyUtil.cur_file_dir()+"\\IOMServer.ini")
        path = MyUtil.cur_file_dir()
        #path = cf.get("main", "path")
        logfile = cf.get("main", "logfile")
        serverIP = cf.get("main", "IP")
        port = cf.getint("main", "port")
        DBUtil.DBHost = cf.get("main", "DBHost")
        DBUtil.DBPort=cf.get("main", "DBPort")
        DBUtil.DBUser=cf.get("main", "DBUser")
        DBUtil.DBPwd=cf.get("main", "DBPwd")
        try:
            #从数据库中取出agent服务器列表
            initServerMap()
        except:
            print u"initServerMap Error:"+str(sys.exc_info()[0])+str(sys.exc_info()[1])
            
        try:
            #从数据库中取出支持的命令列表            
            initCommandList("1")
        except:
            print u"initCommandList Error:"+str(sys.exc_info()[0])+str(sys.exc_info()[1])

        global UpdateServerIP,UpdateServerPort,CmdServerPort
        UpdateServerIP = cf.get("main", "UpdateServerIP")
        UpdateServerPort = cf.get("main", "UpdateServerPort")
        CmdServerPort = cf.get("main", "CmdServerPort")

        global LOG,log
        LOG = os.path.join(path,logfile)
        log = MyUtil.CLogInfo(LOG)
        
        print u"IOMServer Start.集中控制服务器启动"
        print version.__doc__
        print u"ServerIP:%s         PORT:%s"%(serverIP,port)  
        print u"DBServerIP:%s       PORT:%s"%(DBUtil.DBHost,DBUtil.DBPort)  
        print u"UpdateServerIP %s   PORT:%s"%(UpdateServerIP,UpdateServerPort)
        writeLog('IOMServer Start.集中控制服务器启动')
        srv = SocketServer.ThreadingTCPServer((serverIP, int(port)),IOMServer)
        srv.serve_forever()
        log.close()
    except:
        print "main Error:"+str(sys.exc_info()[0])+str(sys.exc_info()[1])
        writeLog("main Error:"+str(sys.exc_info()[0])+str(sys.exc_info()[1]))
        log.close()