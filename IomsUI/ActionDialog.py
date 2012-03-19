#!/usr/bin/python
#-*- coding:utf-8-*-
#code by HAWK.Li

import wx
import os
import time
from wx.lib.stattext import GenStaticText as StaticText
import SocketUtil

def version(cmds,cmd):
    """ActionDialog_version : 1.5_2012-03-12_Release
    """
    return version.__doc__

class ActionDialog(wx.Dialog):
    """对话框父类"""
    def __init__(self, dialogTitle):
        """设置默认的宽高位450,400,设置背景颜色为#eeeeee"""
        wx.Dialog.__init__(self, parent=None, id=-1,  size=(450, 400), title = dialogTitle)
        self.actionPanel = wx.Panel(self, -1, pos=wx.Point(0, 0), size=wx.Size(450, 400), style=wx.TAB_TRAVERSAL)
        self.actionPanel.SetBackgroundColour("#eeeeee")
        
 
class DownLoadFileDialog(ActionDialog):
    """下载文件的对话框"""
    def __init__(self, fileName, downLoadFileServerList):
        """初始方法"""
        
        #保存成临时变量
        self.fileName = fileName
        self.downLoadFileServerList = downLoadFileServerList
        ActionDialog.__init__(self, u"文件下载")
        
        StaticText(self.actionPanel, -1, u"您确认要对选择的服务器进行下载文件的操作吗？",(80, 80))
        
        StaticText(self.actionPanel, -1, u"请输入保存路径:",(80, 120))
        
        self.savePath = wx.TextCtrl(self.actionPanel, -1, "", (80, 140), size=(250, 20))
        
        #操作中提示
        self.actiontext=StaticText(self.actionPanel, -1, u"正在操作,请稍等...", (160, 250))
        self.actiontext.Show(False)
        
        self.ok = wx.Button(self.actionPanel, -1, u"确   定", (100, 200))
        self.ok.SetForegroundColour("#006699")
        self.cancel = wx.Button(self.actionPanel, -1, u"取   消", (230, 200))
        self.cancel.SetForegroundColour("#006699")

        #确定、取消事件
        self.ok.Bind(wx.EVT_LEFT_DOWN,self.OnDisplayInfo)
        self.ok.Bind(wx.EVT_LEFT_UP, self.OnOk)
        self.Bind(wx.EVT_BUTTON, self.OnCancel, self.cancel)
    
    def OnDisplayInfo(self, event):
        """显示操作信息"""
        self.actiontext.Show(True)
        
    def OnOk(self, event):
        """确定方法,开始发送下载命令"""
        
        #获得用户填写的文件保存路径
        self.savePath = self.savePath.GetValue()
        if self.savePath != None and self.savePath != "":
            #判断路径不为空后，准备循环选中的服务器列表
            if self.downLoadFileServerList != None:
                #判断服务器不为空后，组合命令的前半段
                cmd = "cmd=downloads,file="+str(self.fileName)+",path="+(self.savePath)+",serverip="
                self.response = ''
                for server in self.downLoadFileServerList:
                    #循环对命令追加每个服务器的IP
                    cmd += server.split("_")[0]
                    cmd += ";"
                if cmd.endswith(";"):
                    cmd = cmd[:len(cmd)-1]
                SocketUtil.serverSocket.send(str(cmd))
                #接收消息,获得下载命令的返回结果
                self.response += SocketUtil.serverSocket.recv(); """需要修改IOMSERVER的返回值以方便做判断"""
                self.response += '\n'
                self.EndModal(wx.ID_OK)
            else:
                wx.MessageBox(u'没有选择服务器。', u"提示")
                self.EndModal(wx.ID_CANCEL)
        else:
            wx.MessageBox(u'请输入保存路径。', u"提示")
            self.savePath.SetFocus()
            self.actiontext.Show(False)
            return
    
    def OnCancel(self, event):
        """取消方法"""
        self.EndModal(wx.ID_CANCEL)  
    
    def OnGetResponseInfo(self):
        """获得下载文件命令的返回消息"""
        return self.response
    
class UpLoadsFileDialog(ActionDialog):
    """上传文件的对话框"""
    def __init__(self, parent):
        """初始方法 parent为父对象"""
        self.parent = parent
        '''
        self.parent.SysMessaegText.WriteText
        使用父对象的消息框输出消息
        '''
        ActionDialog.__init__(self, u"文件上传")
        
        StaticText(self.actionPanel, -1, u"您确认要对选择的文件进行上传吗？",(80, 80))
        
        StaticText(self.actionPanel, -1, u"请选择文件:",(80, 120))
        
        self.filePath = wx.TextCtrl(self.actionPanel, -1, "", (80, 140), size=(250, 20))
        
        self.Open = wx.Button(self.actionPanel, -1, u"浏览...", (350, 140), size=(60, 20))
        self.Open.SetForegroundColour("#ffffff")
        self.Open.SetBackgroundColour("#154786")
        
        self.Bind(wx.EVT_BUTTON, self.OnOpenbutton,self.Open)
        
        #操作中提示
        self.actiontext=StaticText(self.actionPanel, -1, u"正在操作,请稍等...", (160, 250))
        self.actiontext.Show(False)
        
        self.ok = wx.Button(self.actionPanel, -1, u"确   定", (100, 200))
        self.ok.SetForegroundColour("#006699")
        self.cancel = wx.Button(self.actionPanel, -1, u"取   消", (230, 200))
        self.cancel.SetForegroundColour("#006699")

        #确定、取消事件
        self.ok.Bind(wx.EVT_LEFT_DOWN,self.OnDisplayInfo)
        self.ok.Bind(wx.EVT_LEFT_UP, self.OnOk)
        self.Bind(wx.EVT_BUTTON, self.OnCancel, self.cancel)
    
    def OnOpenbutton(self, event):
        """[打开]按钮方法(调用打开文件对话框)"""
        dlg = wx.FileDialog(self, message=u"选择上传文件",defaultDir=os.getcwd(),defaultFile="",style=wx.OPEN | wx.MULTIPLE | wx.CHANGE_DIR)
        if dlg.ShowModal() == wx.ID_OK:
            self.Importfilename = dlg.GetPaths()
            self.filePath.SetValue("%s" % (self.Importfilename[0]))
        dlg.Destroy()
        
    def OnDisplayInfo(self, event):
        """显示操作信息"""
        self.actiontext.Show(True)
        
    def OnOk(self, event):
        """确定方法,开始发送上传文件命令"""
        
        #获得用户选择的文件路径
        _filePath = self.filePath.GetValue()
        
        #-----------判断文件名中是否带有空格，如有空格提示不支持--------------
        #判断用户选择的目录分割时\还是/符号，以便用来分割取文件名
        _path = _filePath.split("\\")
        pathSplitLen = len(_path)
        if(pathSplitLen > 1):
            pass
        else:
            _path = _filePath.split("/")
            pathSplitLen = len(_path)
            if(pathSplitLen > 1):
                pass
        fileNameIndex = pathSplitLen - 1
        fileNamet = ""
        filePatht = ""
        for i in range(pathSplitLen):
            if(i == fileNameIndex):
                fileNamet = _path[i]
            else:
                filePatht += _path[i] + "\\"
        Cname= ''.join(fileNamet.split())
        if Cname <> fileNamet:
            wx.MessageBox(u"文件名有空格不支持", u"提示")
            self.actiontext.Show(False)
            return
        #-----------判断文件是否存在-------------------------
        if not os.path.isfile(_filePath):
            wx.MessageBox(u'文件不存在。', u"提示")
            self.actiontext.Show(False)
            return
        #组合上传文件命令
        cmd = "cmd=uploads,localpath=" + filePatht + ",file=" + fileNamet
        SocketUtil.serverSocket.send(str(cmd))
        #接收消息,获得上传文件命令的返回结果
        self.response = SocketUtil.serverSocket.recv(); """需要修改IOMSERVER的返回值以方便做判断"""
        if self.response == fileNamet:
            #self.parent.SysMessaegText.WriteText(u"可以上传文件 %s\n" % fileNamet)
            #self.parent.SysMessaegText.WriteText(u"开始上传....\n")
            
            ulfile = open(filePatht + fileNamet,'rb')
            while True:
                data = ulfile.read(10485760)
                if not data:
                    SocketUtil.serverSocket.sendFile("")
                    break
                while len(data) > 0:
                    intSent = SocketUtil.serverSocket.sendFile(data)
                    data = data[intSent:]
                time.sleep(1)
            SocketUtil.serverSocket.sendFile('4423718C61C4E8A4362D955BBC7B9711')
            wx.MessageBox(u"上传完成！",u"集中运维管理系统",wx.OK|wx.ICON_INFORMATION)
            #self.parent.SysMessaegText.WriteText(u"上传完成。\n")
        elif self.response=='-1':
            wx.MessageBox(u"文件名已存在！",u"集中运维管理系统",wx.OK|wx.ICON_WARNING)
            #self.parent.SysMessaegText.WriteText(u"文件名已存在！\n")
        else:
            wx.MessageBox(u"不能上传文件 %s\n" % fileNamet,u"集中运维管理系统",wx.OK|wx.ICON_WARNING)
            #self.parent.SysMessaegText.WriteText(u"不能上传文件 %s\n" % fileNamet)
        self.EndModal(wx.ID_OK)
        
    def OnCancel(self, event):
        """取消方法"""
        self.EndModal(wx.ID_CANCEL)  
    
    def OnGetResponseInfo(self):
        """获得上传文件命令的返回消息"""
        return self.response
    
class RemoveFilesDialog(ActionDialog):
    """删除文件的对话框"""
    def __init__(self, parent, fileName):
        """初始方法 parent为父对象"""
        self.fileName = fileName
        self.parent = parent
        '''
        self.parent.SysMessaegText.WriteText
        使用父对象的消息框输出消息
        '''
        ActionDialog.__init__(self, u"删除文件")
        
        StaticText(self.actionPanel, -1, u"您确认要对选择的文件进行删除吗？",(80, 80))
        
        #操作中提示
        self.actiontext=StaticText(self.actionPanel, -1, u"正在操作,请稍等...", (160, 250))
        self.actiontext.Show(False)
        
        self.ok = wx.Button(self.actionPanel, -1, u"确   定", (100, 200))
        self.ok.SetForegroundColour("#006699")
        self.cancel = wx.Button(self.actionPanel, -1, u"取   消", (230, 200))
        self.cancel.SetForegroundColour("#006699")

        #确定、取消事件
        self.ok.Bind(wx.EVT_LEFT_DOWN,self.OnDisplayInfo)
        self.ok.Bind(wx.EVT_LEFT_UP, self.OnOk)
        self.Bind(wx.EVT_BUTTON, self.OnCancel, self.cancel)
    
    def OnDisplayInfo(self, event):
        """显示操作信息"""
        self.actiontext.Show(True)

    def OnOk(self, event):
        """确定方法,开始发送上传文件命令"""
        
        #组合删除文件的命令
        cmd = "cmd=remove,file="+str(self.fileName)
        #发送删除文件的命令
        SocketUtil.serverSocket.send(str(cmd))
        #接收消息,获得删除命令的返回结果
        self.response = SocketUtil.serverSocket.recv() + '\n'; """需要修改IOMSERVER的返回值以方便做判断"""
        self.EndModal(wx.ID_OK)
        
    def OnCancel(self, event):
        """取消方法"""
        self.EndModal(wx.ID_CANCEL)  
    
    def OnGetResponseInfo(self):
        """获得删除文件命令的返回消息"""
        return self.response

class UpdateSelfDialog(ActionDialog):
    """自更新的对话框"""
    def __init__(self, parent, updateSelfServerList):
        """初始方法 parent为父对象"""
        self.parent = parent
        self.updateSelfServerList = updateSelfServerList
        '''
        self.parent.SysMessaegText.WriteText
        使用父对象的消息框输出消息
        '''
        ActionDialog.__init__(self, u"自更新")
        
        StaticText(self.actionPanel, -1, u"您确认要对选择的服务器进行自更新操作吗？",(80, 80))
        
        #操作中提示
        self.actiontext=StaticText(self.actionPanel, -1, u"正在操作,请稍等...", (160, 250))
        self.actiontext.Show(False)
        
        self.ok = wx.Button(self.actionPanel, -1, u"确   定", (100, 200))
        self.ok.SetForegroundColour("#006699")
        self.cancel = wx.Button(self.actionPanel, -1, u"取   消", (230, 200))
        self.cancel.SetForegroundColour("#006699")

        #确定、取消事件
        self.ok.Bind(wx.EVT_LEFT_DOWN,self.OnDisplayInfo)
        self.ok.Bind(wx.EVT_LEFT_UP, self.OnOk)
        self.Bind(wx.EVT_BUTTON, self.OnCancel, self.cancel)
    
    def OnDisplayInfo(self, event):
        """显示操作信息"""
        self.actiontext.Show(True)
        
    def OnOk(self, event):
        """确定方法,开始发送自更新命令"""
        if self.updateSelfServerList != None:
            #判断服务器不为空后，组合自更新命令的前半段
            cmd = "cmd=updateself,serverip="
            self.response = ''
            for server in self.updateSelfServerList:
                #循环对命令追加每个服务器的IP
                cmd += server.split("_")[0]
                cmd += ";"
            if cmd.endswith(";"):
                cmd = cmd[:len(cmd)-1]
            SocketUtil.serverSocket.send(str(cmd))
            #接收消息,获得自更新命令的返回结果
            self.response += SocketUtil.serverSocket.recv(); """需要修改IOMSERVER的返回值以方便做判断"""
            self.response += '\n'
            self.EndModal(wx.ID_OK)
        else:
            wx.MessageBox(u'没有选择服务器。', u"提示")
            self.EndModal(wx.ID_CANCEL)
            
    def OnCancel(self, event):
        """取消方法"""
        self.EndModal(wx.ID_CANCEL)  
    
    def OnGetResponseInfo(self):
        """获得自更新命令的返回消息"""
        return self.response
    
class ExecCommandDialog(ActionDialog):
    """执行命令的对话框"""
    def __init__(self, parent, ExecCommandServerList):
        """初始方法 parent为父对象"""
        self.parent = parent
        self.ExecCommandServerList = ExecCommandServerList
        '''
        self.parent.SysMessaegText.WriteText
        使用父对象的消息框输出消息
        '''
        ActionDialog.__init__(self, u"执行命令")
        
        StaticText(self.actionPanel, -1, u"您确认要发送该命令吗？",(80, 80))
        
        StaticText(self.actionPanel, -1, u"请输入命令:",(80, 120))
        
        self.commandstr = wx.TextCtrl(self.actionPanel, -1, "", (80, 140), size=(250, 20))
        
        #操作中提示
        self.actiontext=StaticText(self.actionPanel, -1, u"正在操作,请稍等...", (160, 250))
        self.actiontext.Show(False)
        
        self.ok = wx.Button(self.actionPanel, -1, u"确   定", (100, 200))
        self.ok.SetForegroundColour("#006699")
        self.cancel = wx.Button(self.actionPanel, -1, u"取   消", (230, 200))
        self.cancel.SetForegroundColour("#006699")

        #确定、取消事件
        self.ok.Bind(wx.EVT_LEFT_DOWN,self.OnDisplayInfo)
        self.ok.Bind(wx.EVT_LEFT_UP, self.OnOk)
        self.Bind(wx.EVT_BUTTON, self.OnCancel, self.cancel)
    
    def OnDisplayInfo(self, event):
        """显示操作信息"""
        self.actiontext.Show(True)
        
    def OnOk(self, event):
        """确定方法,开始发送上传文件命令"""
        
        #准备循环选中的服务器列表
        if self.ExecCommandServerList != None:
            #判断服务器不为空后，组合命令的前半段
            cmd = "cmd=command,command="+self.commandstr.GetValue()+",serverip="
            self.response = ''
            for server in self.ExecCommandServerList:
                #循环对命令追加每个服务器的IP
                cmd += server.split("_")[0]
                cmd += ";"
            if cmd.endswith(";"):
                cmd = cmd[:len(cmd)-1]
            SocketUtil.serverSocket.send(str(cmd))
            #接收消息,获得执行命令的返回结果
            self.response += SocketUtil.serverSocket.recv(); """需要修改IOMSERVER的返回值以方便做判断"""
            self.response += '\n'
            self.EndModal(wx.ID_OK)
        else:
            wx.MessageBox(u'没有选择服务器。', u"提示")
            self.EndModal(wx.ID_CANCEL)
        self.EndModal(wx.ID_OK)
        
    def OnCancel(self, event):
        """取消方法"""
        self.EndModal(wx.ID_CANCEL)  
    
    def OnGetResponseInfo(self):
        """获得删除文件命令的返回消息"""
        return self.response