#!/usr/bin/python
#-*- coding:utf-8-*-
#code by HAWK.Li

import sys,os
import socket
import base64
import uuid
import zipfile
import ConfigParser
import binascii
import struct

import ServerInfo
import sitecustomize

def version(cmds,cmd):
    """MyUtil_version : 1.5_2012-03-12_Release
    """
    return version.__doc__

class CLogInfo():
    """日志记录模块
    """
    def __init__(self, logfile):
        try:
            import logging
            self.logger = None
            self.logger = logging.getLogger()
            self.hdlr = logging.FileHandler(logfile)
            formatter = logging.Formatter("[%(asctime)s] %(message)s", "%Y-%m-%d %H:%M:%S")
            self.hdlr.setFormatter(formatter)
            self.logger.addHandler(self.hdlr)
            self.logger.setLevel(logging.DEBUG)
        except:
            exit(1)

    def output(self,logInfo,errFlag=0):
        try:
            if (errFlag):
                #print "error:"+logInfo
                self.logger.error("error:"+logInfo)
            else:
                #print logInfo
                self.logger.info(logInfo)
        except:
            #print "log output error!"
            exit(1)

    def close(self):
        try:
            self.logger.removeHandler(self.hdlr)
        except:
            #print "log closed error!"
            exit(1)

class SendMsgToDB():
    """本模块负责发送消息到DBServer
    """
    def __init__(self):
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)    
        self.sock.connect((DBIP, int(DBPort)))
    
    def send(self,data):
        try:
            self.sock.sendall(data)
        except:
            #self.writeLog("SendMsgToDB.send Error:"+str(sys.exc_info()[0])+str(sys.exc_info()[1]))
            #print "SendMsgToDB.send Error:"+str(sys.exc_info()[0])+str(sys.exc_info()[1])
            pass
        
    def closeSock(self):
        self.sock.close()

def cur_file_dir():
    """获取脚本文件当前路径的方法
    """
    #获取脚本路径
    path = sys.path[0]
    #判断为脚本文件还是py2exe编译后的文件，如果是脚本文件，则返回的是脚本的目录
    #如果是py2exe编译后的文件，则返回的是编译后的文件路径
    if os.path.isdir(path):
        return path
    elif os.path.isfile(path):
        return os.path.dirname(path)
    
def splitCmd(cmd):
    """解析命令
    """
    try:
        cmdl = cmd.split(',')
        cmdmap = {}
        for c in cmdl:
            c = c.strip()
            if ''==c:
                continue
            else:
                result = c.split('=')
                if len(result)<2:
                    continue
                cmdmap[result[0]] = result[1]
        return cmdmap
    except:
        #print sys.exc_info()[0],sys.exc_info()[1]
        return '-2'

def mkpath(dir):
    """创建目录，并进入创建的目录中的方法
    """
    try:
        #检查目录是否存在否则创建
        if not os.path.exists(dir):
            os.mkdir(dir)
        #改变当前工作目录位置
        os.chdir(dir)
    except:
        return '-2'

def SecretKey():
    """定义secret_key加密字串
    """
    global secret_key
    try:
        cf = ConfigParser.ConfigParser()
        cf.read(cur_file_dir()+"\\key.ini")
        key = cf.get("main", "key")
        secret_key = binascii.b2a_base64(key)
        #如果读不到KEY，则强制指定一个KEY，但必须所有程序的配置 都一样，否则会出错无法通讯
        if secret_key == None:
            secret_key = 'UHV0WW91cktleUludG9UaGlzU3RyaW5n'
    except:
        secret_key = 'UHV0WW91cktleUludG9UaGlzU3RyaW5n'
        
class _secret():
    """TEA 加解密,  64比特明码, 128比特密钥
这个加解密算法是MIT授权，被授权人有权利使用、复制、修改、合并、出版发行、散布、再授权及
贩售软件及软件的副本。
这是一个确认线程安全的独立加密模块，使用时必须要有一个全局变量secret_key，要求大于等于16位
    """
    def xor(self,a, b):
        op = 0xffffffffL
        a1,a2 = struct.unpack('>LL', a[0:8])
        b1,b2 = struct.unpack('>LL', b[0:8])
        return struct.pack('>LL', ( a1 ^ b1) & op, ( a2 ^ b2) & op)
    
    def code(self,v, k):
        n=16
        op = 0xffffffffL
        delta = 0x9e3779b9L
        k = struct.unpack('>LLLL', k[0:16])
        y, z = struct.unpack('>LL', v[0:8])
        s = 0
        for i in xrange(n):
            s += delta
            y += (op &(z<<4))+ k[0] ^ z+ s ^ (op&(z>>5)) + k[1] 
            y &= op
            z += (op &(y<<4))+ k[2] ^ y+ s ^ (op&(y>>5)) + k[3] 
            z &= op
        r = struct.pack('>LL',y,z)
        return r

    def decipher(self,v, k):
        n = 16
        op = 0xffffffffL
        y, z = struct.unpack('>LL', v[0:8])
        a, b, c, d = struct.unpack('>LLLL', k[0:16])
        delta = 0x9E3779B9L
        s = (delta << 4)&op
        for i in xrange(n):
            z -= ((y<<4)+c) ^ (y+s) ^ ((y>>5) + d)
            z &= op
            y -= ((z<<4)+a) ^ (z+s) ^ ((z>>5) + b)
            y &= op
            s -= delta
            s &= op
        return struct.pack('>LL', y, z)

    def Encrypt(self,v):
        END_CHAR = '\0'
        FILL_N_OR = 0xF8
        vl = len(v)
        filln = (8-(vl+2))%8 + 2
        fills = ''
        for i in xrange(filln):
            fills = fills + chr(220)
        v = ( chr((filln -2)|FILL_N_OR)
              + fills
              + v
              + END_CHAR * 7)
        tr = '\0'*8
        to = '\0'*8
        r = ''
        o = '\0' * 8
        for i in xrange(0, len(v), 8):
            o = self.xor(v[i:i+8], tr)
            tr = self.xor( self.code(o, secret_key), to)
            to = o
            r += tr
        return base64.b64encode(r)
    
    def Decrypt(self,v):
        v=base64.b64decode(v)
        l = len(v)
        prePlain = self.decipher(v, secret_key)
        pos = (ord(prePlain[0]) & 0x07L) +2
        r = prePlain
        preCrypt = v[0:8]
        for i in xrange(8, l, 8):
            x = self.xor(self.decipher(self.xor(v[i:i+8], prePlain),secret_key ), preCrypt)
            prePlain = self.xor(x, preCrypt)
            preCrypt = v[i:i+8]
            r += x
        if r[-7:] != '\0'*7: 
            return None
        return r[pos+1:-7]

def getProperties(fname):
    """私有方法，分析文件的配置文件中的=号，以字典方式返回结果
    """
    try:
        f = open(fname,"r").readlines()
        map = {}
        #strip()
        length = len(f)
        for i in range(length):
            s = f[i][:len(f[i])-1]
            if not '=' in s:
                continue
            m = s.split('=')
            map[m[0]]=m[1]
        return map
    except:
        pass
        
def getComputerId():
    """获取本机的唯一标识，如果从未安装过，则自动从UUID和MAC计算一个新ID出来
取19位长，并保存在操作系统目录下windows/system32/agentid
    """
    try:
        if os.path.isfile(ServerInfo.sysDir()+"/agentid"):
            f = getProperties(ServerInfo.sysDir()+"/agentid")
            return f['agentid']
        else:
            uid = str(uuid.uuid1())
            mac = str(ServerInfo.GetinnerIPMac()[1])
            tempid = base64.b64encode(uid+'_'+mac)
            tempid = tempid[:18]
            f = open(ServerInfo.sysDir()+"/agentid","w")
            #加上一个回车符，否则会取agentid错误
            f.write('agentid='+tempid+'\n')
            f.close()
            return tempid
    except:
        return "getDiskId_error"

class ZFile(object):
    """zip解压/压缩文件的方法
    """
    def __init__(self, filename, mode='r', basedir=''):
        self.filename = filename
        self.mode = mode
        if self.mode in ('w', 'a'):
            self.zfile = zipfile.ZipFile(filename, self.mode, compression=zipfile.ZIP_DEFLATED)
        else:
            self.zfile = zipfile.ZipFile(filename, self.mode)
        self.basedir = basedir
        if not self.basedir:
            self.basedir = os.path.dirname(filename)
        
    def addfile(self, path, arcname=None):
        path = path.replace('\\', '/')
        if not arcname:
            if path.startswith(self.basedir):
                arcname = path[len(self.basedir):]
            else:
                arcname = ''
        self.zfile.write(path, arcname)
            
    def addfiles(self, paths):
        for path in paths:
            if isinstance(path, tuple):
                self.addfile(*path)
            else:
                self.addfile(path)
            
    def close(self):
        self.zfile.close()
        
    def extract_to(self, path):
        #print self,path
        output =""
        for p in self.zfile.namelist():
            output += self.extract(p, path)
        return output
            
    def extract(self, filename, path):
        if not filename.endswith('/') or not filename.endswith('\\'):
            f = os.path.join(path, filename)
            dir = os.path.dirname(f)
            if not os.path.exists(dir):
                os.makedirs(dir)
            file(f, 'wb').write(self.zfile.read(filename))
        sys = ServerInfo.getSYSTEM()
        if  sys == "Windows":
            return 'extract file: '+filename+" to "+"\\"+path+"\\ \n"
        else:
            return 'extract file: '+filename+" to "+"/"+path+"/ \n"
                 
        
def AddZIP(zfile, files):
    """创建zip压缩文件的方法，支持带目录的多文件，但不支持空目录
    注意是反斜杠，如果zip文件不存会自动创建
    AddZIP('c:/a.zip',['c:/2.txt','c:/updatefiles/AutoUpdateServer.log'])
    """
    try:
        z = ZFile(zfile, 'w')
        z.addfiles(files)
        z.close()
        return '1'
    except:
        return '-1',str(sys.exc_info()[0])+str(sys.exc_info()[1])
    
def UnZIP(zfile, path):
    """解压zip文件的方法，如果释放的目录不存在会自动创建
    UnZIP('c:/a.zip','d:/path')
    """
    try:
        #print zfile
        z = ZFile(zfile)
        output = z.extract_to(path)
        z.close()
        return '1',output
    except:
        return '-1',str(sys.exc_info()[0])+str(sys.exc_info()[1])
    
def makeMD5(path1):
    """本模块临时使用，用于生成配置文件中所有文件的MD5
    print makeMD5("e:\\agent\\")
    """
    filelist = os.listdir(path1)
    out =""
    for files in filelist:
        print "filename=",path1+files
        #if os.path.isfile(files):
        f = file(path1+files, 'rb')
        out += files+":"+sumfile(f)+","
    return out

SecretKey()
