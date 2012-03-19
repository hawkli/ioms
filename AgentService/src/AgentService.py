#!/usr/bin/python
#-*- coding:utf-8-*-
#code by HAWK.Li
import base64,string,re
import socket,threading,subprocess
import sys,os,time
import csv,ConfigParser
import psutil
import win32event,win32service,win32serviceutil
import MyUtil,ServerInfo
import sitecustomize

def version(cmds,cmd):
    """AgentService_version : 1.5_2012-3-12_Release
    """
    return version.__doc__

class runCron():
    """定时作业调度模块
    """
  
    def run(self):
        '''首次读入定时调度配置，确认当前时间，设定离下一分钟的秒数，分析定时调度'''
        self.writeLog('agentService start.')
        while True:
            try:
                nowTime=string.split(time.strftime('%w,%m,%d,%H,%M,%S',time.localtime(time.time())), sep=',')
                timesWait=60-int(nowTime[5])
                #读入定时作业用的配置文件
                listcount=self.readCron(MyUtil.cur_file_dir()+'\\crontab.ini')
                
                cf = ConfigParser.ConfigParser()
                cf.read(MyUtil.cur_file_dir()+"\\agent.ini")
                MonitorProcess = cf.get("main", "MonitorProcess").decode('gbk').encode("utf-8").split(',')
                
                #当前全部的进程名
                allProcess = ServerInfo.getAllProcessName()
                #当前全部的进程及详细信息
                _allPro = ServerInfo.getAllProcessInfo()
                insertTime = time.strftime('%Y-%m-%d %H:%M:%S',time.localtime(time.time()))
                #循环需要定时守护的进程数
                for i in range(1,int(listcount)):
                    #如果当前进程中不存在守护的进程，调用定时守护启动程序，并发送重启信息给DB
                    if not str(AExe[i]).upper() in allProcess:
                        self.Cronjob(i,nowTime)
                        send = MyUtil.SendMsgToDB()
                        send.send(_3ds.Encrypt('processRestart;'+str(innerIP)+";"+str(AExe[i])+";"+str(ACmd[i])+";"+str(insertTime)))
                        send.sock.recv(socksize)
                        send.send(_3ds.Encrypt('end'))
                        send.closeSock()
                    else:
                        pass
                
                #如果当前进程中存在要监控的进程，循环找出该进程的相关信息发送至DB服务器    
                for MProcess in MonitorProcess:
                    ProcessStatus = 'NOTRUN'
                    for MPro in _allPro:
                        #如果进程在所有进程中找到一个相同的就发进程状态消息
                        if str(MProcess).upper() == str(MPro[0]).upper():
                            send = MyUtil.SendMsgToDB()
                            #发现psutil取出的进程CPU使用率，需要除CPU个数，否则不准
                            send.send(_3ds.Encrypt('insertProLog;'+innerIP+";"+str(MPro[0])+";"+str(MPro[1])+";"+str(MPro[2])+";"+str(MPro[3])+";"+str(int(MPro[4])/CPUCores)+";"+str(insertTime)))
                            send.sock.recv(socksize)
                            send.send(_3ds.Encrypt('end'))
                            send.closeSock()
                            ProcessStatus = 'running'
                            break
                        else:
                            ProcessStatus = 'NOTRUN'
                    #如果全部检查后进程状态为未运行，发送进程未启动信息
                    if ProcessStatus == 'NOTRUN':
                        try:
                            send = MyUtil.SendMsgToDB()
                            send.send(_3ds.Encrypt('NotRUNProess;'+innerIP+";"+str(MProcess).upper()+";"+str(insertTime)))
                            send.sock.recv(socksize)
                            send.send(_3ds.Encrypt('end'))
                        except:
                            self.writeLog("runCron.send.Error:"+str(sys.exc_info()[0])+str(sys.exc_info()[1]))
                        finally:
                            send.closeSock()
                            
                time.sleep(timesWait)
            except:
                self.writeLog("runCron Error:"+str(sys.exc_info()[0])+str(sys.exc_info()[1]))
                time.sleep(timesWait)

    def readCron(self,csvfile):
        '''首次读入定时调度配置，确认当前时间，设定离下一分钟的秒数，分析定时调度
    *,*,*,*,*,c:\WINDOWS\NOTEPAD.EXE
    *,*,*,*,*,e:\1.bat
        '''
        try:
            self.writeLog("readCron:"+str(csvfile))
            if os.path.isfile(csvfile):
                spamReader = csv.reader(open(csvfile))
                #初始化内存中的列表，计数器，注意这样会强制占用列表0单位
                global AMinutes,AHours,ADays,AMonths,AWeeks,ACmd,AExe
                AMinutes=['AMinutes']
                AHours=['AHours']
                ADays=['ADays']
                AMonths=['AMonths']
                AWeeks=['AWeeks']
                ACmd=['cmd']
                AExe=["exe"]
                listcount=1
                if os.path.isfile(csvfile):
                    f = open(csvfile,"r")
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
                            listcount=listcount+1
                        else:
                            pass
                    f.close()
                    #永久守护CMDServer.exe程序
                    AMinutes.append('*')
                    AHours.append('*')
                    ADays.append('*')
                    AMonths.append('*')
                    AWeeks.append('*')
                    ACmd.append(MyUtil.cur_file_dir()+'\\CMDServer.exe')
                    AExe.append('CMDserver.exe')
                    listcount = listcount+1
                    return listcount
                else:
                    pass
                    self.writeLog("readCron else:"+str(sys.exc_info()[0])+str(sys.exc_info()[1]))
        except:
            self.writeLog("readCron Error:"+str(sys.exc_info()[0])+str(sys.exc_info()[1]))
            
    def Cronjob(self,i,nowTime):
        '''定时调度程序，必须的全局参数为：
    AMinutes[i],AHours[i],ADays[i],AMonths[i],AWeeks[i],ACmd[i]
    '''
        try:    
            #crontab语法:  分，小时，日，月，星期
            #星期，月，          日，         小时，   分，         秒
            #[0-6],[1-12],[1-31],[0-23],[0-59],[0-59]
            #周判断，前面先用正则过滤掉不对的
            match = re.search('\*|[0-6]',AWeeks[i])
            if match:
                if AWeeks[i] == '*' :
                    pass
                else:
                    if int(AWeeks[i]) <> int(nowTime[0]):
                        return
            else:
                return
            #月份判断
            match = re.search('\*|[0-9]',AMonths[i])
            if match:
                if AMonths[i] == '*' :
                    pass
                else:
                    if int(AMonths[i]) <> int(nowTime[1]):
                        return
            else:
                return
            #日期判断
            match = re.search('\*|[0-9]',ADays[i])
            if match:
                if ADays[i] == '*' :
                    pass
                else:
                    if int(ADays[i]) <> int(nowTime[2]):
                        return
            else:
                return
            #小时判断
            match = re.search('\*|[0-9]',AHours[i])
            if match:
                if AHours[i] == '*' :
                    pass
                else:
                    if int(AHours[i]) <> int(nowTime[2]):
                        return
            else:
                return
            #分钟判断
            match = re.search('\*|[0-9]',AMinutes[i])
            if match:
                if AMinutes[i] == '*' :
                    pass
                else:
                    if int(AMinutes[i]) <> int(nowTime[2]):
                        return
            else:
                return
            try:
                output = subprocess.Popen(ACmd[i])
            except WindowsError,e:
                self.writeLog("program.not.found Error:"+str(sys.exc_info()[0])+str(sys.exc_info()[1]))
                pass
            lr= ACmd[i]
            self.writeLog("process: "+lr+" not found, restart.")
            return
        
        except Exception, e:
            self.writeLog("Cronjob Error:"+str(sys.exc_info()[0])+str(sys.exc_info()[1]))
                
    def writeLog(self,info):
        log.output(info)

class ServiceDoRun(win32serviceutil.ServiceFramework):        
    _svc_name_ = "AgentService" 
    _svc_display_name_ = "AgentService"
    _svc_description_ = "IOMS AgentService for windows"
    def __init__(self, args): 
        win32serviceutil.ServiceFramework.__init__(self, args) 
        self.hWaitStop = win32event.CreateEvent(None, 0, 0, None) 

    def SvcStop(self): 
        # 先告诉SCM停止这个过程 
        self.ReportServiceStatus(win32service.SERVICE_STOP_PENDING) 
        # 设置事件 
        win32event.SetEvent(self.hWaitStop)

    def SvcDoRun(self):
        try:
            global LOG,DBIP,DBPort,_3ds,log,socksize,innerIP,CPUCores
            socksize = 64000
            _3ds = MyUtil._secret()
            cf1 = ConfigParser.ConfigParser()
            cf1.read(MyUtil.cur_file_dir() + "\\agent.ini")
            agentpath = cf1.get("main", "path").decode('gbk').encode("utf-8")
            agentlogfile = cf1.get("main", "agentlogfile").decode('gbk').encode("utf-8")
            MyUtil.DBIP = cf1.get("main", "DBIP").decode('gbk').encode("utf-8")
            MyUtil.DBPort = cf1.get("main", "DBPort").decode('gbk').encode("utf-8")          
            LOG = os.path.join(agentpath,agentlogfile)
            #创建日志实例
            log = MyUtil.CLogInfo(LOG)        
            
            cf = ConfigParser.ConfigParser()
            cf.read(MyUtil.cur_file_dir()+"\\auto.ini")
            #强制读取配置文件中的IP地址设置，当前的问题是第一次必须手工更改配置文件中的IP，否则传出的IP错误
            innerIP = cf.get("Configuration", "localip").decode('gbk').encode("utf-8")            
            try:
                CPUCores = cf.get("Configuration","cpucores").decode('gbk').encode("utf-8")
                CPUCores = int(CPUCores)
            except:
                CPUCores = int('1')

            rc = runCron()
            rc.run()
        except:
            #print "main Error:"+str(sys.exc_info()[0])+str(sys.exc_info()[1])
            pass
     
        
if __name__ == '__main__':
        win32serviceutil.HandleCommandLine(ServiceDoRun)
        #关闭日志 文件访问
        log.close()

