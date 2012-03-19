#!/usr/bin/python
#-*- coding:utf-8-*-
#code by HAWK.Li

import xml.etree.ElementTree as ET
import os
import sys
import DBUtil

def version(cmds,cmd):
    """ServerList_version : 1.5_2012-3-12_Release
    """
    return version.__doc__

#把服务器列表查询出来放入列表对象中
AllServerList = []
#获得所有服务器类型配置
root_tree = ET.parse('data/ServerOptioninfo.xml')
root_doc = root_tree.getroot()

AllDirList = []

def initAllServerList(self):
    """初始化所有在线三分钟服务器列表"""
    del AllServerList[:]
    #生成数据库操作类
    server = DBUtil.Server()
    #获得所有服务器
    _allServerList = server.getAllActiveServerList()
    for _allServer in _allServerList:
        sinServerList = []
        for _server in _allServer:
            sinServerList.append(_server)
        AllServerList.append(sinServerList)
    print AllServerList
            
class ServerClassList():
    """服务器列表相关类"""
    def Resurn_list(self):
        """返回服务器类型树"""
        
        initAllServerList(self)
        ServerList_KEY=[]
        serverclass=[]
        serverapp=[]
        for root_child in root_doc:
            serverclass.append(root_child[0].text)
            serverapp=[]
            serverclass.append(serverapp)
            ServerList_KEY.append(serverclass)
            serverclass=[]
        return ServerList_KEY
    
class ServerFunction():
    """服务器相关方法"""
    def __init__(self):
        """初始化方法"""
        #服务器列表初始化
        self.serverlist=[]
        #服务器分类(一级分类)标志
        self.root_child_id=""
        
    def SelectServerList(self,root_server):
        """点击服务器类型，显示该类型下的所有服务器"""
        initAllServerList(self)
        #判断选择的是否是一级类别，如果是则获取id值;
        for root_child in root_doc:
            if root_child[0].text==root_server:
                self.root_child_id=root_child.get('id')
                break;
        
        #递归出当前选择的服务器类别/应用类别一致的服务器wip清单;
        self.allServerList = AllServerList
        for server_child in self.allServerList:
            server_template = server_child[8].split(",")
            for _server_template in server_template:
                if _server_template==self.root_child_id or _server_template==root_server:
                    self.serverlist.append(server_child[1]+'_'+server_child[0])

    def getServerList(self):
        """返回服务器列表"""
        return self.serverlist
    def getUnassignedServerList(self):
        """获得未分配设备列表"""
        unassignedServerList = []
        server = DBUtil.Server()
        unassignedServerList = server.getUnassignedServerList()
        for items in unassignedServerList:
            items.insert(0,u'□')
        return unassignedServerList
    def getPysicalServerList(self,area):
        """获得物理模式下设备列表"""
        pysicalServerList = []
        tem_list = []
        server = DBUtil.Server()
        pysicalServerList = server.getPysicalServerList(area)
        for items in pysicalServerList:
            tem_list.append(items[0][1:3])
            items.insert(0,u'□')
            
        #空机柜，无效数据填充 写的较麻烦
        tem_list = list(set(tem_list))
        pysicalServerList.sort(key=lambda x:x[1])
        for tem in tem_list:
            for i in range(1,8):
                for items in pysicalServerList:
                    if items[1][1:3]==str(tem):
                        if items[1][4:] == str(i):
                            tem_item = items
                            pysicalServerList.remove(items)
                            break
                        else:
                            tem_item = [u'□','A'+str(tem),' ',' ',' ',' ',' ',' ',' ']
                            break
                else:
                    tem_item = [u'□','A'+str(tem),' ',' ',' ',' ',' ',' ',' ']
                pysicalServerList.append(tem_item)
        return pysicalServerList
    def getMonitorServerList(self,list=None):
        """获得监控模式下设备列表"""
        monitorServerList = []
        server = DBUtil.Server()
        monitorServerList = server.getMonitorServerList(list)
        for items in monitorServerList:
            items[2]=unicode(str(items[2]),"utf-8")#解决转换成exe后，所属项目栏乱码问题
            items.insert(0,u'□')
        return monitorServerList    

class dirList():
    def getDirList(self):
        del AllDirList[:]
        #生成数据库操作类
        dir = DBUtil.Dir()
         #获得所有服务器
        _allDirList = dir.getAllDirList()
        for _allDir in _allDirList:
            sinDirList = []
            for _dir in _allDir:
                sinDirList.append(_dir)
            AllDirList.append(sinDirList)
        return AllDirList