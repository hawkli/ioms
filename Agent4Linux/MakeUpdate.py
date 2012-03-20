#!/usr/bin/python
#-*- coding:utf-8-*-
#本程序生成配置文件和可用于更新的压缩文件

import os,sys
import time,shutil
import md5,platform
import sitecustomize
import zipfile

def version(cmds,cmd):
    """update_version : 1.5_2012-03-20_Release
    """
    return version.__doc__

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

def cur_file_dir():
    '''获取脚本文件当前路径的方法
    '''
    #获取脚本路径
    path = sys.path[0]
    #判断为脚本文件还是py2exe编译后的文件，如果是脚本文件，则返回的是脚本的目录
    #如果是py2exe编译后的文件，则返回的是编译后的文件路径
    if os.path.isdir(path):
        return path
    elif os.path.isfile(path):
        return os.path.dirname(path)

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
    
def getSYSTEM():
    """返回操作系统(windows,linux)，此处用于区分程序运行在何系统下Windows/Linux"""
    return platform.system()

  
def makeMD5(path1):
    """本模块用于生成config.ini配置文件中所有文件的MD5
    print makeMD5("/root/src/agent/")
    """
    filelist = os.listdir(path1)
    out =""
    for files in filelist:
        print "filename=",path1+files
        #if os.path.isfile(files):
        f = file(path1+files, 'rb')
        out += files+":"+sumfile(f)+","
    return out

if __name__ == '__main__':
    #输入目标目录
    directory = raw_input('Enter absolute path directory: ')
    #生成MD5
    md5str = makeMD5(directory)
    Pmd5str = "md5Files = "+md5str[0:len(md5str)-1]
    #创建配置文件
    fileHandle = open ( 'config.ini', 'w' )  
    fileHandle.write("[filemd5]\n")
    fileHandle.write(Pmd5str+"\n")
    fileHandle.write("\n")
    fileHandle.write("[main]\n")
    fileHandle.write("updateAgentService = yes\n")
    fileHandle.write("updateCMDServer = yes\n")
    fileHandle.write("RunPrograms = no\n")
    fileHandle.write("removeFiles = no\n")
    fileHandle.write("\n")
    fileHandle.write("[end]\n")
    fileHandle.write("\n")
    fileHandle.close()
    #复制配置文件至目录中
    plat = getSYSTEM()
    if plat == "Linux":
        hf = '/'
    else:
        hf ='\\'
    print "copy config.ini to :",os.path.join(directory+hf+"config.ini")
    shutil.copy2("config.ini", os.path.join(directory+hf+"config.ini"))
    #压缩

    if plat == "Linux":
        filename = "update4Linux.zip"
    elif plat == "Windows":
        filename = "update.zip"
    else:
        file = "unknow.zip"
    os.chdir(directory)
    print "AddZIP",filename,os.listdir(directory)
    print AddZIP(filename,os.listdir(directory))
    print "Make "+directory+filename+" over." 
    #shutil.copy2("filename", os.path.join(directory+"\\"+filename))
