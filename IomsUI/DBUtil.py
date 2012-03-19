#!/usr/bin/python
#-*- coding:utf-8-*-
#code by HAWK.Li
#数据库操作相关,通过socket连接从iomserver端获得数据
#这个文件与服务端的功能不同，可能需要考虑重命名，避免理解上的误区

import sys
import SocketUtil

def version(cmds,cmd):
    """DBUtil_for_IOMSUI_version : 1.5_2012-3-12_Release
    """
    return version.__doc__

class User():
    """用户相关数据库操作"""
    
    def Check(self, name, password):
        """通过用户名和密码匹配是否存在"""
        SocketUtil.serverSocket.send("cmd=dbutil,parm=checkUser;" + name + ";" + password)
        result = SocketUtil.serverSocket.recv();
        return result
    
    def actionLog(self, name, action, result, ip):
        """用户操作在数据库中插入日志"""
        SocketUtil.serverSocket.send("cmd=dbutil,parm=actionLog;" + name + ";" + action + ";" + result + ";" + ip)
        return True

class Server():
    """服务器相关数据库操作"""
    
    def getAllServerList(self):
        """获得所有服务器的列表"""
        SocketUtil.serverSocket.send("cmd=dbutil,parm=getAllServerList")
        result = SocketUtil.serverSocket.recv();
        if result != None and result != "" and result != "None":
            AllServerList = []
            list = result.split(";;")
            for _list in list:
                AllServerList.append(_list.split(",,"))
            return AllServerList
        else:
            return []

    def getAllActiveServerList(self):
        """获得所有服务器的列表"""
        SocketUtil.serverSocket.send("cmd=dbutil,parm=getAllActiveServerList")
        result = SocketUtil.serverSocket.recv();
        if result != None and result != "" and result != "None":
            AllServerList = []
            list = result.split(";;")
            for _list in list:
                AllServerList.append(_list.split(",,"))
            return AllServerList
        else:
            return []
    
    def updateServerInfo(self, serverInfo, serverDistribute):
        """修改服务器可供修改的相关信息"""
        SocketUtil.serverSocket.send("cmd=dbutil,parm=updateServerInfo;" + serverInfo[0] + ";" + serverInfo[13] + ";" + serverInfo[14] + ";" + serverInfo[15] + ";" + serverInfo[16] + ";" + serverInfo[17] + ";" + serverInfo[18] + ";" + serverDistribute)
        result = SocketUtil.serverSocket.recv();
        return bool(result)
    
    def updateServerGC(self, serverAgentIds):
        """修改服务器为回收站状态"""
        length = len(serverAgentIds)
        serverGCInfo = "cmd=dbutil,parm=updateServerGC;"
        for j in range(length):
            serverGCInfo += serverAgentIds[j]
            if j < length - 1:
                serverGCInfo += ";"
        SocketUtil.serverSocket.send(serverGCInfo)
        result = SocketUtil.serverSocket.recv();
        return bool(result)                  
    
    def getServerCpuInfo(self, agentId, startTime, endTime):
        """获得服务器CPU活动信息"""
        SocketUtil.serverSocket.send("cmd=dbutil,parm=serverCpuCurve;" + agentId + ";" + startTime + ";" + endTime)
        result = SocketUtil.serverSocket.recv();
        if result != None and result != "" and result != "None":
            serverList = []
            list = result.split(";;")
            for _list in list:
                serverList.append(_list.split(",,"))
            return serverList
        else:
            return []
    def getUnassignedServerList(self):
        """未分配设备列表"""
        SocketUtil.serverSocket.send("cmd=dbutil,parm=getAllUnassignedServerList")
        result = SocketUtil.serverSocket.recv();
        if result != None and result != "" and result != "None":
            AllServerList = []
            list = result.split(";;")
            for _list in list:
                AllServerList.append(_list.split(",,"))
            return AllServerList
        else:
            return []
    def getPysicalServerList(self,area):
        """获得物理模式下设备列表"""
        SocketUtil.serverSocket.send("cmd=dbutil,parm=getPysicalServerList;"+str(area))
        result = SocketUtil.serverSocket.recv();
        if result != None and result != "" and result != "None":
            AllServerList = []
            list = result.split(";;")
            for _list in list:
                AllServerList.append(_list.split(",,"))
            return AllServerList
        else:
            return []
    def getMonitorServerList(self,list=None):
        """监控显示模式设备列表"""
        info = "cmd=dbutil,parm=getMonitorServerList"
        if list == None:
            pass
        else:
            for item in list:
                info += ";"+str(item)
        SocketUtil.serverSocket.send(info)
        result = SocketUtil.serverSocket.recv();
        if result != None and result != "" and result != "None":
            AllServerList = []
            list = result.split(";;")
            for _list in list:
                AllServerList.append(_list.split(",,"))
            return AllServerList
        else:
            return []
class Dir():
    """菜单相关操作"""
    def getAllDirList(self):
        """获得所有菜单列表"""
        SocketUtil.serverSocket.send("cmd=dbutil,parm=getAllDirList")
        result = SocketUtil.serverSocket.recv();
        if result != None and result != "" and result != "None":
            AllDirList = []
            list = result.split(";;")
            for _list in list:
                AllDirList.append(_list.split(",,"))
            return AllDirList
        else:
            return []
        