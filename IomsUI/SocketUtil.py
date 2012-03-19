#!/usr/bin/python
#-*- coding:utf-8-*-
#code by HAWK.Li

import sys
import socket
import ConfigParser
import MyUtil

def version(cmds,cmd):
    """SocketUtil_version : 1.5_2012-3-12_Release
    """
    return version.__doc__

class Socket():
    """socket操作类"""
    def __init__(self, host ,post):
        """初始化socket"""
        self.host = host
        self.post = post
        self.sockSize = 64000
    
    def connect(self):
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.sock.connect((self.host, self.post))
    
    def send(self, msg):
        """通过socket发送消息,发送前将消息加密"""
        try:
            #发现TEA加密方法似乎不支持utf8，要转成GBK
            msg1 = _3ds.Encrypt(msg.decode('utf-8').encode("GBK"))
            self.sock.sendall(msg1)
        except:
            print sys.exc_info()[0],sys.exc_info()[1]
            
    def sendFile(self, msg):
        """通过socket发送文件"""
        try:
            return self.sock.send(msg)
        except:
            print sys.exc_info()[0],sys.exc_info()[1]
            
    def recv(self):
        """通过socket获得消息"""
        try:
            self.response = self.sock.recv(self.sockSize)
            #_3ds.Decrypt(self.sock.recv(self.sockSize))
            return self.response
        except:
            print sys.exc_info()[0],sys.exc_info()[1]
    
    def close(self):
        """关闭socket"""
        self.sock.close()

#加密对象
_3ds = MyUtil._secret()
#读取配置文件
cf = ConfigParser.ConfigParser()
cf.read("data/IOMSUI.ini")

host = cf.get("main", "serverip")           #IOMS服务端IP
port = int(cf.get("main", "serverport"))    #IOMS服务端端口

#连接IOMS服务端的socket
serverSocket = Socket(host, port)
serverSocket.connect()
#-------------------------各消息解析方法-----------------------

def analysisData(data):
    """获得可下载文件列表的消息解析"""
    
    '''解析流程：
    1、判断是否为空
    2、以\n来split分割成列表
    3、判断列表长度，长度为1说明没有文件可以下载，长度大于1为有文件可以下载
    4、列表下标0的数据时一句描述，故循环从下标1开始
    5、数据由3块组成,以\t分割，第一部分为文件名，第二部分为文件MD5码，第三部分为文件大小
    6、其中每个部分的数据以 : 号可分成2部分，第一部分为描述，第二部分为实际内容
    '''
    fileList = []
    if data != None:
        #判断数据不为空
        _data = str(data).split("\n")
        if len(_data) > 1:
            del _data[0]
            for cdata in _data:
                value = cdata.split("\t")
                if len(value) > 1:
                    fileList.append([str(value[0]).split(":")[1],str(value[1]).split(":")[1],str(value[2]).split(":")[1]])
    return fileList
