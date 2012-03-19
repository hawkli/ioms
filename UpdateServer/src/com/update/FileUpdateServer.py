#!/usr/bin/python
#-*- coding:utf-8-*-
#code by HAWK.Li

from xml.dom import minidom
import codecs

import SocketServer, time,os
import md5
import string
import ConfigParser
import sys
import MyUtil
import sitecustomize

def version(cmds,cmd):
    """FileUpdateServer_version : 1.5_2012-3-12_Release
    """
    return version.__doc__

def sumfile(fobj):
    """检查文件的MD5"""
    m = md5.new()
    while True:
        d = fobj.read(8096)
        if not d:
            break
        m.update(d)
    return m.hexdigest()

def md5sum(fname):
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
                return '-1'
            finally:
                f.close()
                return fname+' '+ret
        else:
            return '-2'
    except:
        print "md5sum Error:"+str(sys.exc_info()[0])+str(sys.exc_info()[1])
        writeLog("md5sum Error:"+str(sys.exc_info()[0])+str(sys.exc_info()[1]))
        return '-2'

def fileMd5(fname):
    """从XML获取文件的md5码"""
    try:
        ret = fileMap[fname]
        ret2 = fileSizeMap[fname]
        return fname+' '+ret#+' '+ret2
    except:
        print "fileMd5 Error:"+str(sys.exc_info()[0])+str(sys.exc_info()[1])
        writeLog("fileMd5 Error:"+str(sys.exc_info()[0])+str(sys.exc_info()[1]))
        return '-2'

def getFileSize(fname):
    filesize = int(os.path.getsize(fname))
    if filesize < 1024:
        FS = str(filesize)+"Bytes"
    elif filesize >= 1024 and filesize < 1048576:
        FS = str("%.2f"%(filesize/1024.0))+"KB"
    elif filesize >= 1048576:
        FS = str("%.2f"%(filesize/1024.0/1024.0))+"MB"
    return FS

class MyServer(SocketServer.BaseRequestHandler):
    """接收来自客户端的文件验证请求和文件下载请求AutoUgrade
接收到的命令格式为：
au,cmd=downloads,file=filename 从指定IP的端口下载文件至本机的目录下
au,cmd=dir 查看本机提供的可下载文件列表
au,cmd=uploads,file=filename 远程机器上传文件至本机
au,cmd=remove,file=filename 删除文件
au,cmd=genmd5 重新生成所有可下载文件的md5码
        """
    def handle(self):
        try:
            while True:
                #receivedData = self.rfile.readline().strip()
                #只接收使用 sock.sendall这样发过来的命令，不接受直接命令
                receivedData = self.request.recv(sockSize)
                if not receivedData or not receivedData.startswith('au'):
                    print receivedData
                    break
                cmdmap = self.AuSplitCmd(receivedData)
                #检查是否正常发给autoupgrage的指令
                client_address = self.client_address[0]
                keys = cmdmap.keys()
                if not 'cmd' in keys:
                    break
                cmd = cmdmap['cmd']
                if 'downloads'==cmd and 'file' in keys:#下载文件
                    filename = str(cmdmap['file'])
                    print str(time.strftime('[%Y-%m-%d_%H:%M:%S] ')+'|['+client_address+']|'+'发起下载请求').decode('utf-8').encode("gbk")
                    writeLog('|['+client_address+']|'+'发起下载请求')
                    #提供服务端指定文件下载
                    result = fileMd5(filename)#md5sum(filename)
                    self.request.sendall(result)
                    writeLog('|['+client_address+']|'+'下载前MD5验证，结果为: '+str(result))
                    #如果检验返回-1或-2说明文件有问题，不提供下载
                    if result == '-1' or result == '-2':
                        print str(time.strftime('[%Y-%m-%d_%H:%M:%S] ')+'|['+client_address+']|'+'请求下载失败: '+str(result)).decode('utf-8').encode("gbk")
                        writeLog('|['+client_address+']|'+'请求下载失败: '+str(result))
                        break
                    sfile = open(filename, 'rb')
                    while True:
                        data = sfile.read(10485760)
                        if not data:
                            break
                        while len(data) > 0:
                            intSent = self.request.send(data)
                            data = data[intSent:]
                    self.request.send('4423718C61C4E8A4362D955BBC7B9711')
                    #self.request.send('EOF')
                    sfile.close()
                    print str(time.strftime('[%Y-%m-%d_%H:%M:%S] ')+'|['+client_address+']|'+'请求下载完成: '+str(result)).decode('utf-8').encode("gbk")
                    writeLog('|['+client_address+']|'+'请求下载完成: '+str(result))
                    break
                elif 'dir'==cmd:#查看可以下载的文件
                    print str(time.strftime('[%Y-%m-%d_%H:%M:%S] ')+'|['+client_address+']|'+'发起请求,查看可下载文件').decode('utf-8').encode("gbk")
                    writeLog('|['+client_address+']|'+'发起请求,查看可下载文件')
                    files = ''
                    for key in fileMap.keys():
                        files += 'file:%s\tMd5:%s\tSize:%s\n' % (str(key),str(fileMap[key]),str(fileSizeMap[key]))
                        print "file:"+str(key),"MD5:"+str(fileMap[key]),"Size:"+str(fileSizeMap[key])
                    if files=='':
                        files = '-1'
                    self.request.sendall(files)
                elif 'uploads'==cmd and 'file' in keys:#上传文件
                    print str(time.strftime('[%Y-%m-%d_%H:%M:%S] ')+'|['+client_address+']|'+'发起请求,上传文件 '+cmdmap['file']).decode('utf-8').encode("gbk")
                    writeLog('|['+client_address+']|'+'发起请求,上传文件 '+cmdmap['file'])
                    #文件已存在，禁止上传
                    if cmdmap['file'] in fileMap.keys():
                        self.request.sendall('-1')
                        break
                    self.request.sendall(cmdmap['file'])
                    MyUtil.mkpath(path)
                    Fname = os.path.join(path,cmdmap['file'])
                    f = open(Fname, 'wb')
                    i = 0
                    while True:
                        data = self.request.recv(10485760)
                        print "Receviced files...接受文件中。。。。".decode('utf-8').encode("gbk"),'  ',i, len(data)
                        i+=1
                        if not data:
                            print "All File Receviced complete.文件全部接受完成".decode('utf-8').encode("gbk")
                            break
                        if str(data).endswith('4423718C61C4E8A4362D955BBC7B9711'):
                            data = data[:len(data)-len('4423718C61C4E8A4362D955BBC7B9711')]
                            print "All File Receviced complete.文件全部接受完成".decode('utf-8').encode("gbk")
                            f.write(data)
                            break
                        print "Write File...写入文件中。。。".decode('utf-8').encode("gbk")
                        f.write(data)
                        print "Write File complete.写入文件完成".decode('utf-8').encode("gbk")
                    f.flush()
                    f.close()
                    FMD5 = string.split(md5sum(Fname))
                    addXml(cmdmap['file'], FMD5[1],getFileSize(Fname))
                    print str(time.strftime('[%Y-%m-%d_%H:%M:%S] ')+'|['+client_address+']|'+'上传文件完成 FMD5：'+FMD5[1]).decode('utf-8').encode("gbk")
                    writeLog('|['+client_address+']|'+'上传文件完成 FMD5：'+FMD5[1])
                elif 'remove'==cmd and 'file' in keys:#删除文件
                    print str(time.strftime('[%Y-%m-%d_%H:%M:%S] ')+'|['+client_address+']|'+'发起请求,删除文件 '+cmdmap['file']).decode('utf-8').encode("gbk")
                    writeLog('|['+client_address+']|'+'发起请求,删除文件 '+cmdmap['file'])
                    MyUtil.mkpath(path)
                    if os.path.isfile(cmdmap['file']) and cmdmap['file'] in fileMap.keys():
                        print str(time.strftime('[%Y-%m-%d_%H:%M:%S] ')+'|['+client_address+']|'+'删除文件 '+cmdmap['file']+'完成').decode('utf-8').encode("gbk")
                        writeLog('|['+client_address+']|'+'删除文件 '+cmdmap['file']+'完成')
                        FMD5 = string.split(fileMd5(cmdmap['file']))
                        removeXml(FMD5[0], FMD5[1])
                        os.remove(cmdmap['file'])
                        self.request.sendall('1')
                    else:
                        writeLog('|['+client_address+']|'+'文件不存在')
                        self.request.sendall('-1')
                elif 'genmd5'==cmd:#重新生成文件MD5
                    print str(time.strftime('[%Y-%m-%d_%H:%M:%S] ')+'|['+client_address+']|'+'发起请求,重新生成所有文件的MD5码').decode('utf-8').encode("gbk")
                    writeLog('|['+client_address+']|'+'发起请求,重新生成所有文件的MD5码')
                    try:
                        for key in fileMap.keys():
                            md5 = md5sum(key)
                            fileMap[key] = string.split(md5)[1]
                            fileSizeMap[key] = getFileSize(key)
                        genXML()
                        self.request.sendall("1")
                        print str(time.strftime('[%Y-%m-%d_%H:%M:%S] ')+'|['+client_address+']|'+'重新生成所有文件的MD5码完成').decode('utf-8').encode("gbk")
                        writeLog('|['+client_address+']|'+'重新生成所有文件的MD5码完成')
                    except:
                        self.request.sendall("-1")
                        writeLog('|['+client_address+']|'+'重新生成所有文件的MD5码失败')
            self.request.close()
            writeLog('|['+client_address+']|'+'断开链接.')
        except:
            print "MyServer.handle Error:"+str(sys.exc_info()[0])+str(sys.exc_info()[1])
            writeLog("MyServer.handle Error:"+str(sys.exc_info()[0])+str(sys.exc_info()[1]))
        
    def AuSplitCmd(self,cmd):
        """解析命令--updateserver专用版本
        """
        cmdl = cmd.split(',')
        cmdmap = {}
        for c in cmdl:
            c = c.strip()
            if c.startswith('au') or ''==c:
                continue
            else:
                result = c.split('=')
                if len(result)<2:
                    continue
                cmdmap[result[0]] = result[1]
        return cmdmap

def writeLog(info):
    """记录日志
    """
    log.output(info)
    

def readFileXML():
    """读取文件md5配置
    """
    try:
        doc = minidom.parse(path+"\\"+fileXml)
        root = doc.documentElement
        filelist = root.getElementsByTagName("file")
        for file in filelist:
            fileMap[file.getAttribute('name')] = file.getAttribute('md5')
            fileSizeMap[file.getAttribute('name')] = file.getAttribute('size')
    except:
        print "readFileXML Error:"+str(sys.exc_info()[0])+str(sys.exc_info()[1])
        writeLog("readFileXML Error:"+str(sys.exc_info()[0])+str(sys.exc_info()[1]))
    

def addXml(fname,md5,size):
    """上传文件时，更改xml文件
    """
    try:
        doc = minidom.parse(path+"\\"+fileXml)
        dom = minidom.Document()
        dom.encoding = 'utf-8'
        dom.appendChild(doc.documentElement)
        root = dom.documentElement
        add = dom.createElement("file")
        add.setAttribute("id",str(len(fileMap.keys())+1))
        add.setAttribute("name",fname)
        add.setAttribute("md5",md5)
        add.setAttribute("size",size)
        root.appendChild(add)
        wf = open(path+"\\"+fileXml,"w")
        writer = codecs.lookup('utf-8')[3](wf)
        dom.writexml(writer)#dom.writexml(writer,'\n')
        writer.close()
        fileMap[fname] = md5
        fileSizeMap[fname] = size
    except:
        print "addXml Error:"+str(sys.exc_info()[0])+str(sys.exc_info()[1])
        writeLog("addXml Error:"+str(sys.exc_info()[0])+str(sys.exc_info()[1]))

def removeXml(fname,md5):
    """删除文件时，删除xml中的信息
    """
    try:
        doc = minidom.parse(path+"\\"+fileXml)
        dom = minidom.Document()
        dom.encoding = 'utf-8'
        dom.appendChild(doc.documentElement)
        root = dom.documentElement
        childs = root.getElementsByTagName("file")
        for child in childs:
            if child.getAttribute("name")==fname and child.getAttribute("md5")==md5:
                root.removeChild(child)
                fileMap.pop(fname)
                fileSizeMap.pop(fname)
        wf = open(path+"\\"+fileXml,"w")
        writer = codecs.lookup('utf-8')[3](wf)
        dom.writexml(writer)#dom.writexml(writer,'\n')
        writer.close()
    except:
        print "removeXml Error:"+str(sys.exc_info()[0])+str(sys.exc_info()[1])
        writeLog("removeXml Error:"+str(sys.exc_info()[0])+str(sys.exc_info()[1]))
 
def genXML():
    """重新生成md5的时，重新生成xml
    """
    try:
        doc = minidom.parse(path+"\\"+fileXml)
        dom = minidom.Document()
        dom.encoding = 'utf-8'
        dom.appendChild(doc.documentElement)
        root = dom.documentElement
        childs = root.getElementsByTagName("file")
        for child in childs:
            root.removeChild(child)
        i = 1
        for key in fileMap.keys():
            add = dom.createElement("file")
            add.setAttribute("id",str(i))
            add.setAttribute("name",key)
            add.setAttribute("md5",fileMap[key])
            add.setAttribute("size",fileSizeMap[key])
            root.appendChild(add)
        wf = open(path+"\\"+fileXml,"w")
        writer = codecs.lookup('utf-8')[3](wf)
        dom.writexml(writer)#dom.writexml(writer,'\n')
        writer.close()
    except:
        print "genXML Error:"+str(sys.exc_info()[0])+str(sys.exc_info()[1])
        writeLog("genXML Error:"+str(sys.exc_info()[0])+str(sys.exc_info()[1]))

def makeXML(XMLFILE):
    """创建一个空的XML文件
    """
    try:
        f = open(XMLFILE ,"w")
        f.write('<?xml version="1.0" ?><files></files>\n')
        f.close()
    except:
        print "makeXML Error:"+str(sys.exc_info()[0])+str(sys.exc_info()[1])


if __name__ == '__main__':
    global sockSize
    sockSize = 64000
    global fileXml
    fileXml = "file.xml"   
    Cfgfile="conf\\AUServer.ini"
    try:
        global fileMap,fileSizeMap
        fileMap = {}
        fileSizeMap = {}
        cf = ConfigParser.ConfigParser()
        if os.path.isfile(Cfgfile):
            cf.read(Cfgfile)
        else:
            pass
        global path
        path = cf.get("main", "path")
        logfile = cf.get("main", "logfile")
        serverIP = cf.get("main", "IP")
        port = cf.getint("main", "port")
    
        if not os.path.isdir(path):
            #创建上传 文件存放目录和日志文件的目录
            MyUtil.mkpath(path)
            #创建一个空的XML
            makeXML(path+"\\"+fileXml)
        global LOG,log
        LOG = os.path.join(path,logfile)
        #创建日志实例
        log = MyUtil.CLogInfo(LOG)
    
        readFileXML()
    
        log.output('FileUpdateServer启动')
        print u'FileUpdateServer启动'
        MyUtilVer=MyUtil.version.__doc__
        print version.__doc__,MyUtilVer
        print u"FileUpdateServerIP %s   PORT:%s"%(serverIP,port)
        srv = SocketServer.ThreadingTCPServer((serverIP, int(port)), MyServer)
        srv.serve_forever()
        log.close()
    except:
        print "start Error:"+str(sys.exc_info()[0])+str(sys.exc_info()[1])
        writeLog("start Error:"+str(sys.exc_info()[0])+str(sys.exc_info()[1]))
        log.close()
