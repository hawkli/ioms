#!/usr/bin/python
#-*- coding:utf-8-*-
#code by HAWK.Li

import base64
import ConfigParser
import sys,os,time
import socket
import getpass

import MyUtil
import sitecustomize

def version(cmds,cmd):
    """IOMClient_version : 1.5_2012-3_12_Release
    """
    return version.__doc__

class Client():
    """封装客户端核心方法
    """
    def login(self,user,pwd):
        """登录"""
        try:
            self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.sock.connect((host, port))
            msg = 'cmd=login,user='+user+',pwd='+pwd
            msg = _3ds.Encrypt(msg)
            self.sock.sendall(msg)
            self.response = self.sock.recv(sockSize)
            return self.response
        except:
            print "登录出错！".decode('utf-8').encode("gbk")
            print "Client.login Error:"+str(sys.exc_info()[0])+str(sys.exc_info()[1])
    
    def enterCmd(self,cmd):
        """登录成功，进入登录解释行
        """
        try:
            if 'cmd=uploads' in cmd:
                self.uploadFile(cmd,MyUtil.splitCmd(cmd))
            else:
                cmd = _3ds.Encrypt(cmd)
                self.sock.sendall(cmd)
                self.response = self.sock.recv(sockSize)
                result = self.response
                result = result.decode('utf-8').encode("gbk")
                print result
        except:
            print "enterCmd Error:"+str(sys.exc_info()[0])+str(sys.exc_info()[1])
                
    def uploadFile(self,cmdstr,cmd):
        """上传文件至updateServer的方法
        """
        try:
            if not 'file' in cmd.keys():
                print "参数不完整，缺少文件名".decode('utf-8').encode("gbk")
                return
            filename = cmd['file']
            Cname= ''.join(filename.split())
            if Cname <> filename:
                print "文件名有空格不支持".decode('utf-8').encode("gbk")
                return
            if not 'localpath' in cmd.keys():
                print "必须输入本地文件地址".decode('utf-8').encode("gbk")
                return 
            path_ = cmd['localpath']
            if not path_[len(path_)-1:]=="\\":
                path_ +="\\"
            if not os.path.isfile(path_+filename):
                print "文件不存在！".decode('utf-8').encode("gbk")
                return
            cmdstr = _3ds.Encrypt(cmdstr)
            self.sock.sendall(cmdstr)
            self.response = self.sock.recv(sockSize)
            if self.response==cmd['file']:
                print "可以上传文件 %s".decode('utf-8').encode("gbk") % cmd['file']
                print "开始上传....".decode('utf-8').encode("gbk")
                
                ulfile = open(path_+cmd['file'],'rb')
                #文件传输使用10M缓存，提高传输速度
                while True:
                    data = ulfile.read(10485760)
                    if not data:
                        break
                    while len(data) > 0:
                        intSent = self.sock.send(data)
                        data = data[intSent:]
                self.sock.send('4423718C61C4E8A4362D955BBC7B9711')
                print "上传完成。".decode('utf-8').encode("gbk")
            elif self.response=='-1':
                print "文件名已存在！".decode('utf-8').encode("gbk")
            else:
                print "不能上传文件 %s".decode('utf-8').encode("gbk") % cmd['file']
        except:
            print "上传文件出错".decode('utf-8').encode("gbk")
            print "uploadFile Error:"+str(sys.exc_info()[0])+str(sys.exc_info()[1])
        
    def closeSock(self):
        self.sock.close()
        
def loginCheck(uiusername = None, uiuserpass = None):
    """登录验证方法
    """
    global isLogin
    isLogin = "false"
    try:
        while isLogin=="false":
            username = ""
            userpass = ""
            if uiusername != None:
                username = uiusername
            else:
                username=raw_input(u"账号:".encode('gbk'))
            if uiuserpass != None:
                userpass = uiuserpass
            else:
                userpass=getpass.getpass(u"password:".encode('gbk'))
            r = client.login(username, userpass)
            if r == '1':
                print "登录成功！".decode('utf-8').encode("gbk")
                isLogin = "true"
                break
            elif r == '-1':
                uiusername = None
                uiuserpass = None
                print "登录失败,请重新登录！".decode('utf-8').encode("gbk")
            else:
                uiusername = None
                uiuserpass = None
        enter()
    except:
        print "loginCheck Error:"+str(sys.exc_info()[0])+str(sys.exc_info()[1])

def enter():
    """进入命令行模式
    """
    try:
        while isLogin=="true":
            if not isLogin:
                print "登录状态不正确！".decode('utf-8').encode("gbk")
                break
            cmd = raw_input(">")
            client.enterCmd(cmd)
        #登录状态为false，进入登录验证
        loginCheck()
    except:
        print "enter Error:"+str(sys.exc_info()[0])+str(sys.exc_info()[1])

if __name__ == "__main__":
    print "-"*50
    print "IOMClient"
    print "-"*50
    global host,port,client,sockSize,_3ds
    sockSize = 64000
    _3ds = MyUtil._secret()
    
    cf = ConfigParser.ConfigParser()
    cf.read("IOMClient.ini")
    
    host = cf.get("main", "serverip")
    port = int(cf.get("main", "serverport"))
    
    client = Client()
    
    #判断是否是从UI层进入客户端，如果是，直接使用UI系统的账号密码登陆
    args = sys.argv
    if args != None:
        argslen = len(args)
        if argslen >= 3:
            loginCheck(args[1], args[2])
        else:
            print "请登录".decode('utf-8').encode("gbk")
            loginCheck()
    else:
        print "请登录".decode('utf-8').encode("gbk")
        loginCheck()
    
    
    
    
    