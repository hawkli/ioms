#!/usr/bin/python
#-*- coding:utf-8-*-
#code by HAWK.Li

import MySQLdb
import sys
import sitecustomize

def version(cmds,cmd):
    """DBUtil_for_IOMServer_version : 1.5_2012-3-12_Release
    """
    return version.__doc__

class DBUtil():
    def __init__(self,DBName):
        try:
            self.connection = MySQLdb.connect(host=DBHost, user=DBUser, passwd=DBPwd, db=DBName, port=int(DBPort), charset='utf8')
            self.cursor = self.connection.cursor()
            self.cursor.execute("SET NAMES utf8")
            self.cursor.execute("SET CHARACTER_SET_CLIENT=utf8")
            self.cursor.execute("SET CHARACTER_SET_RESULTS=utf8")
        except:
            print u"创建数据库连接失败"
            print u"DB.init Error"+str(sys.exc_info()[0])+str(sys.exc_info()[1])
    
    def getData(self,sql,value):
        """查询数据
        sql = "select account,password,role from user"
        result = db.getData(sql)
        for r in result:
            print r[0],'\t',r[1],'\t',r[2]"""
        try:
            if value==None or len(value)==0:
                self.cursor.execute(sql)
            else:
                self.cursor.executemany(sql,value)
            result = self.cursor.fetchall()
            return result
        except:
            print u"查询数据出错"
            print u"select Error"+str(sys.exc_info()[0])+str(sys.exc_info()[1])
    
    def insert(self,sql,value):
        """插入数据
        value为一个list可以批量插入数据 value=[["123","123"],["321","321"]]
        sql = "insert into user(account,password,role) values(%s,%s,%s)"
        value = []
        for i in range(4,8):
            val = ['user'+str(i),"123","超级管理员".encode('utf-8')]
            value.append(val)
        db.insert(sql, value)
        """
        try:
            self.cursor.executemany(sql,value)
        except:
            print u"数据批量插入出错"
            print u"insert Error"+str(sys.exc_info()[0])+str(sys.exc_info()[1])
    
    def update(self,sql,value):
        """删,改
        sql = "delete from user"
        value = []
        db.update(sql, value)"""
        try:
            if  value==None or len(value)==0:
                self.cursor.execute(sql)
            else:
                self.cursor.executemany(sql,value)
            return True
        except:
            print u"数据更改出错"
            print u"update Error"+str(sys.exc_info()[0])+str(sys.exc_info()[1])
            return False
        
    def closeConn(self):
        try:
            self.connection.close()
        except:
            print u"数据库连接关闭出错"
            print u"DB.close Error"+str(sys.exc_info()[0])+str(sys.exc_info()[1])
    
    def commit(self):
        self.connection.commit()
        
class User():
    """用户相关数据库操作"""
    
    def Check(self, name, password):
        """通过用户名和密码匹配是否存在"""
        myrow=DBUtil('ioms_user')
        sql = "select account,account from user where account=%s and password=%s "
        result = myrow.getData(sql,[[name,password]])
        myrow.closeConn()
        return result
    
    def actionLog(self, name, action, result, ip):
        """用户操作在数据库中插入日志"""
        myrow=DBUtil('ioms_user')
        sql = "insert into user_action_log(account, action, result, ip_address, time) values(%s, %s, %s, %s, NOW())"
        flag = myrow.insert(sql, [[name, action, result, ip]])
        myrow.closeConn()
        return flag

class Server():
    """服务器相关数据库操作"""
    
    def getAllServerList(self):
        """获得所有服务器的列表"""
        myrow = DBUtil('ioms_monitor')
        sql = "select agent_id,server_ip_lan,server_ip_wan,server_mac_lan,server_type,server_hostname,server_codeset,server_systemdir,server_template,HW_CPU_num,HW_CPU_info,HW_RAM_info,HW_DISK_info,HW_sn,HW_RACK,HW_IDC_address,HW_admin,HW_admin_phone,HW_type from server_list order by server_template"
        result = myrow.getData(sql, None)
        myrow.closeConn()
        return result

    def getAllActiveServerList(self):
        """获得所有三分钟活动的服务器列表"""
        myrow = DBUtil('ioms_monitor')
        sql = "select agent_id,server_ip_lan,server_ip_wan,server_mac_lan,server_type,server_hostname,server_codeset,server_systemdir,server_template,HW_CPU_num,HW_CPU_info,HW_RAM_info,HW_DISK_info,HW_sn,HW_RACK,HW_IDC_address,HW_admin,HW_admin_phone,HW_type from server_list where agent_id in (select agent_id from active_server where HB_time > now() - INTERVAL 3 MINUTE) order by server_template"
        result = myrow.getData(sql, None)
        myrow.closeConn()
        return result
    
    def updateServerInfo(self, serverInfo, serverDistribute):
        """修改服务器可供修改的相关信息"""
        myrow=DBUtil('ioms_monitor')
        sql = "update server_list set HW_sn = %s, HW_RACK = %s, HW_IDC_address = %s, HW_admin = %s, HW_admin_phone = %s, HW_type = %s , HW_distribute = %s where agent_id = %s"
        flag = myrow.update(sql, [[serverInfo[13], serverInfo[14], serverInfo[15], serverInfo[16], serverInfo[17], serverInfo[18], serverDistribute, serverInfo[0]]])
        myrow.closeConn()
        return flag
    
    def updateServerGC(self, serverGCList, serverDistribute):
        """修改服务器为回收站状态"""
        myrow=DBUtil('ioms_monitor')
        sql = "update server_list set HW_distribute = %s where agent_id in (" + serverGCList +")"
        flag = myrow.update(sql, [[serverDistribute]])
        myrow.closeConn()
        return flag
    
    def getServerCpuInfo(self, agentId, startTime, endTime):
        """获得服务器CPU活动信息"""
        myrow = DBUtil('ioms_monitor')
        sql = "select CPU_load,log_time from server_monitor where agent_id = %s and log_time >= %s and log_time < %s order by log_time"
        result = myrow.getData(sql, [[agentId, startTime, endTime]])
        myrow.closeConn()
        return result
    def getUnassignedServerList(self):
        """获得未分配设备"""
        myrow = DBUtil('ioms_monitor')
        sql = "select a.agent_id,a.server_ip_lan,a.server_ip_wan,a.server_type,a.server_hostname,b.HB_time,a.achieve_time from server_list as a,active_server as b where a.agent_id = b.agent_id and HW_distribute = 0"
        result = myrow.getData(sql, None)
        myrow.closeConn()
        return result
    def getPysicalServerList(self,area):
        """获得物理模式下设备列表"""
        myrow = DBUtil('ioms_monitor')
        sql = "select distinct a.HW_RACK,a.agent_id,a.server_ip_lan,a.server_ip_wan,a.server_type,a.server_hostname,b.HB_time,a.achieve_time from server_list as a ,active_server as b where a.agent_id = b.agent_id and HW_distribute = 1 and a.HW_IDC_address = %s order by a.HW_RACK asc"
        result = myrow.getData(sql, [[area]])
        myrow.closeConn()
        return result
    def getMonitorServerList(self,area,subject):
        """获得监视模式设备列表"""
        myrow = DBUtil('ioms_monitor')
        sql = "select distinct a.agent_id,a.HW_RACK,a.HW_type,a.server_type,a.server_ip_lan,a.server_ip_wan,b.HB_time,a.HW_CPU_info,a.HW_RAM_info,a.HW_DISK_info,a.HW_sn,a.achieve_time from server_list as a ,active_server as b where a.agent_id = b.agent_id and HW_distribute = 1"
        if area == "None":
            pass
        else:
            sql += " and HW_IDC_address = '"+[area][0]+"'"
        if subject == "None":
            pass
        else:
            sql += " and HW_type = '"+ [subject][0]+"'"
        print sql
        result = myrow.getData(sql, None)
        myrow.closeConn()
        return result
class Dir():
    def getDirList(self):
        """获得所有的目录列表"""
        myrow = DBUtil('ioms_info')
        sql = "select dir2_id,dir1_name,dir2_name,dir_template from dir_list"
        result = myrow.getData(sql, None)
        myrow.closeConn()
        return result

