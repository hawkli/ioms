#!/usr/bin/python
# -*- coding: utf-8 -*-
#Linux版本CMDServer
#code by HAWK.Li

import ConfigParser, base64

import SocketServer, threading, socket, subprocess

import os, sys, time, string
import csv, logging, re

import MyUtil,ServerInfo
import AgentUpdateClient
import sitecustomize

def version(cmds, cmd):
    """CMDServer_version : 1.50_2012-03-20_Release
    """
    return version.__doc__

def readCron(csvfile):
    '''首次读入定时调度配置，确认当前时间，设定离下一分钟的秒数，分析定时调度
*,*,*,*,*,/home/a.sh
    '''
    if os.path.isfile(csvfile):
        spamReader = csv.reader(open(csvfile))
        #初始化内存中的列表，计数器，注意这样会强制占用列表0单位
        global AMinutes, AHours, ADays, AMonths, AWeeks, ACmd, AExe
        AMinutes = ['AMinutes']
        AHours = ['AHours']
        ADays = ['ADays']
        AMonths = ['AMonths']
        AWeeks = ['AWeeks']
        ACmd = ['cmd']
        AExe = ["exe"]
        listcount = 1
        if os.path.isfile(csvfile):
            f = open(csvfile, "r")
            for eachline in f:
                e = eachline.split(',')
                if len(e) == 7:
                    AMinutes.append(e[0])
                    AHours.append(e[1])
                    ADays.append(e[2])
                    AMonths.append(e[3])
                    AWeeks.append(e[4])
                    ACmd.append(e[5])
                    AExe.append(e[6])
                    listcount = listcount + 1
                else:
                    pass
        return listcount
    else:
        print "配置文件找不到，退出"
        exit(3)
        
class cmdServerThread(threading.Thread):
    def __init__(self, threadname):
        threading.Thread.__init__(self, name=threadname)
        
    def run(self):
        try:
            srv = SocketServer.ThreadingTCPServer((CmdServerIP, int(CmdServerPort)), CmdServer)
            srv.serve_forever()
        except:
            writeLog("cmdServerThread.run Error:" + str(sys.exc_info()[0]) + str(sys.exc_info()[1]))

class ServerMonitorInfo(threading.Thread):
    """每分钟发送一次心跳
    """
    def __init__(self, threadname):
        threading.Thread.__init__(self, name=threadname)
    
    def run(self):
        while True:
            try:
                try:
                    cpuload = ServerInfo.getCPUUsage()
                except:
                    self.writeLog("ServerMonitorInfo.cpuload:" + str(sys.exc_info()[0]) + str(sys.exc_info()[1]))
                    cpuload = '999'
                mem = ServerInfo.getPhyMem()
                memload = int(mem[1])
                try:
                    disk = ServerInfo.getDiskWarning()
                except:
                    disk = "GetdiskstatusError."
                try:
                    send = MyUtil.SendMsgToDB()
                    send.send(_3ds.Encrypt('agentHeart;' + computerId))
                    send.sock.recv(sockSize)
                    send.send(_3ds.Encrypt("ServerMonitorInfo;" + str(computerId) + ";" + str(cpuload) + ";" + str(memload) + ";" + str(disk) + ";" + str(CmdServerIP)))
                    send.sock.recv(sockSize)
                    send.send(_3ds.Encrypt('end'))
                except:
                    print "ServerMonitorInfo.run.send.error:" + str(sys.exc_info()[0]) + str(sys.exc_info()[1])
                    writeLog("ServerMonitorInfo.run.send.error:" + str(sys.exc_info()[0]) + str(sys.exc_info()[1]))
                finally:
                    send.closeSock()
                    time.sleep(60)
            except:
                print "ServerMonitorInfo.run error:" + str(sys.exc_info()[0]) + str(sys.exc_info()[1])
                writeLog("ServerMonitorInfo.run error:" + str(sys.exc_info()[0]) + str(sys.exc_info()[1]))
                time.sleep(60)
    
class CmdServer(SocketServer.BaseRequestHandler):
    """本模块负责接收服务端的命令请求
    """
    def handle(self):
        try:
            while True:
                cmd = self.request.recv(sockSize)
                cmd = _3ds.Decrypt(cmd)
                print "recevied command: "+str(cmd)
                cmds = MyUtil.splitCmd(cmd)
                keys = cmds.keys()
                if len(keys) > 0:
                    if cmds['cmd'] in fm.keys():
                        self.request.sendall(str(fm[cmds['cmd']](cmds, cmd)))
                        break
                    else:
                        self.request.sendall("-1")
                        break
                else:
                    self.request.sendall("-1")
                    break
            self.request.close()
        except:
            self.request.close()
            writeLog("CmdServer.handle:" + str(sys.exc_info()[0]) + str(sys.exc_info()[1]))
            print "CmdServer.handle:" + str(sys.exc_info()[0]) + str(sys.exc_info()[1])

def cronlist(cmds, cmd):
    """返回agent守护进程列表--CMDServer只负责看，真正守护的工作由agentservice完成
    """
    exes = "|"
    for i, e in enumerate(AExe):
        if i <> 0:
            exes += str(e) + "|"
    return exes + "\n"

def cronAdd(cmds, cmd):
    """增加守护进程列表的方法
    cmd=cronadd,cronadd=*;*;*;*;*;/usr/bin/tomcat.sh;JAVA
    """
    try:
        if not 'cronadd' in cmds.keys():
            return "-1", "Lost cronadd.缺少cronadd参数".encode("utf-8")
        cronNew = cmds['cronadd'].upper() + '\n'
        if not cronNew.find(';'):
            return "-1", "parameter Error.请使用;分号为分隔符".encode("utf-8")
        cronNew = cronNew.replace(';', ',')
        if os.path.isfile(MyUtil.cur_file_dir() + '/crontab.ini'):
            f = open(MyUtil.cur_file_dir() + '/crontab.ini', "r+")
            cronMatch = False
            for eachLine in f:
                if cronNew == eachLine.upper():
                    cronMatch = True
                    break
                else:
                    cronMatch = False
            str1 = 'Find duplicate cron.'
            if not cronMatch:
                f.write(cronNew + '\n')
                str1 = 'cronadd OK.'
            f.close()
            return "1", str1
        else:
            return "-1", 'crontab.ini not found.'
    except:
        return "-1", "CronAdd.Error"
    
def cronRemove(cmds, cmd):
    """删除已有守护进程列表的方法
    cmd=cronremove,cronremove=*;*;*;*;*;/usr/bin/a.sh
    """
    try:
        if not 'cronremove' in cmds.keys():
            return "-1", "Lost cronremove.缺少cronremove参数".encode("utf-8")
        cronNew = cmds['cronremove'].upper() + '\n'
        if not cronNew.find(';'):
            return "-1", "parameter Error.请使用;分号为分隔符".encode("utf-8")
        cronNew = cronNew.replace(';', ',')
        crons = ''
        if os.path.isfile(MyUtil.cur_file_dir() + '/crontab.ini'):
            f = open(MyUtil.cur_file_dir() + '/crontab.ini', "r+")
            cronMatch = False
            for eachLine in f:
                if cronNew == eachLine.upper():
                    cronMatch = True
                    break
                else:
                    crons += eachLine
                    cronMatch = False
            f.close()
            print crons
            if cronMatch:
                f = open(MyUtil.cur_file_dir() + '/crontab.ini', "w")
                f.write(crons + '\n')
                str1 = 'cronRemove OK.'
                f.close()
            else:
                str1 = cmds['cronremove'] + ' Cron not found.'
            return "1", str1
        else:
            return "-1", 'crontab.ini not found.'
    except:
        return "-1", "CronRemove.Error"

def isOnLine(cmds, cmd):
    """返回CMDServer是否在线
    """
    return "存活\n"

def Cpassword(cmd, cmdStr):
    """更改CMDServer所在windows操作系统的密码
    """
    try:
        if not 'password' in cmd.keys():
            return "-1", "Lost password.参数不完整，缺少密码".encode("utf-8")
        Cpass = cmd['password']
        Cpass1 = ''.join(Cpass.split())
        if Cpass1 <> Cpass:
            return "-1", 'Password has space.密码有空格不支持'.encode("utf-8")
        if not 'account' in cmd.keys():
            return "-1", "Lost account.参数不完整，缺少账号".encode("utf-8")
        account = cmd['account']
        restr = ""
        lines = os.popen("echo '%s:%s'|chpasswd" % (account, Cpass) + ' 2>&1').readlines()
        for line in lines:
            restr += line
        writeLog(restr)
        return restr.encode("utf-8")
    except:
        print "Cpassword Error:" + str(sys.exc_info()[0]) + str(sys.exc_info()[1])
        writeLog("Cpassword Error:" + str(sys.exc_info()[0]) + str(sys.exc_info()[1]))

def MyUnZIP(cmds, cmd):
    """收到命令后进行解压的方法
    cmd=unzip,unzipfile=c:/a.zip,path=c:/test
    """
    try:
        if not 'unzipfile' in cmds.keys():
            return "-1", "Lost unzip filename.缺少zip压缩文件参数".encode("utf-8")
        if not 'path' in cmds.keys():
            return "-1", "Lost unzip path.缺少解压目录路径".encode("utf-8")    
        #unzip方法只支持/，所以要转义
        zpath = cmds['path'].replace('\\', '/')
        zfile = cmds['unzipfile']
        if os.path.isfile(zfile):
            zfile = zfile.replace('\\', '/')
            result1 = MyUtil.UnZIP(zfile, zpath)
            if result1 <> '-1':
                return "1", "unzip OK.解压完成."
            else:
                return "-1", "unzip failed.解压失败."
        else:
            return "-1", 'zipfile not found.压缩文件未找到.'
    except:
        return "-1", "MyUnZIP.Error"
    

def command(cmds, cmd):
    """执行命令"""
    restr = ""
    lines = os.popen(cmds['command'] + ' 2>&1').readlines()
    for line in lines:
        restr += line
    print restr
    return restr.encode("utf-8")
    #怀疑编码的问题在这里，默认不是GBK，但是一种unicode，所以按默认的文件codeutf-8已经转了，不能再用GBK做encoding
    #以下先试试看能否解决问题
#    print restr
#    if isinstance(restr, unicode):
#        print "code is unicode!"
#    else:
#        print "code not unicode!"
#    return restr.decode("CP936").encode("utf-8")

def forever():
    try:
        print "CmdServer启动"
        writeLog('CmdServer Start')
        cmdserver = cmdServerThread("cmdserver")
        cmdserver.start()
        try:
            send = MyUtil.SendMsgToDB()
            send.send(_3ds.Encrypt('startAgent;' + computerId))
            send.sock.recv(sockSize)
            
            info1 = _3ds.Encrypt("insertServer;" + computerId + ";" + infos)
            send.send(info1)
            send.sock.recv(sockSize)
            send.send(_3ds.Encrypt('end'))
            send.closeSock()
        except:
            writeLog("CMDServer.handle:" + str(sys.exc_info()[0]) + str(sys.exc_info()[1]))
        serverinfo = ServerMonitorInfo("ServerMonitorInfo")
        serverinfo.start()
        serverinfo.join()
        cmdserver.join()
    except:
        print "runCron Error:" + str(sys.exc_info()[0]) + str(sys.exc_info()[1])
        writeLog("CMDServer.forever Error:" + str(sys.exc_info()[0]) + str(sys.exc_info()[1]))

def writeLog(info):
    """记录日志方法
    """
    try:
        log.output(info)
        
    except:
        print "writeLog Error:" + str(sys.exc_info()[0]) + str(sys.exc_info()[1])
        pass

def setLocalIP():
    #强写本地IP地址到配置文件中去
    cf1 = ConfigParser.ConfigParser()
    cf1.read(MyUtil.cur_file_dir() + "/auto.ini")
    ipMac = ServerInfo.GetinnerIPMac()
    innerIP = str(ipMac[0])
    cf1.set("Configuration", "localIP", innerIP)
    cf1.write(open(MyUtil.cur_file_dir() + "/auto.ini", "w"))
   
if __name__ == '__main__':
    global computerId, fm, sockSize, _3ds
    _3ds = MyUtil._secret()
    sockSize = 64000
    computerId = MyUtil.getComputerId()
    setLocalIP()
    fm = {
          "downloads":AgentUpdateClient.downloads,
          "updateself":AgentUpdateClient.updateSelf,
          "cronlist":cronlist,
          "agentlist":isOnLine,
          "command":command,
          "version":version,
          "password":Cpassword,
          "cronadd":cronAdd,
          "cronremove":cronRemove,
          "unzip":MyUnZIP
          }
    
    cf1 = ConfigParser.ConfigParser()
    cf1.read(MyUtil.cur_file_dir() + "/agent.ini")
    cf2 = ConfigParser.ConfigParser()
    cf2.read(MyUtil.cur_file_dir() + "/auto.ini")
    
    global CmdServerIP, CmdServerPort, DBIP, DBPort,CPUCores,infos
    path = cf1.get("main", "path").encode("utf-8")
    logfile = cf1.get("main", "logfile").encode("utf-8")
    
    updateServerIp = cf1.get("main", "UpdateServerIP").encode("utf-8")
    AgentUpdateClient.serverIp = updateServerIp
    CmdServerIP = cf2.get("Configuration", "localIP").encode("utf-8")
    CmdServerPort = cf1.get("main", "CmdServerPort").encode("utf-8")
    MyUtil.DBIP = cf1.get("main", "DBIP").encode("utf-8")
    MyUtil.DBPort = cf1.get("main", "DBPort").encode("utf-8")
    try:
        innerIP = cf2.get("Configuration", "localIP").encode("utf-8")
    except:
        innerIP = "getIP_Error"
    try:
        innerMAC = cf2.get("Configuration","localMACAddress").encode("utf-8")
    except:
        innerMAC = "getMAC_Error"
    try:
        WAIIP = cf2.get("Configuration","OuterIP").encode("utf-8")
    except:
        WAIIP = "getWAIIP_Error"
    try:
        OS = cf2.get("Configuration","OS").encode("utf-8")
    except:
        OS = "getOS_Error"
    try:
        CodeSet = cf2.get("Configuration","CodeSet").encode("utf-8")
    except:
        CodeSet = "getCodeSet_Error"
    try:
        CPUCores = cf2.get("Configuration","CPUCores").encode("utf-8")
    except:
        CPUCores = '1'
    try:
        Hostname = cf2.get("Configuration","hostname").encode("utf-8")
    except:
        Hostname = "getHostname_Error"
    try:
        getPlatform = cf2.get("Configuration","Platform").encode("utf-8")
    except:
        getPlatform = "Linux"
    try:
        CPUInfo = cf2.get("Configuration","CPUInfo").encode("utf-8")
    except:
        CPUInfo = "GetCPUInfo_Error"
    try:
        SysDir = cf2.get("Configuration","SystemDirectory").encode("utf-8")
    except:
        SysDir = "GetSystemDir_Error"
    try:
        PHMEM = cf2.get("Configuration","Physicalmemory").encode("utf-8")
    except:
        PHMEM = "GetPHMEM_Error"

    infos = str(innerIP+';'+WAIIP+';'+innerMAC+';'+OS+';'+Hostname+';'+SysDir+';'+CPUCores+';'+CPUInfo+';'+PHMEM+';'+CodeSet+';'+getPlatform)
    
    readCron(MyUtil.cur_file_dir() + '/crontab.ini')
    
    global LOG, log
    LOG = os.path.join(path, logfile)
    log = MyUtil.CLogInfo(LOG)
    forever()
    log.close()
    
