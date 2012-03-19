#!/usr/bin/python
#-*- coding:utf-8-*-
#code by HAWK.Li

import wx
import os
import sys

import wx.lib.hyperlink as hl
from wx.lib.stattext import GenStaticText as StaticText
from wx.lib.statbmp  import GenStaticBitmap as StaticBitmap

from iomsMain import MainFrame

from DBUtil import User
from config import *
import sitecustomize

def version(cmds,cmd):
    """IOMSUI_version : 1.5_2012-03-12_Release
    """
    return version.__doc__

class Login(wx.Dialog):
    """登录对话框"""
    
    def __init__(self):
        """初始化登录对话框，包括用户名、密码。"""
        self.delta = (0,0)
        wx.Dialog.__init__(self, parent=None, id=-1,title=APP_TITLE,style=wx.STAY_ON_TOP)
        sizer = wx.GridBagSizer(hgap=5, vgap=10)
        self.SetBackgroundColour("#ffffff")
        self.SetIcon(wx.Icon('img/Loading.ico',wx.BITMAP_TYPE_ICO))
        bmp = wx.Image('img/title.jpg', wx.BITMAP_TYPE_JPEG).ConvertToBitmap()
        self.logo = wx.StaticBitmap(self, -1, bmp, size=(340, bmp.GetHeight()))
        sizer.Add(self.logo, pos=(0, 0), span=(1,6), flag=wx.EXPAND)

        bmp_logo = wx.Image('img/logo.jpg', wx.BITMAP_TYPE_JPEG).ConvertToBitmap()
        StaticBitmap(self, -1, bmp_logo, (0, 27), (bmp_logo.GetWidth(), bmp_logo.GetHeight()))
        
        #Link text
        link = hl.HyperLinkCtrl(self, wx.ID_ANY,u"IOMS集中运维管理系统",
                                URL="http://code.google.com/p/ioms/",pos=(290, 170))
        link.SetColours("BLUE", "BLUE", "BLUE")
        link.EnableRollover(True)
        link.SetUnderlines(False, False, False)
        link.UpdateLink()

        
        #Loging text
#        self.logintext=StaticText(self, -1, u"正在验证,请稍等...", (100, 160))
#        self.logintext.Show(False)
        
        # Label
        sizer.Add(wx.StaticText(self, -1, u"用户名：　    "), pos=(2, 1), flag=wx.ALIGN_RIGHT)
        sizer.Add(wx.StaticText(self, -1, u"密　码：　    "), pos=(3, 1), flag=wx.ALIGN_RIGHT)
        
        # Text
        self.username = wx.TextCtrl(self, -1,"", size=(160, 20))
        self.username.SetMaxLength(20)
        self.password = wx.TextCtrl(self, -1,"", size=(160, 20), style=wx.TE_PASSWORD)
        self.password.SetMaxLength(20)
        sizer.Add(self.username, pos=(2,2), span=(1,1))
        sizer.Add(self.password, pos=(3,2), span=(1,1))
        
        self.ok = wx.Button(self, -1, u"确   定", (35, 20))
        self.ok.SetForegroundColour("#006699")
        self.cancel = wx.Button(self, -1, u"取消登录", (35, 20))
        self.cancel.SetForegroundColour("#006699")

        # bind the evt
        #self.ok.Bind(wx.EVT_LEFT_DOWN,self.OnDisplayInfo)
        self.ok.Bind(wx.EVT_BUTTON, self.OnOK)
        self.ok.Bind(wx.EVT_LEFT_UP, self.OnOK)
        self.Bind(wx.EVT_BUTTON, self.OnCancel, self.cancel)
        
        self.Bind(wx.EVT_MOTION,self.OnMouseMove)
        self.Bind(wx.EVT_LEFT_DOWN,self.OnLeftDown)
        self.Bind(wx.EVT_LEFT_UP,self.OnLeftUp)

        sizer.Add(self.ok, pos=(4,1),flag=wx.EXPAND)
        sizer.Add(self.cancel, pos=(4,2))
        sizer.Add((4, 2), (6, 2))
        sizer.AddGrowableCol(3)
        sizer.AddGrowableRow(3)        
        self.SetSizer(sizer)
        self.Fit() 
        
    def OnLeftDown(self, evt):
        """鼠标拖动窗体辅助函数1"""
        self.CaptureMouse()
        x, y = self.ClientToScreen(evt.GetPosition())
        originx, originy = self.GetPosition()
        dx = x - originx
        dy = y - originy
        self.delta = ((dx, dy))
    def OnLeftUp(self, evt):
        """鼠标拖动窗体辅助函数2"""
        if self.HasCapture():
            self.ReleaseMouse()
    def OnMouseMove(self,event):
        """鼠标拖动窗体辅助函数3"""
        if event.Dragging() and event.LeftIsDown():
            x, y = self.ClientToScreen(event.GetPosition())
            fp = (x - self.delta[0], y - self.delta[1])
            self.Move(fp)
#    def OnDisplayInfo(self,event):
#        """显示验证中提示"""
#        self.logintext.Show(True)
        
    def OnOK(self, event):
        """进行登录验证"""
        user = User()
        if not self.username.GetValue():
            wx.MessageBox(u'请输入用户名。', u"提示")
            self.username.SetFocus()
            return

        if not self.password.GetValue():
            wx.MessageBox(u'请输入密码。', u"提示")
            self.password.SetFocus()
            return
        try:
            #查询用户是否存在，密码是否正确
            self.GetcheckRow= user.Check(self.username.GetValue(), self.password.GetValue())
            if not self.GetcheckRow:
                wx.MessageBox(u'用户名或密码错误，请确认后重新输入。', u"错误")
                self.username.SetFocus()
                return
            elif self.GetcheckRow == '-1':
                wx.MessageBox(u'用户名或密码错误，请确认后重新输入。', u"错误")
                self.username.SetFocus()
                return
            elif self.GetcheckRow == '-2':
                wx.MessageBox(u'用户名或密码错误，请确认后重新输入。', u"错误")
                self.username.SetFocus()
                return
        except Exception,e:
            message=u"系统出现异常："+str(e)
            wx.MessageBox(message,u"大承网络服务器管理系统：",style=wx.OK|wx.ICON_ERROR)              
        self.EndModal(wx.ID_OK)
    def OnGetuserInfo(self):
        """获得用户信息"""
        return self.GetcheckRow

    def OnCancel(self, event):
        self.EndModal(wx.ID_CANCEL)   

class MisApp(wx.App):
    """入口方法 帐号验证通过后调用主程序。"""
    def OnInit(self):
        """初始方法 自动调用"""
        login = Login()
        #显示登录框
        ret = login.ShowModal()
        if (ret == wx.ID_OK):
            self.username = login.username.GetValue()
            self.password = login.password.GetValue()
            self.userInfo = login.OnGetuserInfo()
            #弹出登陆后界面
            self.frame = MainFrame(None,u"")
            self.frame.Show()
            self.SetTopWindow(self.frame)
        else:
            pass
        #销毁登录框
        login.Destroy()
        return True

if __name__ == "__main__":
    try:
        #psyco加速NewEdit
        import psyco
        psyco.full()
    except ImportError:
        pass
    app = MisApp(redirect=False)
    app.MainLoop()
