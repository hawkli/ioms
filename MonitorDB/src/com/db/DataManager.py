#!/usr/bin/python
#-*- coding:utf-8-*-
#code by HAWK.Li

import base64
import ConfigParser
import sys,os
import SocketServer
import time

import MyUtil,DBUtil
import sitecustomize

def version(cmds,cmd):
    """DataManager_version : 1.5_2012-03-12_Release
    """
    return version.__doc__

class DataManager(SocketServer.BaseRequestHandler):
    """运维数据库管理核心模块
    """
    def handle(self):
        while True:
            try:
                try:
                    recvData = self.request.recv(sockSize)
                    recvData = _3ds.Decrypt(recvData)
                except:
                    recvData ="recvDataError"
                    break
                if recvData=='end':
                    break
                agentIp = self.client_address[0]
                recvData += ';'+agentIp
                print time.strftime('%Y-%m-%d %H:%M:%S',time.localtime(time.time()))+"|"+recvData
                key = str(recvData).split(';')[0]
                if key in fm.keys():
                    fm[key](recvData)
                self.request.sendall('1')
            except:
                print "DataManager Error:"+str(sys.exc_info()[0])+str(sys.exc_info()[1])
        self.request.close()

def agentHeart(data):
    """用于每分钟agent心跳的命令，暂时用startAgent方法
    """
    startAgent(data)
    
def startAgent(data):
    """agent启动时候向更新或插入agent信息
    """
    try:
        db = DBUtil.DBUtil('ioms_monitor')
        _data = data.split(';')
        _data = toUtf8(_data)
        sql = "select agent_id from active_server where agent_id=%s"
        param = [[_data[1]]]
        result = db.getData(sql, param)
        if not result==None and len(result)==1:
            sql = "update active_server set HB_time=now() where agent_id=%s"
            param = [[_data[1]]]
            db.update(sql, param)
        else:
            sql = "insert into active_server(agent_id,server_IP,HB_warning,HB_time) values(%s,%s,'OK',now())"
            param = [[_data[1],_data[2]]]
            db.insert(sql, param)
        db.commit()
        db.closeConn()
    except:
        print "startAgent Error:"+str(sys.exc_info()[0])+str(sys.exc_info()[1])

def insertServer(data):
    """向数据库server_list表插入服务器配置信息
    """
    try:
        db = DBUtil.DBUtil('ioms_monitor')
        _data = data.split(';')
        _data = toUtf8(_data)
        sql = "select agent_id from server_list where agent_id=%s"
        param = [[_data[1]]]
        result = db.getData(sql, param)
        if result==None or len(result)==0:
            sql = "insert into server_list(agent_id,server_ip_lan,server_ip_wan,server_mac_lan,server_type,server_hostname,server_systemdir,HW_CPU_num,HW_CPU_info,HW_RAM_info,server_codeset,server_template,achieve_time) values(%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,now())"
            param = [[_data[1],_data[2],_data[3],_data[4],_data[5],_data[6],_data[7],_data[8],_data[9],_data[10],_data[11],_data[12]]]
            
            db.insert(sql, param)
        db.commit()
        db.closeConn()
    except:
        print "insertServer Error:"+str(sys.exc_info()[0])+str(sys.exc_info()[1])

def insertProLog(data):
    """记录受监控进程的心跳记录process_monitor表
    """
    try:
        db = DBUtil.DBUtil('ioms_monitor')
        _data = data.split(';')
        _data = toUtf8(_data);
        ram = "%d" % (int(_data[4])/1024)
        vram = "%d" % (int(_data[5])/1024)
        sql = "insert into process_monitor(agent_ip,process_name,status,process_id,process_ram,process_vram,process_cpu,log_time) values(%s,%s,%s,%s,%s,%s,%s,%s)"
        param = [[_data[1],_data[2],'running',_data[3],ram,vram,_data[6],_data[7]]]
        db.insert(sql, param)
        db.commit()
        db.closeConn()
    except:
        print "insertProLog Error:"+str(sys.exc_info()[0])+str(sys.exc_info()[1])

def NotRUNProess(data):
    """记录监控进程时发现的未启动进程process_monitor表
    """
    try:
        db = DBUtil.DBUtil('ioms_monitor')
        _data = data.split(';')
        _data = toUtf8(_data);
        sql = "insert into process_monitor(agent_ip,process_name,status,log_time) values(%s,%s,%s,%s)"
        param = [[_data[1],_data[2],'NOTRUN',_data[3]]]
        db.insert(sql, param)
        db.commit()
        db.closeConn()
    except:
        print "insertProLog Error:"+str(sys.exc_info()[0])+str(sys.exc_info()[1])

def processRestart(data):
    """记录受重启的进程列表process_restart表
    """
    try:
        db = DBUtil.DBUtil('ioms_monitor')
        _data = data.split(';')
        _data = toUtf8(_data);
        sql = "insert into process_restart(agent_ip,process_name,process_executablepath,restart_time,log_time) values(%s,%s,%s,%s,now())"
        param = [[_data[1],_data[2],_data[3],_data[4]]]
        db.insert(sql, param)
        db.commit()
        db.closeConn()
    except:
        print "processRestart Error:"+str(sys.exc_info()[0])+str(sys.exc_info()[1])

def ServerMonitorInfo(data):
    '''服务器的心跳server_monitor
    '''
    try:
        db = DBUtil.DBUtil('ioms_monitor')
        _data = data.split(';')
        _data = toUtf8(_data);
        sql = "insert into server_monitor(agent_id,CPU_load,RAM_load,DISK_load,agent_ip,log_time) values(%s,%s,%s,%s,%s,now())"
        param = [[_data[1],_data[2],_data[3],_data[4],_data[5]]]
        db.insert(sql, param)
        db.commit()
        db.closeConn()
    except:
        print "ServerMonitorInfo Error:"+str(sys.exc_info()[0])+str(sys.exc_info()[1])

def toUtf8(data):
    """编码转换UTF-8
    """
    l = len(data)
    for i in range(l):
        try:
            data[i] = data[i].decode('gbk').encode("utf-8")
        except:
            print "toUtf8 Error:"+str(sys.exc_info()[0])+str(sys.exc_info()[1])
    return data

def start():
    try:
        global fm,_3ds
        _3ds = MyUtil._secret()
        fm = {"startAgent":startAgent,"insertServer":insertServer,"insertProLog":insertProLog,"ServerMonitorInfo":ServerMonitorInfo,"agentHeart":agentHeart,"processRestart":processRestart,"NotRUNProess":NotRUNProess}
        
        cf = ConfigParser.ConfigParser()
        cf.read("MonitorDB.ini")
        
        DBUtil.DBHost = cf.get("main", "DBHost")
        DBUtil.DBPort=cf.get("main", "DBPort")
        DBUtil.DBUser=cf.get("main", "DBUser")
        DBUtil.DBPwd=cf.get("main", "DBPwd")
        serverIP=cf.get("main", "serverip")
        serverPORT=cf.get("main", "serverport")
        
        print u"数据库服务启动"
        print version.__doc__,MyUtil.version.__doc__,DBUtil.version.__doc__
        print u"DataManagerServerIP %s   PORT:%s"%(serverIP,serverPORT)
        srv = SocketServer.ThreadingTCPServer((serverIP,int(serverPORT)), DataManager)
        srv.serve_forever()
    except:
        print "start Error:"+str(sys.exc_info()[0])+str(sys.exc_info()[1])
        
if __name__ == "__main__":
    global sockSize
    sockSize = 64000
    start()
    