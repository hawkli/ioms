#!/usr/bin/python
#-*- coding:utf-8-*-

"""
返回服务器的各种信息
"""
import re,urllib2
import socket
import os,time
import platform
import psutil
import sitecustomize

def version(cmds,cmd):
    """ServerInfo_version : 1.5_2011_03_12_Release
    """
    return version.__doc__

def getCPUUsage():
    """获取cpu使用率，此程序取的似乎是第一个CPU的使用率，多核下情况还待观察"""
    return psutil.cpu_percent(interval=1.0)

def getCPUCores():
    """取CPU核数，仅python2.6以上版本支持
    """
    import multiprocessing
    cores = multiprocessing.cpu_count()    
    return cores

def visit(url):
    opener = urllib2.urlopen(url)
    if url == opener.geturl():
        str = opener.read()
    return re.search('\d+\.\d+\.\d+\.\d+',str).group(0)

def getWaiIP():
    """返回外网卡ip地址和外网卡MAC地址"""
    waiIP = "None"
    waiMAC = "None"
    sys = getSYSTEM()
    if  sys == "Windows":   
        import wmi 
        c = wmi.WMI()
        interfaces = c.Win32_NetworkAdapterConfiguration(IPEnabled=True)
        for interface in interfaces:
            pat = re.compile(r'\d{0,3}\.\d{0,3}\.\d{0,3}\.\d{0,3}')
            ip=re.findall(pat,str(interface.IPAddress))
            if ip[0].startswith('172.18') or ip[0].startswith('172.20') or ip[0].startswith('192.168')or ip[0].startswith('10.') or ip[0].startswith('0.0.') or ip[0].startswith('127.0.'):
                pass
            else:
                waiIP = ip[0]
                waiMAC = str(interface.MACAddress)

    elif sys == "Linux":
        """linux的取IP和MAC的设计是仔细分析了反馈的结果，对一台有二个网卡，其中一个网卡绑了二个IP
所有IP地址中又有内网，又有外网的服务器做了分析，设计为取为不是内网IP地址的第一个真实网卡上的外网地址
        """
        try:
            ipLine = "ifconfig | grep 'inet addr' | awk -F: '{print $2}' | awk '{print $1}' | grep -v 127.0.0.1 "
            ips = os.popen(ipLine).read()
            ip = ips.split('\n')
            macLine = "ifconfig | grep HWaddr | awk -F' ' '{print $5}'"
            macs = os.popen(macLine).read()
            mac = macs.split('\n')
            J=0
            for wip in ip:
                if wip:
                    if wip.startswith('172.18') or wip.startswith('172.20') or wip.startswith('192.168')or wip.startswith('10.') or wip.startswith('0.0.') or wip.startswith('127.0.'):
                        J=J+1
                    else:
                        waiIP = wip
                        waiMAC = mac[J]
                        break
        except:
            pass
    else:
        pass
    return waiIP,waiMAC

def GetinnerIPMac():
    """获取内网IP地址及内网卡的Mac地址"""
    innerIP ="None"
    innerMAC ="None"    
    sys = getSYSTEM()
    if  sys == "Windows":    
        import wmi
        c = wmi.WMI()
        interfaces = c.Win32_NetworkAdapterConfiguration(IPEnabled=True)
        for interface in interfaces:
            pat = re.compile(r'\d{0,3}\.\d{0,3}\.\d{0,3}\.\d{0,3}')
            ip=re.findall(pat,str(interface.IPAddress))
            if ip[0].startswith('172.18') or ip[0].startswith('172.20') or ip[0].startswith('192.168')or ip[0].startswith('10.'):
                innerIP = ip[0]
                innerMac = str(interface.MACAddress)

    elif sys == "Linux":
        try:
            ipLine = "ifconfig | grep 'inet addr' | awk -F: '{print $2}' | awk '{print $1}' | grep -v 127.0.0.1 "
            ips = os.popen(ipLine).read()
            ip = ips.split('\n')
            macLine = "ifconfig | grep HWaddr | awk -F' ' '{print $5}'"
            macs = os.popen(macLine).read()
            mac = macs.split('\n')
            J=0
            for iip in ip:
                if iip:
                    if iip.startswith('172.18') or iip.startswith('172.20') or iip.startswith('192.168')or iip.startswith('10.') or iip.startswith('0.0.') or iip.startswith('127.0.'):
                        innerIP = iip
                        innerMAC = mac[J]
                        break
                    else:
                        J=J+1
        except:
            pass
    else:
        pass
    return innerIP,innerMAC
def getOS():
    """返回操作系统版本(windows,linux)"""
    return platform.platform()

def getSYSTEM():
    """返回操作系统(windows,linux)，此处用于区分程序运行在何系统下Windows/Linux"""
    return platform.system()

def hostname():
    """获取主机名(windows,linux)"""
    try:
        hostname = socket.getfqdn(socket.gethostname())
        return str(hostname)
    except:
        return 'Unkown_hostname'

def sysDir():
    """获取系统目录(windows/linux)如果是linux，则特指指程序运行的目录"""
    lines="None"
    sys = getSYSTEM()
    if  sys == "Windows":
        lines = os.getenv('WINDIR')+"\\system32"
    elif sys == "Linux":
        lines = os.getcwd()
    return str(lines)
      
def cpuInfo():
    """cpu型号信息(windows)/linux"""
    CPUINFO = "None"
    sys = getSYSTEM()
    if  sys == "Windows":
        import wmi
        c = wmi.WMI ()
        for cpu in c.Win32_Processor():
            lines = cpu.Name
            CPUINFO = lines.strip()
    elif sys == "Linux":
        try:        
            infos = "cat /proc/cpuinfo | grep 'model name' | awk -F: '{print $2}'"
            info = os.popen(infos).read()
            CPUINFO = info.strip()
        except:
            pass
    else:
        pass
    return CPUINFO

def getPhyMem():
    """取本机的物理内存，可用物理内存，剩余可用物理内存，单位K
    """
    phymem = int(psutil.TOTAL_PHYMEM)/1024
    availphymem = int(psutil.avail_phymem())/1024
    usedphymem = int(psutil.used_phymem())/1024
    return phymem,availphymem,usedphymem

def codeset():
    """服务器语言代码(windows)/linux"""
    codeset = "None"
    sys = getSYSTEM()
    if  sys == "Windows":
        import wmi
        lines = os.popen('wmic os get codeset').readlines()
        codeset = lines[1][:len(lines[1])-1].strip()
    elif sys == "Linux":
        try:  
            codecmd = "cat /etc/sysconfig/i18n | grep 'LANG=' | awk -F= '{print $2}'"
            code1 = os.popen(codecmd).read()
            codeset = code1.split('"')[1]
        except:
            pass
    else:
        pass
    return codeset

def getDiskWarning():
    """windows各硬盘可用空间低于10%，并小于5G的返回告警
        Linux所有挂载目录空闲大于85%以上，返回告警
    """
    warning = "None"
    sys = getSYSTEM()
    if  sys == "Windows":
        try:
            c = wmi.WMI ()
            for disk in c.Win32_LogicalDisk (DriveType=3):
                #各盘剩余空间百分比
                freePercent = 100.0 * long (disk.FreeSpace) / long (disk.Size)
                #各盘剩余空间折算为G
                freeSpace = float(disk.FreeSpace)/1024/1024/1024
                #小于10%可用空间，并且可用空间低于5G的列出
                if int(freePercent) <= int(10):
                    if int(freeSpace) < int(5):
                        warning= "%s free %0.2fG, %0.2f%%" % (disk.Caption,freeSpace,freePercent)
                    else:
                        warning='normal'
                else:
                    warning='normal'        
        except:
            warning='getDiskWarningError'
    elif sys == "Linux":
        try:
            #小于85$空间可用率的列出
            diskcmd = "df | awk '/\<(08[5-9]|9[0-9]|100)% +/'"
            warning = os.popen(diskcmd).read()
            if warning:
                pass
            else:
                warning = 'normal'
        except:
            warning='getDiskWarningError'
    else:
        pass
    return warning



def getProcessInfo(p): 
    """取出指定进程占用的进程名，进程ID，进程实际内存, 虚拟内存,CPU使用率
发现psutil取出的进程CPU使用率，需要除CPU个数，否则不准，这里没有除CPU个数，需要自行处理
    """
    try:
        cpu = int(p.get_cpu_percent(interval=0)) 
        rss, vms = p.get_memory_info() 
        name = p.name 
        pid = p.pid 
    except psutil.error.NoSuchProcess, e:
        name = "Closed_Process"
        pid = 0
        rss = 0
        vms = 0
        cpu = 0
    return [name.upper(), pid, rss, vms, cpu]

def getAllProcessInfo():
    """取出全部进程的进程名，进程ID，进程实际内存, 虚拟内存,CPU使用率
    """
    instances = []
    all_processes = list(psutil.process_iter()) 
    for proc in all_processes: 
        proc.get_cpu_percent(interval=0) 
    #此处sleep1秒是取正确取出CPU使用率的重点
    time.sleep(1) 
    for proc in all_processes: 
        instances.append(getProcessInfo(proc))
    return instances

def getAllProcessName():
    """返回所有进程的名字
    """
    instances = []
    all_processes = list(psutil.process_iter()) 
    for proc in all_processes: 
        instances.append(proc.name.upper())
    return instances

def getAllProcessNameId():
    """返回所有进程的名字和pid，将取代getAllProcessName
    """
    instances = []
    all_processes = list(psutil.process_iter())
    for proc in all_processes:
        nameid = [proc.name.upper(),proc.pid]
        instances.append(nameid)
    return instances

def Kill_Process_pid(pid):
    '''杀掉指定PID的进程'''
    try:
        p = psutil.Process(pid)
        processkill = p.kill()
    except:
        pass

def getDirSize(dir):
    '''获取目录大小'''
    size = 0L
    for root, dirs, files in os.walk(dir):
        size += sum([os.path.getsize(os.path.join(root, name)) for name in files])
    return size

def getInfos():
    ipMac = GetinnerIPMac()
    waiIP = getWaiIP()
    #cpuInfo()
    return ipMac[0]+";"+waiIP[0]+";"+ipMac[1]+";"+getOS()+";"+hostname()+";"+sysDir()+";"+cpuInfo()+";"+str(getPhyMem()[0])+";"+codeset()

#if __name__ == '__main__':
#    print GetinnerIPMac()
#    print getWaiIP()
    