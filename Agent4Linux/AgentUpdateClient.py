#!/usr/bin/python
# -*- coding: utf-8 -*-

import sys
import socket, time,string,os,subprocess
import ConfigParser,shutil
import md5
import MyUtil,ServerInfo
import sitecustomize

global serverIp,serverPort
serverIp = ""
serverPort = 50000

def version():
    """AgentUpdateClient4Linux_version : 1.50_2012-03-20_Release
    """
    pass

def sumfile(fobj):
    """检查文件的MD5
    """
    m = md5.new()
    while True:
        d = fobj.read(8096)
        if not d:
            break
        m.update(d)
    return m.hexdigest()

def md5sum(fname):
    """生成文件md5
    """
    #其他类型错误，例如目录是否空，返回-2
    try:
        MyUtil.mkpath(path)
        #给文件名前加上绝对地址，避免出错
        Fname=os.path.join(path,fname)
        #检查文件是否存在，如果存后返回其MD5值，如果不存在返回-1
        if os.path.isfile(Fname):
            try:
                f = file(Fname, 'rb')
                ret = sumfile(f)
            except:
                return '-1',"none"
            finally:
                f.close()
                return fname+' '+ret
        else:
            return '-1',"none"
    except:
        return '-2',"none"

class Client(): 
    """下载文件模块
    """
    def __init__(self):
        self.host = serverIp
        self.port = serverPort
        self.sockSize = 64000
   
    def downfile(self,filename,cmdStr):
#        """下载文件
#        """
#        try:
            jieguo = ""
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.connect((self.host,self.port ))
            sock.sendall('au,'+cmdStr)
            self.response = sock.recv(self.sockSize)
            l = string.split(self.response)
            #如果返回有文件名，而且一致，说明有MD5码
            if l[0] == filename:
                returnMD5=l[1]
                #确认本地存放路径
                MyUtil.mkpath(path)
                # 'please wait...'
                Fname = os.path.join(path,filename)
                f = open(Fname, 'wb')
                #print '开始下载。。。'
                i = 0
                while True:
                    data = sock.recv(10485760)
                    #print '接受文件中。。。。','  ',i
                    i+=1
                    if not data:
                        break
                    if str(data).endswith('4423718C61C4E8A4362D955BBC7B9711'):
                        data = data[:len(data)-len('4423718C61C4E8A4362D955BBC7B9711')]
                        f.write(data)
                        break
                    f.write(data)
                f.flush()    
                f.close()
                #print '接受完毕。。。。'
                FMD5 = string.split(md5sum(Fname))
                if FMD5[0] > int("0"):
                    if FMD5[1] == returnMD5:
                        if 'updateself' in cmdStr:
                            jieguo = 2
                        else:
                            jieguo = 1
                    else:
                        jieguo = -2
                else:
                    jieguo = -3

            elif l[0] == '-1':
                jieguo = -4
            elif l[0] == '-2':
                jieguo = -5
            else:
                jieguo = -6
                
            sock.close()
            #print jieguo
            return jieguo
            
#        except:
#            print "Client.downfile Error:"+str(sys.exc_info()[0])+str(sys.exc_info()[1])
#            updateselflog("Client.downfile Error:"+str(sys.exc_info()[0])+str(sys.exc_info()[1]))
#            
def downloads(cmd,cmdStr):
    """下载文件方法，返回状态位0＝1成功，返回负数失败
    """
    global path
    path = ""
    try:
        if not 'file' in cmd.keys():
            return '-1', 'Lost filename.'
        dlfilename = cmd['file']
        Cname= ''.join(dlfilename.split())
        if Cname <> dlfilename:
            return '-1', 'Filename has space.'
        if not 'path' in cmd.keys():
            return '-1', 'Specify the file address.'
        if os.path.isdir(cmd['path']) and not '.' in cmd['path']:
            if cmd['path'].endswith('/'):
                path = cmd['path']
            else:
                path = cmd['path']+"/"
        else:
            return '-1', 'Path does not exist.\n'
        client = Client()
        result = client.downfile(dlfilename,cmdStr)
        jieguo = 'Unkown Error.\n'
        if result == int("1"):
            jieguo = 'download complete.'
        elif result == int("2"):
            jieguo = 'update.zip download complete.'
        elif result == int("-2") or result == int("-3"):
            jieguo = 'MD5 check failed, please downloads again.'
        elif result == int("-4"):
            jieguo = 'transfer error.'
        elif result == int("-5"):
            jieguo = 'file not found.'
        elif result == int("-6"):
            jieguo = 'ClientDownload Error.'
        else:
            result == '-1'
        #print result,jieguo
        return result,jieguo
    except:
        print "Client.downloads Error:"+str(sys.exc_info()[0])+str(sys.exc_info()[1])
        updateselflog("Client.downloads Error:"+str(sys.exc_info()[0])+str(sys.exc_info()[1]))

def updateSelf(cmd,cmdStr):
    """2011-01-13 update self
    """
    try:
        print "updateself step 1"
        path = MyUtil.cur_file_dir()
        cmdStr = "cmd=downloads,file=update4Linux.zip,updateself=updateself,path="+path
        cmd = MyUtil.splitCmd(cmdStr)
        reStr = downloads(cmd, cmdStr)
        if reStr[0] == int('-1'):
            return reStr[1]
        rs =""
        print "updateself step 2 ", reStr
        if reStr[0] == int('2'):
            """解压update.zip至当前目录下的update.tmp中"""
            zipout = MyUtil.UnZIP("update4Linux.zip", "update.tmp")
            print "updateself step 3 unzip. zipout = ",zipout[0]
            if zipout[0] == '1':
                rs += zipout[1]
            '''检验update.tmp/config.ini是否存在'''
            if os.path.isfile("update.tmp/config.ini"):
                print "updateself step 4 check config.ini"
                '''读取config.ini的配置'''
                cf = ConfigParser.ConfigParser()
                cf.read("update.tmp/config.ini")
                md5Files = cf.get("filemd5","md5Files")
                uAgent = cf.get("main", "updateAgentService")
                uCMDServer = cf.get("main", "updateCMDServer")
                uRunPro = cf.get("main", "RunPrograms")
                uremove = cf.get("main", "removeFiles")

                '''对需要的文件做MD5验证，通过则下一步'''
                md5FilePath = (MyUtil.cur_file_dir()+"/update.tmp/")
                _md5Files = md5Files.split(',')
                MD5Flag = False
                if _md5Files != None and md5FilePath != None and _md5Files != '' and md5FilePath != '':
                    for filemd5 in _md5Files:
                        '''循环比对指定文件的MD5码值'''
                        fileName,rightMD5 = filemd5.split(":")
                        filePath = md5FilePath + fileName
                        ret = string.split(md5sum(filePath))
                        if ret[0] == "-1" or ret[0] == "-2":
                            MD5Flag = False
                        elif ret[1] == rightMD5:
                            MD5Flag = True
                    print "updateself step 5 check MD5, MD5Flag =",MD5Flag
                    if MD5Flag:
                        '''根据配置运行'''
                        print "updateself step 6 update Agent4Linux =",uAgent.upper()
                        if uAgent.upper() == "YES":
                            '''如果要更新Agent，则先杀掉进程，调用自更新脚本复制文件和启动服务'''
                            _allpronameid = ServerInfo.getAllProcessNameId()
                            for _name,_id in _allpronameid:
                                if _name.upper() == "Agent4Linux".upper():
                                    p = ServerInfo.Kill_Process_pid(_id)
                                    str1 = "find process "+str(_name)+", pid = "+str(_id)+", kill it!\n"
                                    rs += str1
                            try:
                                os.chmod(MyUtil.cur_file_dir()+"/updateself.sh",0755)
                                p = os.popen(MyUtil.cur_file_dir()+"/updateself.sh")
                                str1 = p.readlines()
                                for s in str1:
                                    rs += s
                                p.close()
                            except:
                                print "updateAgent4LinuxError:"+str(sys.exc_info()[0]) + str(sys.exc_info()[1])
                                pass
                        print "updateself step 7, RunProcess= ",uRunPro.upper()
                        if uRunPro.upper() <> "NO" :
                            """如果不是NO，则把要运行的程序绝对路径和执行名放在参数中，以逗号隔开
                            """
                            try:
                                Pros = uRunPro.split(",")
                                for Pro in Pros:
                                    p = os.popen(Pro)
                                    str1 = p.readlines()
                                    for s in str1:
                                        rs += s
                                    p.close()                                     
                            except:
                                pass
                        
                        print "updateself step 8, RemoveFile= ",uremove.upper()
                        """如果不是NO，则把要删除的文件绝对路径放在参数中，以逗号隔开
                        """
                        if uremove.upper() <> "NO":
                            try:
                                removefiles = uremove.split(",")
                                for rfile in removefiles:
                                    shutil.rmtree(rfile)
                            except:
                                pass
                        
                        print "updateself step 9, Update CMDServer4Linux = ",uCMDServer.upper()
                        if uCMDServer.upper() == "YES":
                            '''如果需要更新CMDServer4Linux，调用updateCMDServer.sh完成更新'''
#                            _allpronameid = getAllProcessNameId()
#                            for _name,_id in _allpronameid:
#                                if _name.upper() == "CMDServer4Linux".upper():
#                                    p = Kill_Process_pid(_id)
#                                    str1 = "find process "+str(_name)+", pid = "+str(_id)+", kill it!\n"
#                                    rs += str1
                            try:
                                os.chmod(MyUtil.cur_file_dir()+"/updateCMDServer.sh",0755)
                                p = os.popen(MyUtil.cur_file_dir()+"/updateCMDServer.sh")
                                str1 = p.readlines()
                                for s in str1:
                                    rs += s
                                p.close()
                            except:
                                print "updateCMDServerError:"+str(sys.exc_info()[0]) + str(sys.exc_info()[1])
                                pass
                                                       
                        print "updateself step 10, remove update.tmp."
                        if os.path.isdir(md5FilePath):
                            '''全部运行完毕，删除tmp文件目录'''
                            shutil.rmtree(md5FilePath)

                        #return "1",rs
                        return rs
                    else:
                        #return "-1","MD5 check failed!文件MD5码验证与配置不一致!"
                        return "MD5 check failed!文件MD5码验证与配置不一致!"
                            
                else:
                    #return "-1","config.ini md5Files is null.配置文件中没有需要比对的文件."
                    return "config.ini md5Files is null.配置文件中没有需要比对的文件."
                
            else:
                #return "-1","config.ini not found.更新配置文件未找到."
                return "config.ini not found.更新配置文件未找到."
            
        else:
            return reStr
    except:
        updateselflog("Client.updateSelf:"+str(sys.exc_info()[0])+str(sys.exc_info()[1]))
        print sys.exc_info()[0],sys.exc_info()[1]
    finally:
        if os.path.isdir(md5FilePath):
            '''删除tmp文件目录'''
            shutil.rmtree(md5FilePath)
            
def updateselflog(data):
    """写日志方法
    """
    f = open(MyUtil.cur_file_dir()+"/updateself.log","w")
    f.write(data)
    f.close()
    
#if __name__ == '__main__':
#    serverIp = "172.18.165.253"
#    serverPort = 50000
#    aa = updateSelf(1,2)
#    print aa[1].decode('utf-8').encode("gbk")