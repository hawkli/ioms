#!/usr/bin/python
# -*- coding: utf-8 -*-
#检查配置文件，更改IP地址
#code by HAWK.Li
import ConfigParser
import os,sys,time,string

import MyUtil,ServerInfo
import sitecustomize

def version(cmds,cmd):
    """setupCfg_version : 1.12_2011-03_11_ALPHA
    """
    return version.__doc__
  
def writeCfgfile(setIP,setinnerMAC,setWAIIP,setOS,setCodeSet,setCPUCores,setHostname,setPlatform,setSysDir,setCPUInfo,setPHMEM):
    #强写本地IP地址到配置文件中去
    cf1 = ConfigParser.ConfigParser()
    cf1.read(MyUtil.cur_file_dir()+"/auto.ini")
    cf1.set("Configuration", "localIP", setIP)
    cf1.set("Configuration","localMACAddress",setinnerMAC)
    cf1.set("Configuration","OuterIP",setWAIIP)
    cf1.set("Configuration","OS",setOS)
    cf1.set("Configuration","CodeSet",setCodeSet)
    cf1.set("Configuration","CPUCores",setCPUCores)
    cf1.set("Configuration","hostname",setHostname)
    cf1.set("Configuration","Platform",setPlatform)
    cf1.set("Configuration","CPUInfo",setCPUInfo)
    cf1.set("Configuration","SystemDirectory",setSysDir)
    cf1.set("Configuration","Physicalmemory",setPHMEM)
    cf1.write(open(MyUtil.cur_file_dir()+"/auto.ini", "w"))
 
  
if __name__ == '__main__':
    try:
        #配置文件获取
        ipMac = ServerInfo.GetinnerIPMac()
        waiIP = ServerInfo.getWaiIP()
        innerIP = str(ipMac[0])
        innerMAC = str(ipMac[1])
        swaiIP = waiIP[0]
        setOS = ServerInfo.getOS()
        CodeSet = ServerInfo.codeset()
        Cores = ServerInfo.getCPUCores()
        sHostname = ServerInfo.hostname()
        sPlatform = ServerInfo.getSYSTEM()
        sCPUInfo = ServerInfo.cpuInfo()
        sSysDir = ServerInfo.sysDir()
        sPHMEM = str(ServerInfo.getPhyMem()[0])
        writeCfgfile(innerIP,innerMAC,swaiIP,setOS,CodeSet,Cores,sHostname,sPlatform,sSysDir,sCPUInfo,sPHMEM)
        print "CheckOK.检查配置文件完成".decode('utf-8')
    except:
        print "RunError.运行错误".decode('utf-8')
        print  str(sys.exc_info()[0]) + str(sys.exc_info()[1])
    

    
