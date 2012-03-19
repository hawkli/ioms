#!/usr/bin/python
#-*- coding:utf-8-*-
#code by HAWK.Li

import sys,os
import socket
import time,datetime
import wx.html
import wx.grid as gridlib

import images
import gridModel
import ServerList
from ServerList import dirList
from ServerList import ServerFunction
from ServerList import ServerClassList

try:
    from agw import aui
    from agw.aui import aui_switcherdialog as ASD
except ImportError: # if it's not there locally, try the wxPython lib.
    import wx.lib.agw.aui as aui
    from wx.lib.agw.aui import aui_switcherdialog as ASD
    
import DBUtil,MyUtil,ActionDialog,wxTextEditor,CurveUtil,SocketUtil

ID_About = wx.NewId()
ID_CustomizeToolbar = wx.ID_HIGHEST + 1
ID_SampleItem = ID_CustomizeToolbar + 1
ID_auiPanel = ID_CustomizeToolbar + 2

def version(cmds,cmd):
    """IOMSMain_version : 1.5_2012-03-12_Release
    """
    return version.__doc__

class MainFrame(wx.Frame):
    def __init__(self, parent, title):
        global gridList,gridListIndex
        gridList = []
        gridListIndex = 0
        wx.Frame.__init__(self, parent, -1, u'集中运维管理系统',size=(1100, 750),pos=(200,100))
        
        self._mgr = aui.AuiManager()
        self._mgr.SetManagedWindow(self)
        
        self._notebook_style = aui.AUI_NB_DEFAULT_STYLE | aui.AUI_NB_TAB_EXTERNAL_MOVE | wx.NO_BORDER
        self._notebook_theme = 1
        
        self.CurrentAdmin=wx.GetApp().username
        Intologs=DBUtil.User()
        Intologs.actionLog(self.CurrentAdmin, "UiLogin", u"UiLogin Succ", socket.gethostbyname(socket.gethostname()))
        #为使ServerList().AllServerList中有数据
        ServerClassList().Resurn_list()
        #创建菜单
        self.createMenuBar()
        #创建选项卡的窗口
        self.BuildPanes()
        
        #创建状态栏
        statusBar = self.CreateStatusBar(4, wx.ST_SIZEGRIP)
        statusBar.SetStatusWidths([-2, -3,-6,-3])
        
        statusBar.SetStatusText(u"就绪", 0)
        statusBar.SetStatusText(u"IOMS集中运维管理系统", 1)
        statusBar.SetStatusText(u"操作员："+str(self.CurrentAdmin), 2)
        
        #右下角时间
        self.timer = wx.PyTimer(self.Notify)
        self.timer.Start(1000)
        self.Notify()
        #事件绑定
        self.BindEvents()
        
    #创建面板
    def BuildPanes(self):
        #设置MinSize
        self.SetMinSize(wx.Size(400, 300))
        #设置ToolBar
        prepend_items, append_items = [], []
        item = aui.AuiToolBarItem()        
        item.SetKind(wx.ITEM_NORMAL)
        item.SetId(ID_CustomizeToolbar)
        #item.SetLabel("Customize...")
        append_items.append(item)
        
        #工具栏
        toolBar1 = aui.AuiToolBar(self, ID_auiPanel, wx.DefaultPosition, wx.DefaultSize,
                             agwStyle=aui.AUI_TB_OVERFLOW | aui.AUI_TB_TEXT | aui.AUI_TB_HORZ_TEXT)
        toolBar1.SetToolBitmapSize(wx.Size(16, 16))
        toolBar1_bmp1 = wx.ArtProvider.GetBitmap(wx.ART_FOLDER, wx.ART_OTHER, wx.Size(16, 16))
        
        toolBar1.AddSimpleTool(ID_SampleItem+1, u"重启", toolBar1_bmp1, u"点击此处重启")#加提示aui.ITEM_CHECK
        toolBar1.AddSimpleTool(ID_SampleItem+2, u"远程命令", toolBar1_bmp1, u"点击此处进行远程命令")
        toolBar1.AddSimpleTool(ID_SampleItem+3, u"文件上传", toolBar1_bmp1, u"点击此处上传文件呢")
        toolBar1.AddSimpleTool(ID_SampleItem+4, u"系统更新", toolBar1_bmp1, u"点击此处进行自更新")
        toolBar1.AddSeparator()
        toolBar1.AddSimpleTool(ID_SampleItem+5, u"连接到Client", toolBar1_bmp1, u"点击此处连接到Client")
        toolBar1.AddSimpleTool(ID_SampleItem+6, u"删除", toolBar1_bmp1, u"点击此处删除更新服务器上文件")
        toolBar1.AddSimpleTool(ID_SampleItem+7, u"编辑", toolBar1_bmp1, u"点击此处对服务器基本信息进行编辑")
        toolBar1.AddSimpleTool(ID_SampleItem+8, u"CPU运行信息", toolBar1_bmp1, u"点击此处查看所选服务器CPU信息")
        toolBar1.AddSimpleTool(ID_SampleItem+9, u"文件分发", toolBar1_bmp1, u"点击此处下载文件到所选服务器")
        toolBar1.AddSimpleTool(ID_SampleItem+10, u"删除进回收站", toolBar1_bmp1, u"点击此处将服务器放入回收站")

        toolBar1.SetCustomOverflowItems(prepend_items, append_items)
        toolBar1.Realize()
        
        #页面添加部分：
        #Toolbar 添加到页面
        self._mgr.AddPane(toolBar1, aui.AuiPaneInfo().Name("toolBar1").Caption("Toolbar 3").
                          ToolbarPane().Top().Row(1).Position(1))
        #目录
        self._mgr.AddPane(self.createTree(), aui.AuiPaneInfo().Left().MaximizeButton(True))
        #选项卡
        self._mgr.AddPane(self.createNoteBook(), aui.AuiPaneInfo().Name("notebook_content").
                          CenterPane().PaneBorder(False))
        #改变时，通知manager更新
        self._mgr.Update()
#数据区------------------------------------------------------------忧伤的分割线--------------------------------------------------------------
    #未分配设备Label
    def UnassignedColData(self):
        colLabels = [u'选择',u'ID', u'网卡1', u'网卡2', u'操作系统',
                          u'主机名', u'状态', u'捕获时间']
        return colLabels
    #未分配设备数据类型
    def UnassignedTypeData(self):
        dataTypes = [
                     gridlib.GRID_VALUE_STRING,
                     gridlib.GRID_VALUE_STRING,
                     gridlib.GRID_VALUE_STRING,
                     gridlib.GRID_VALUE_STRING,
                     gridlib.GRID_VALUE_STRING,
                     gridlib.GRID_VALUE_STRING,
                     gridlib.GRID_VALUE_STRING,
                     gridlib.GRID_VALUE_STRING
                     ]
        return dataTypes
    #未分配设备数据获得方法
    def UnassignedData(self):
        data = []
        data = ServerFunction().getUnassignedServerList()
        if data ==[]:
            data=[[u'无数据']]
        return data
    #物理显示模式Label
    def PhysicalColData(self):
        colLabels = [u'选择', u'机房-机柜', u'ID', u'网卡1', u'网卡2', u'操作系统',
                          u'主机名', u'状态', u'捕获时间']
        return colLabels
    #物理显示模式数据类型
    def PhysicalTypeData(self):
        dataTypes = [
                     gridlib.GRID_VALUE_STRING,
                     gridlib.GRID_VALUE_STRING,
                     gridlib.GRID_VALUE_STRING,
                     gridlib.GRID_VALUE_STRING,
                     gridlib.GRID_VALUE_STRING,
                     gridlib.GRID_VALUE_STRING,
                     gridlib.GRID_VALUE_STRING,
                     gridlib.GRID_VALUE_STRING,
                     gridlib.GRID_VALUE_STRING,
                     ]
        return dataTypes
    #物理显示模式数据获得方法
    def PhysicalData(self,area):
        data = []
        data = ServerFunction().getPysicalServerList(area)
        if data ==[]:
            data=[[u'无数据']]        
        return data
    #监控显示模式Label
    def MonitorPageColData(self):
        colLabels = [u'选择', u'ID', u'所在机房',u'所属项目',u'设备型号',
                          u'网卡1', u'网卡2', u'状态',u'CPU', u'RAM',
                           u'HDD读写', u'HDD剩余',u'捕获时间']
        return colLabels
    #监控显示模式数据类型
    def MonitorPageTypeData(self):
        dataTypes = [
                     gridlib.GRID_VALUE_STRING,
                     gridlib.GRID_VALUE_STRING,
                     gridlib.GRID_VALUE_STRING,
                     gridlib.GRID_VALUE_STRING,
                     gridlib.GRID_VALUE_STRING,
                          
                     gridlib.GRID_VALUE_STRING,
                     gridlib.GRID_VALUE_STRING,
                     gridlib.GRID_VALUE_STRING,
                     gridlib.GRID_VALUE_STRING,
                     gridlib.GRID_VALUE_STRING,
                     
                     gridlib.GRID_VALUE_STRING,
                     gridlib.GRID_VALUE_STRING,
                     gridlib.GRID_VALUE_STRING,
                     gridlib.GRID_VALUE_STRING,
                     ]
        return dataTypes
    #监控显示模式数据获得方法
    def MonitorPageData(self,list=None):
        data = []
        data = ServerFunction().getMonitorServerList(list)
        if data ==[]:
            data=[[u'无数据']]
        return data
    #1、菜单数据
    def menuData(self): 
        return ((u"文件(&F)",
            (u"保存日志", "Open", self.OnOpen),
            (u"清空日志", "Open", self.OnOpen),
            (u"退出(&Q)", "Quit", self.OnClose)),
            
            (u"视图(&V)",
            (u"目录", "View", self.OnCopy),
            (u"选项卡", "View", self.OnCopy)),
            
            (u"功能(&D)",
            (u"上传文件", "Function", self.OnOpen),
            (u"下载文件", "Function", self.OnOpen),
            (u"删除文件", "Function", self.OnOpen),
            (u"自更新", "Function", self.OnOpen),
            (u"执行命令", "Function", self.OnOpen),
            (u"在线状态", "Function", self.OnOpen),
            ),
            
            (u"基础数据管理(&B)",
            (u"基础数据管理", "View", self.OnCopy)),

            (u"用户(&U)",
            (u"用户管理", "View", self.OnCopy)),
            
            (u"帮助(&H)",
            (u"关于...", "About", self.OnAbout),
            (u"帮助说明", "Help", self.OnCut))
            )
#创建功能菜单、按钮、目录-----------------------------------------------------------------------------------------------------------------
    #2、循环创建menu
    def createMenuBar(self):
        menuBar = wx.MenuBar()
        for eachMenuData in self.menuData():
            menuLabel = eachMenuData[0]
            menuItems = eachMenuData[1:]
            menuBar.Append(self.createMenu(menuItems),menuLabel)
        self.SetMenuBar(menuBar)
    #3、读取数据循环创建单个并绑定事件
    def createMenu(self,menuData):
        menu = wx.Menu()
        for eachLabel,eachStatus,eachHandler in menuData:
            if not eachLabel:
                menu.AppendSeparator()
                continue
            menuItem = menu.Append(-1,eachLabel,eachStatus)
            self.Bind(wx.EVT_MENU,eachHandler,menuItem)
        return menu
    #生成目录
    def createTree(self):
        self.tree = wx.TreeCtrl(self, -1, wx.Point(0, 0), wx.Size(200, 250),
                           wx.TR_DEFAULT_STYLE | wx.NO_BORDER|wx.TR_ROW_LINES)
        
        imglist = wx.ImageList(16, 16, True, 2)
        imglist.Add(wx.ArtProvider.GetBitmap(wx.ART_FOLDER, wx.ART_OTHER, wx.Size(16, 16)))
        imglist.Add(wx.ArtProvider.GetBitmap(wx.ART_NORMAL_FILE, wx.ART_OTHER, wx.Size(16, 16)))
        self.tree.AssignImageList(imglist)

        root = self.tree.AddRoot(u"选择类别", 0)

        iom_dirList=dirList()
        self.allDirList = iom_dirList.getDirList()
        
        items = []
        tem = u""
        #一级目录
        for itemLs in self.allDirList:
            if itemLs[1] <> tem:
                items.append(self.tree.AppendItem(root,unicode(str(itemLs[1]),"utf-8"),0))
            tem = itemLs[1]
        #二级目录    
        for item in items:
            for template in self.allDirList:
                if self.tree.GetItemText(item)==template[1]:
                    self.tree.AppendItem(item,unicode(str(template[2]),"utf-8"),1) 
        self.tree.Expand(root)
        return self.tree
    #树形目录，选择改变时触发该事件
    def OnSelChanged(self, event):
        fm = {
              '0':self.createInfo,
              '1':self.createUnassigned,
              '2':self.createPhysical,
              '3':self.createMonitorPage,
              #4:self.createMonitorPage,
              }
        
        self.item = event.GetItem()
        #当前点击的目录描述，一级目录点击无作用
        tem = self.tree.GetItemText(self.item)
        #获得当前的tab数量，方便遍历检查重复
        pages = self.ctrl.GetPageCount()
        #检查在数据库中是否有相对应得tab
        create_not = False
        #检查是否已经创建
        exist = False 
        to_page = 0
        #循环检查是否在数据库中取出的数据列表中
        for template in self.allDirList:
            if tem == template[2]:#template[2]是二级目录(dir2_name)
                create_not = True
                break
        #若在数据库中有数据，则检查是否已经创建
        if create_not:
            #遍历检查当前要产生的tab是否已经显示出来了
            
            #以下单独列出一个函数，作公共使用
#            for i in range(pages):
#                #已经存在，转到以前产生的tab
#                if tem == self.ctrl.GetPageText(i):
#                    exist = True
#                    to_page = i
#                    break
#                else:
#                    pass
            #若已经创建，则转到已经生成的tab上
            check = self.CheckPages(tem)
            if check[0]:
                self.ctrl.SetSelection(check[1])
                self.changeShowGrid(check[1])
            else:
                page_bmp = wx.ArtProvider.GetBitmap(wx.ART_NORMAL_FILE, wx.ART_OTHER, wx.Size(16, 16))
                name = self.tree.GetItemText(self.item)
                if template[3] == '2':
                    self.ctrl.AddPage(fm[template[3]](str(name),self.ctrl), name, True, page_bmp)
                else:
                    self.ctrl.AddPage(fm[template[3]](self.ctrl), name, True, page_bmp)
        #所需创建的tab在数据库中找不到
        else:
            pass
        event.Skip()
#创建NoteBook-----------------------------------------------------------------------------------------------------------------
    def createNoteBook(self):
        # create the notebook off-window to avoid flicker
        client_size = self.GetClientSize()
        self.ctrl = aui.AuiNotebook(self, -1, wx.Point(client_size.x, client_size.y),
                              wx.Size(430, 200), agwStyle=self._notebook_style)
        #显示风格
        arts = [aui.AuiDefaultTabArt, aui.AuiSimpleTabArt, aui.VC71TabArt, aui.FF2TabArt,
                aui.VC8TabArt, aui.ChromeTabArt]
        
        art = arts[self._notebook_theme]()
        self.ctrl.SetArtProvider(art)
        #加选项卡
        page_bmp = wx.ArtProvider.GetBitmap(wx.ART_NORMAL_FILE, wx.ART_OTHER, wx.Size(16, 16))
        self.ctrl.AddPage(self.createHTML(self.ctrl), u"欢迎界面", True, page_bmp)
        #加载选项卡事件
        self.ctrl.Bind(aui.EVT_AUINOTEBOOK_PAGE_CHANGED, self.changeAuiPage) #标签切换事件
        self.ctrl.Bind(aui.EVT_AUINOTEBOOK_PAGE_CLOSE, self.closeAuiPage)    #标签关闭事件
        return self.ctrl
    
    def changeAuiPage(self, event):
        #切换当前grid下标为当前选择的标签序号
        self.changeShowGrid(self.ctrl.GetSelection())
        event.Skip()
        
    def closeAuiPage(self, event):
        self.removeShowGrid(self.ctrl.GetSelection())
        event.Skip()
        
    #单个设备编辑
    def createSingleEdit(self,agentId,parent=None):
        if not parent:
            parent= self
        activeServerLs = ServerList.AllServerList
        for activeServer in activeServerLs:
            if activeServer[0] == agentId:
                panel = wx.Panel(parent, -1)
                flex = wx.FlexGridSizer(0, 2)
                
                self.agentId = wx.TextCtrl(panel, -1, str(activeServer[0]), (90, 50), size=(90, 20))
                self.agentId.Hide()
                
                self.staticText1 = wx.StaticText(panel, -1, u"所在机房:")
                flex.Add(self.staticText1, 0, wx.ALL|wx.LEFT, 5)
                self.inputInfo1 = wx.ComboBox(panel, -1, unicode(str(activeServer[15]),"utf-8"), wx.DefaultPosition, wx.Size(200, -1))
                for tempDir in self.allDirList:
                    if tempDir[1] == u"物理显示模式":
                        self.inputInfo1.Append(unicode(str(tempDir[2]),"utf-8"))
                flex.Add(self.inputInfo1, 1, wx.ALL|wx.ALIGN_CENTRE, 5)
                
                self.staticText2 = wx.StaticText(panel, -1, u"所属项目:")
                flex.Add(self.staticText2, 0, wx.ALL|wx.LEFT, 5)
                self.inputInfo2 = wx.TextCtrl(panel, -1, unicode(str(activeServer[18]),"utf-8"), size=wx.Size(200,-1))
                flex.Add(self.inputInfo2, 1, wx.ALL|wx.ALIGN_LEFT, 5)
                
                self.staticText3 = wx.StaticText(panel, -1, u"所属机柜-层数:")
                flex.Add(self.staticText3, 0, wx.ALL|wx.LEFT, 5)
                self.inputInfo3 = wx.TextCtrl(panel, -1, activeServer[14], size=wx.Size(200,-1))
                flex.Add(self.inputInfo3, 1, wx.ALL|wx.ALIGN_LEFT, 5)
                
                self.staticText4 = wx.StaticText(panel, -1, u"硬件SN:")
                flex.Add(self.staticText4, 0, wx.ALL|wx.LEFT, 5)
                self.inputInfo4 = wx.TextCtrl(panel, -1, activeServer[13], size=wx.Size(200,-1))
                flex.Add(self.inputInfo4, 1, wx.ALL|wx.ALIGN_CENTRE, 5)
                
                self.staticText5 = wx.StaticText(panel, -1, u"外网IP:")
                flex.Add(self.staticText5, 0, wx.ALL|wx.LEFT, 5)
                self.inputInfo5 = wx.TextCtrl(panel, -1,activeServer[1],size=wx.Size(200,-1),style = wx.TE_READONLY)
                flex.Add(self.inputInfo5, 0, wx.ALL|wx.ALIGN_LEFT, 5)
                
                self.staticText6 = wx.StaticText(panel, -1, u"内网IP:")
                flex.Add(self.staticText6, 0, wx.ALL|wx.LEFT, 5)
                self.inputInfo6 = wx.TextCtrl(panel, -1,activeServer[2],size=wx.Size(200,-1),style = wx.TE_READONLY)
                flex.Add(self.inputInfo6, 0, wx.ALL|wx.ALIGN_LEFT, 5)
                
                self.staticText7 = wx.StaticText(panel, -1, u"服务器名称:")
                flex.Add(self.staticText7, 0, wx.ALL|wx.LEFT, 5)
                self.inputInfo7 = wx.TextCtrl(panel, -1,activeServer[5],size=wx.Size(200,-1),style = wx.TE_READONLY)
                flex.Add(self.inputInfo7, 1, wx.ALL|wx.ALIGN_CENTRE, 5)
                
        #        self.staticText8 = wx.StaticText(panel, -1, u"是否物理服务器:")
        #        flex.Add(self.staticText8, 0, wx.ALL|wx.LEFT, 5)
        #        self.inputInfo8 = wx.CheckBox(panel, -1, "", wx.DefaultPosition, wx.Size(200, -1))
        #        flex.Add(self.inputInfo8,1, wx.ALL|wx.ALIGN_CENTRE, 5)
        
        #        self.staticText9 = wx.self.staticText(panel, -1, u"是否代理:")
        #        flex.Add(self.staticText9, 0, wx.ALL|wx.LEFT, 5)
        #        self.inputInfo9 = wx.CheckBox(panel, -1, "", wx.DefaultPosition, wx.Size(200, -1))
        #        flex.Add(self.inputInfo9,1, wx.ALL|wx.ALIGN_CENTRE, 5)
        
                self.staticText10 = wx.StaticText(panel, -1, u"服务器型号:")
                flex.Add(self.staticText10, 0, wx.ALL|wx.LEFT, 5)
                self.inputInfo10 = wx.TextCtrl(panel, -1,activeServer[8],size=wx.Size(200,-1),style = wx.TE_READONLY)
                flex.Add(self.inputInfo10, 1, wx.ALL|wx.ALIGN_CENTRE, 5)
                
        #        self.staticText11 = wx.StaticText(panel, -1, u"购买时间:")
        #        flex.Add(self.staticText11, 0, wx.ALL|wx.LEFT, 5)
        #        self.inputInfo11 = wx.DatePickerCtrl(panel,-1)
        #        flex.Add(self.inputInfo11, 0, wx.ALL|wx.ALIGN_LEFT, 5)
        
        #        self.staticText12 = wx.StaticText(panel, -1, u"所属运营商:")
        #        flex.Add(self.staticText12, 0, wx.ALL|wx.LEFT, 5)
        #        self.inputInfo12 = wx.ComboBox(panel, -1, "", wx.DefaultPosition, wx.Size(200, -1))
        #        flex.Add(self.inputInfo12,1, wx.ALL|wx.ALIGN_CENTRE, 5)
        
                self.staticText13 = wx.StaticText(panel, -1, u"机房联系人:")
                flex.Add(self.staticText13, 0, wx.ALL|wx.LEFT, 5)
                self.inputInfo13 = wx.TextCtrl(panel, -1,activeServer[16],size=wx.Size(200,-1))
                flex.Add(self.inputInfo13, 0, wx.ALL|wx.ALIGN_LEFT, 5)
        
                self.staticText14 = wx.StaticText(panel, -1, u"联系人电话:")
                flex.Add(self.staticText14, 0, wx.ALL|wx.LEFT, 5)
                self.inputInfo14 = wx.TextCtrl(panel, -1,activeServer[17],size=wx.Size(200,-1))
                flex.Add(self.inputInfo14, 0, wx.ALL|wx.ALIGN_LEFT, 5)
                
        #        self.staticText15 = wx.StaticText(panel, -1, u"备用电话:")
        #        flex.Add(self.staticText15, 0, wx.ALL|wx.LEFT, 5)
        #        self.inputInfo15 = wx.TextCtrl(panel, -1,"",size=wx.Size(200,-1))
        #        flex.Add(self.inputInfo15, 0, wx.ALL|wx.ALIGN_LEFT, 5)
        
        #        self.staticText16 = wx.StaticText(panel, -1, u"备注:")
        #        flex.Add(self.staticText16, 0, wx.ALL|wx.LEFT, 5)
        #        self.inputInfo16 = wx.TextCtrl(panel, -1, "",size=wx.Size(200,80),style=wx.TE_MULTILINE|wx.TE_RICH2)
        #        flex.Add(self.inputInfo16, 0, wx.ALL|wx.ALIGN_LEFT, 5)
                self.singleButton = wx.Button(panel,-1,u"提交")
                flex.Add(self.singleButton)
                #self.singleButton2 = wx.Button(panel,-1,u"重置")
                #flex.Add(self.singleButton2)
                panel.SetSizer(flex)
                self.Bind(wx.EVT_BUTTON, self.OnUpdateServerButton, self.singleButton)
                #self.Bind(wx.EVT_BUTTON, self.OnCut, self.singleButton2)
                
                self.createShowGrid(None)
                return panel
        else:
            message = u"只有活动的服务器才可编辑！"
            wx.MessageBox(message,u"IOMS集中运维管理系统：",style=wx.OK|wx.ICON_INFORMATION)
    #多个设备编辑
    def createMutilEdit(self,parent=None):
        panel = wx.Panel(parent,-1)
        flex = wx.FlexGridSizer(0,2)
        
        flex.Add(wx.StaticText(panel, -1, u"所在机房:"), 0, wx.ALL|wx.LEFT, 5)
        flex.Add(wx.ComboBox(panel, -1, "", wx.DefaultPosition, wx.Size(200, -1)),
                 1, wx.ALL|wx.ALIGN_CENTRE, 5)

        flex.Add(wx.StaticText(panel, -1, u"服务器名称:"), 0, wx.ALL|wx.LEFT, 5)
        flex.Add(wx.ComboBox(panel, -1, "", wx.DefaultPosition, wx.Size(200, -1)),
                 1, wx.ALL|wx.ALIGN_CENTRE, 5)

        flex.Add(wx.StaticText(panel, -1, u"所属机柜:"), 0, wx.ALL|wx.LEFT, 5)
        flex.Add(wx.ComboBox(panel, -1, "", wx.DefaultPosition, wx.Size(200, -1)),
                 1, wx.ALL|wx.ALIGN_CENTRE, 5)

        flex.Add(wx.StaticText(panel, -1, u"所属项目:"), 0, wx.ALL|wx.LEFT, 5)
        flex.Add(wx.ComboBox(panel, -1, "", wx.DefaultPosition, wx.Size(200, -1)),
                 1, wx.ALL|wx.ALIGN_CENTRE, 5)
        
        flex.Add(wx.StaticText(panel, -1, u"是否物理服务器:"), 0, wx.ALL|wx.LEFT, 5)
        flex.Add(wx.CheckBox(panel, -1, "", wx.DefaultPosition, wx.Size(200, -1)),
                 1, wx.ALL|wx.ALIGN_CENTRE, 5)

        flex.Add(wx.StaticText(panel, -1, u"是否代理:"), 0, wx.ALL|wx.LEFT, 5)
        flex.Add(wx.CheckBox(panel, -1, "", wx.DefaultPosition, wx.Size(200, -1)),
                 1, wx.ALL|wx.ALIGN_CENTRE, 5)

        flex.Add(wx.StaticText(panel, -1, u"服务器型号:"), 0, wx.ALL|wx.LEFT, 5)
        flex.Add(wx.ComboBox(panel, -1, "", wx.DefaultPosition, wx.Size(200, -1)),
                 1, wx.ALL|wx.ALIGN_CENTRE, 5)

        flex.Add(wx.StaticText(panel, -1, u"购买时间:"), 0, wx.ALL|wx.LEFT, 5)
        flex.Add(wx.DatePickerCtrl(panel,-1), 0, wx.ALL|wx.ALIGN_LEFT, 5)

        flex.Add(wx.StaticText(panel, -1, u"所属运营商:"), 0, wx.ALL|wx.LEFT, 5)
        flex.Add(wx.ComboBox(panel, -1, "", wx.DefaultPosition, wx.Size(200, -1)),
                 1, wx.ALL|wx.ALIGN_CENTRE, 5)

        flex.Add(wx.StaticText(panel, -1, u"所属区域:"), 0, wx.ALL|wx.LEFT, 5)
        flex.Add(wx.SpinCtrl(panel, -1, "1", wx.DefaultPosition, wx.Size(200, -1),
                             wx.SP_ARROW_KEYS, 1, 13, 5), 0, wx.ALL|wx.ALIGN_CENTRE, 5)

        flex.Add(wx.StaticText(panel, -1, u"机房联系人:"), 0, wx.ALL|wx.LEFT, 5)
        flex.Add(wx.TextCtrl(panel, -1, "",size=wx.Size(200,-1)), 0, wx.ALL|wx.ALIGN_LEFT, 5)

        flex.Add(wx.StaticText(panel, -1, u"机房电话:"), 0, wx.ALL|wx.LEFT, 5)
        flex.Add(wx.TextCtrl(panel, -1, "",size=wx.Size(200,-1)), 0, wx.ALL|wx.ALIGN_LEFT, 5)

        flex.Add(wx.StaticText(panel, -1, u"备用电话:"), 0, wx.ALL|wx.LEFT, 5)
        flex.Add(wx.TextCtrl(panel, -1, "",size=wx.Size(200,-1)), 0, wx.ALL|wx.ALIGN_LEFT, 5)

        flex.Add(wx.StaticText(panel, -1, u"备注:"), 0, wx.ALL|wx.LEFT, 5)
        flex.Add(wx.TextCtrl(panel, -1, "",size=wx.Size(200,80),style=wx.TE_MULTILINE|wx.TE_RICH2), 0, wx.ALL|wx.ALIGN_LEFT, 5)
        flex.Add(wx.Button(panel,-1,u"提交"))
        flex.Add(wx.Button(panel,-1,u"重置"))
        panel.SetSizer(flex)
        return panel
    #未分配设备
    def createUnassigned(self,parent=None):
        if not parent:
            parent =self
        colLabels = self.UnassignedColData()
        dataTypes = self.UnassignedTypeData()
        data = self.UnassignedData()
        if data ==[[u'无数据']]:
            dataTypes=[gridlib.GRID_VALUE_STRING]
            colLabels=["-"*80+u"无相关数据"+"-"*80]
            grid = gridModel.CustTableGrid(parent,colLabels,dataTypes,data,False)
            grid.SetCellAlignment(0, 0, wx.ALIGN_CENTRE, wx.ALIGN_CENTRE)
            grid.SetReadOnly(0,0)
        else:
            grid = gridModel.CustTableGrid(parent,colLabels,dataTypes,data,True,6)
            self.Bind(wx.grid.EVT_GRID_SELECT_CELL, self.clickGridCheckBox, grid)
        #cb2 = wx.CheckBox(self.grid, -1, "Oranges")
        #self.grid.Add(wx.CheckBox(self, -1, 'Case Sensitive')) #没有Add方法
        self.createShowGrid(grid)
        return grid
    
    def createShowGrid(self, grid):
        global gridListIndex
        gridList.append(grid)
        gridListIndex = len(gridList)
        print 'createShowGrid-%d' %(gridListIndex)
    
    def changeShowGrid(self, gridIndex):
        global gridListIndex
        gridListIndex = gridIndex
        print 'changeShowGrid-%d' %(gridListIndex)
        
    def removeShowGrid(self, gridIndex):
        global gridListIndex
        del gridList[gridIndex]
        if gridListIndex > len(gridList):
            gridListIndex = len(gridList)
        print 'removeShowGrid-%d' %(gridListIndex)
        
    def getShowGrid(self):
        return gridList[gridListIndex]
    
    #物理显示模式
    def createPhysical(self,area,parent=None):
        if not parent:
             parent = self
        colLabels = self.PhysicalColData()
        dataTypes = self.PhysicalTypeData()
        data = self.PhysicalData(area)
        #数据库中无数据，页面显示无相关数据
        if data ==[[u'无数据']]:
            dataTypes=[gridlib.GRID_VALUE_STRING]
            colLabels=["-"*80+u"无相关数据"+"-"*80]
            grid = gridModel.CustTableGrid(parent,colLabels,dataTypes,data,False)
            grid.SetCellAlignment(0, 0, wx.ALIGN_CENTRE, wx.ALIGN_CENTRE)
            grid.SetReadOnly(0,0)
        #数据库中有数据，则分析机房个数之后显示
        else:
            #问题要处理，这边每一个grid不是一样的，数据要单独处理，上面提供数据，下面动态生成，也是可以的~
            grid = gridModel.CustTableGrid(parent,colLabels,dataTypes,data,True,7)
            self.Bind(wx.grid.EVT_GRID_SELECT_CELL, self.clickGridCheckBox, grid)
            color = ['WHITE','#E0E0E0']
            for i in range((len(data)/7)):
                grid.SetCellSize(i*7, 1, 7, 1);
                grid.SetCellAlignment(i*7, 1, wx.ALIGN_CENTRE, wx.ALIGN_CENTRE)
                grid.SetCellBackgroundColour(i*7,1,str(color[i%2]))
                for j in range(i*7,(i+1)*7):
                    attr = gridlib.GridCellAttr()
                    attr.SetTextColour(wx.BLACK)
                    attr.SetBackgroundColour(str(color[i%2]))
                    attr.SetFont(wx.Font(10, wx.SWISS, wx.NORMAL, wx.NORMAL)) 
                    grid.SetRowAttr(j, attr)
        grid.AutoSizeColumns(False)
        self.createShowGrid(grid)
        return grid
    
    def clickGridCheckBox(self, event):
        #编辑器处理方法，暂时无效果
        """
        if event.GetCol() == 0:
            grid = self.getShowGrid()
            grid.SetCellEditor(event.GetRow(), 0, wx.grid.GridCellBoolEditor())
            grid.EnableCellEditControl()
            print grid.IsCellEditControlEnabled()
            grid.BeginBatch()
            #grid.SetCellValue(event.GetRow(), 2, "True")
            grid.ShowCellEditControl()
            grid.SetCellValue(event.GetRow(), 0, "True")
            grid.SaveEditControlValue()
            #grid.SetCellRenderer(event.GetRow(), 0, wx.grid.GridCellBoolRenderer())
            grid.EndBatch()
            grid.ForceRefresh()
            print grid.GetCellValue(event.GetRow(), 0)
            #print grid.GetCellValue(event.GetRow(), 2)
        """
        if event.GetCol() == 0:
            grid = self.getShowGrid()
            value = grid.GetCellValue(event.GetRow(), 0)
            if value == u'□':
                grid.SetCellValue(event.GetRow(), 0, u'■')
            else:
                grid.SetCellValue(event.GetRow(), 0, u'□')
            grid.ForceRefresh()
        event.Skip()
    
    #监控显示模式
    def createMonitorPage(self,parent=None):
        if not parent:
             parent = self
        colLabels = self.MonitorPageColData()
        dataTypes = self.MonitorPageTypeData()
        data = self.MonitorPageData()
        
        pMain = wx.Panel(parent, -1, style= 0)
        topP = wx.Panel(pMain,-1,style = 0)
        buttomP = wx.Panel(pMain,-1,style = wx.SUNKEN_BORDER)
        if data ==[[u'无数据']]:
            dataTypes=[gridlib.GRID_VALUE_STRING]
            colLabels=["-"*80+u"无相关数据"+"-"*80]
            grid = gridModel.CustTableGrid(parent,colLabels,dataTypes,data,False)
            grid.SetCellAlignment(0, 0, wx.ALIGN_CENTRE, wx.ALIGN_CENTRE)
            grid.SetReadOnly(0,0)
        else:
            grid = gridModel.CustTableGrid(buttomP,colLabels,dataTypes,data,True,7)
        self.Bind(wx.grid.EVT_GRID_SELECT_CELL, self.clickGridCheckBox, grid)
        self.createShowGrid(grid)
        #这部分代码需要后期版本更改
        addressList = [u'上海机房', u'沈阳机房', u'南京机房']
        subjectList = [u'项目A',u'项目B',u'项目C',u'项目D']
        
        lab = wx.StaticText(topP, -1, u"所在机房:")
        self.cb = wx.ComboBox(topP, 500, u"--请选择--", (90, 50), 
                         (160, -1), addressList,
                         wx.CB_DROPDOWN
                         | wx.TE_PROCESS_ENTER
                         )
        lab2 = wx.StaticText(topP, -1, u"所属项目:")
        self.cb2 = wx.ComboBox(topP, 500, u"--请选择--", (90, 50), 
                         (160, -1), subjectList,
                         wx.CB_DROPDOWN
                         | wx.TE_PROCESS_ENTER
                         )
        bt = wx.Button(topP,-1,u"查询")
        self.Bind(wx.EVT_BUTTON, self.OnQuery, bt)
        #顶部panel布局
        topBs = wx.BoxSizer(wx.HORIZONTAL)
        topBs.Add(lab)
        topBs.Add(self.cb)
        topBs.Add(lab2)
        topBs.Add(self.cb2)
#        topBs.Add(lab3)
#        topBs.Add(cb3)
        topBs.Add(bt)
        topP.SetSizer(topBs)
        #底下panel布局
        buttomBs = wx.BoxSizer(wx.HORIZONTAL)
        buttomBs.Add(grid,wx.EXPAND)
        buttomP.SetSizer(buttomBs)
        #父panel布局
        mainBs = wx.BoxSizer(wx.VERTICAL)
        mainBs.Add(topP,2,wx.EXPAND)
        mainBs.Add(buttomP,18,wx.EXPAND)
        pMain.SetAutoLayout(True)
        pMain.SetSizer(mainBs)
        pMain.Layout()
        return pMain
    #创建HTML
    def createHTML(self, parent=None):
        if not parent:
            parent = self
        html = wx.html.HtmlWindow(parent, -1, wx.DefaultPosition, wx.Size(400, 300))
        html.SetPage(GetIntroText())
        self.createShowGrid(None)
        return html
    #设备类型管理
    def createEqType(self,parent=None):
        if not parent:
            parent = self
        panel = wx.Panel(parent,-1)
        flex = wx.FlexGridSizer(0,2)
        flex.Add(wx.StaticText(panel, -1, u"资产类别:"), 0, wx.ALL|wx.LEFT, 5)
        flex.Add(wx.ComboBox(panel, -1, "", wx.DefaultPosition, wx.Size(200, -1)),
                 1, wx.ALL|wx.ALIGN_CENTRE, 5)
        flex.Add(wx.StaticText(panel, -1, u"品牌型号:"), 0, wx.ALL|wx.LEFT, 5)
        flex.Add(wx.ComboBox(panel, -1, "", wx.DefaultPosition, wx.Size(200, -1)),
                 1, wx.ALL|wx.ALIGN_CENTRE, 5)
        flex.Add(wx.StaticText(panel, -1, u"数量:"), 0, wx.ALL|wx.LEFT, 5)
        flex.Add(wx.ComboBox(panel, -1, "", wx.DefaultPosition, wx.Size(200, -1)),
                 1, wx.ALL|wx.ALIGN_CENTRE, 5)
        flex.Add(wx.StaticText(panel, -1, u"CPU:"), 0, wx.ALL|wx.LEFT, 5)
        flex.Add(wx.ComboBox(panel, -1, "", wx.DefaultPosition, wx.Size(200, -1)),
                 1, wx.ALL|wx.ALIGN_CENTRE, 5)
        flex.Add(wx.StaticText(panel, -1, u"RAM:"), 0, wx.ALL|wx.LEFT, 5)
        flex.Add(wx.ComboBox(panel, -1, "", wx.DefaultPosition, wx.Size(200, -1)),
                 1, wx.ALL|wx.ALIGN_CENTRE, 5)
        flex.Add(wx.StaticText(panel, -1, u"HDD:"), 0, wx.ALL|wx.LEFT, 5)
        flex.Add(wx.ComboBox(panel, -1, "", wx.DefaultPosition, wx.Size(200, -1)),
                 1, wx.ALL|wx.ALIGN_CENTRE, 5)
        flex.Add(wx.StaticText(panel, -1, u"采购时间:"), 0, wx.ALL|wx.LEFT, 5)
        flex.Add(wx.TextCtrl(panel, -1, "",size=wx.Size(200,-1)), 0, wx.ALL|wx.ALIGN_LEFT, 5)
        flex.Add(wx.StaticText(panel, -1, u"备注:"), 0, wx.ALL|wx.LEFT, 5)
        flex.Add(wx.TextCtrl(panel, -1, "",size=wx.Size(200,-1)), 0, wx.ALL|wx.ALIGN_LEFT, 5)
        flex.Add(wx.Button(panel,-1,u"提交"))
        flex.Add(wx.Button(panel,-1,u"重置"))
        panel.SetSizer(flex)
        return panel
    #产生文件上传下载页面
    def createDownload(self,RefurbMask, extData):
        #标题
        fieldsdata=[[u"文件名"],[u"md5码"],[u"文件大小"],[u"操作"]]
        
        rowLen = len(extData)
        collen = len(fieldsdata)
        
        if RefurbMask==0:
            #新建表格
            self.grid_1 = wx.grid.Grid(self, -1, size=(1, 1))
            self.grid_1.CreateGrid(rowLen,4)
            #下载文件表格单击事件
            self.Bind(wx.grid.EVT_GRID_CELL_LEFT_CLICK, self.doDownloads, self.grid_1)
        
        elif RefurbMask==1:
            self.grid_1.ClearGrid()
            self.grid_1.ForceRefresh()
        
        self.grid_1.SetDefaultCellAlignment(wx.ALIGN_CENTER, wx.ALIGN_RIGHT)
        #显示网格
        self.grid_1.EnableGridLines(True)
        #表格只读
        self.grid_1.EnableEditing(False)
        
        #计算该添加几行数据
        if rowLen > self.grid_1.GetNumberRows():
            self.grid_1.AppendRows(rowLen-self.grid_1.GetNumberRows())
        elif self.grid_1.GetNumberRows() > rowLen:
            self.grid_1.DeleteRows(self.grid_1.GetNumberRows() - rowLen)
        #行/列坐标标题
        index = 0 
        for item in fieldsdata:
            self.grid_1.SetColLabelValue(index, item[0])
            index+= 1
        #行/列数据
        color_key=1
        color_value=""
        for row in range(rowLen):
            #间隔背景值
            if color_key%2==0:
                color_value="#efefef"
            else:
                color_value="#ffffff"
            #设置行高
            self.grid_1.SetRowSize(row, 25)
            
            #设置隔行背景
            for col in range(collen):
                self.grid_1.SetCellBackgroundColour(row, col, color_value)
                if col == 0:
                    self.grid_1.SetCellValue(row, col, extData[row][0])
                elif col == 1:
                    self.grid_1.SetCellValue(row, col, extData[row][1])
                elif col == 2:
                    self.grid_1.SetCellValue(row, col, extData[row][2])
                elif col == 3:
                    self.grid_1.SetCellValue(row, col, u"下载")
                    self.grid_1.SetCellTextColour(row, 3, "BLUE")
            
            color_key+=1
        #设置三列的宽
        self.grid_1.SetColSize(0, 180)
        self.grid_1.SetColSize(1, 250)
        self.grid_1.SetColSize(2, 130)
        self.grid_1.SetColSize(3, 80)
        
        self.createShowGrid(None)
        return self.grid_1
    def createDelete(self,RefurbMask, extData):
        #标题
        fieldsdata=[[u"文件名"],[u"md5码"],[u"文件大小"],[u"操作"]]
        rowLen = len(extData)
        collen = len(fieldsdata)
        
        if RefurbMask==0:
            #新建表格
            self.grid_2 = wx.grid.Grid(self, -1, size=(1, 1))
            self.grid_2.CreateGrid(rowLen,4)
            page_bmp = wx.ArtProvider.GetBitmap(wx.ART_NORMAL_FILE, wx.ART_OTHER, wx.Size(16, 16))
            self.ctrl.AddPage(self.grid_2,u"删除文件", True, page_bmp)
            #删除文件表格单击事件
            self.Bind(wx.grid.EVT_GRID_CELL_LEFT_CLICK, self.doRemoveFiles, self.grid_2)
        
        elif RefurbMask==1:
            self.grid_2.ClearGrid()
            self.grid_2.ForceRefresh()
        
        self.grid_2.SetDefaultCellAlignment(wx.ALIGN_CENTER, wx.ALIGN_RIGHT)
        #显示网格
        self.grid_2.EnableGridLines(True)
        #表格只读
        self.grid_2.EnableEditing(False)
        #计算该添加几行数据
        if rowLen > self.grid_2.GetNumberRows():
            self.grid_2.AppendRows(rowLen-self.grid_2.GetNumberRows())
        elif self.grid_2.GetNumberRows() > rowLen:
            self.grid_2.DeleteRows(self.grid_2.GetNumberRows() - rowLen)
        #行/列坐标标题
        index = 0 
        for item in fieldsdata:
            self.grid_2.SetColLabelValue(index, item[0])
            index+= 1
        #行/列数据
        color_key=1
        color_value=""
        for row in range(rowLen):
            #间隔背景值
            if color_key%2==0:
                color_value="#efefef"
            else:
                color_value="#ffffff"
            #设置行高
            self.grid_2.SetRowSize(row, 25)
            
            #设置隔行背景
            for col in range(collen):
                self.grid_2.SetCellBackgroundColour(row, col, color_value)
                if col == 0:
                    self.grid_2.SetCellValue(row, col, extData[row][0])
                elif col == 1:
                    self.grid_2.SetCellValue(row, col, extData[row][1])
                elif col == 2:
                    self.grid_2.SetCellValue(row, col, extData[row][2])
                elif col == 3:
                    self.grid_2.SetCellValue(row, col, u"删除")
                    self.grid_2.SetCellTextColour(row, 3, "BLUE")
            color_key+=1
        #设置三列的宽
        self.grid_2.SetColSize(0, 180)
        self.grid_2.SetColSize(1, 250)
        self.grid_2.SetColSize(2, 130)
        self.grid_2.SetColSize(3, 80)
        return self.grid_2
#菜单事件处理部分--------------------------------------------------------------------------------------------------------
    def OnOpen(self, event): pass
    def OnCopy(self, event): pass
    def OnCut(self, event):
        """帮助说明按钮方法"""
        try:
            #发送查看帮助说明的命令
            SocketUtil.serverSocket.send("cmd=help")
            #接收消息,获得帮助说明
            data = SocketUtil.serverSocket.recv();
            if data != None:
                if hasattr(sys, "frozen") and getattr(sys, "frozen") == "windows_exe": 
                    #以下这行专用于打包exe版本，否则运行命令出错              
                    data = data.decode('utf-8').encode('gbk')
                else:
                    #以下这行专用于eclipse运行版本
                    pass
                
                dlg = wx.MessageDialog(self, data, u"帮助说明...",
                               wx.OK | wx.ICON_INFORMATION)
                dlg.ShowModal()
                dlg.Destroy()
        except Exception,e:
            message=u"系统出现异常："+str(e)
            wx.MessageBox(message,u"IOMS集中运维管理系统：",style=wx.OK|wx.ICON_ERROR)        
        
    def OnPaste(self, event): pass
    def OnOptions(self, event): pass
    def OnAbout(self, event):
        """关于按钮方法"""
        try:
            #发送查看版本信息的命令
            SocketUtil.serverSocket.send("cmd=showversion")
            #接收消息,获得版本信息
            data = SocketUtil.serverSocket.recv();
            if data != None:
                dlg = wx.MessageDialog(self, data, u"关于...",
                               wx.OK | wx.ICON_INFORMATION)
                dlg.ShowModal()
                dlg.Destroy()
        except Exception,e:
            message=u"系统出现异常："+str(e)
            wx.MessageBox(message,u"IOMS集中运维管理系统：",style=wx.OK|wx.ICON_ERROR)    
#工具栏事件处理部分--------------------------------------------------------------------------------------------------------
    #重启服务器
    def OnRestart(self, event):
        """执行重启命令"""
        message=u"重启功能未开发："
        wx.MessageBox(message,u"IOMS集中运维管理系统",style=wx.OK|wx.ICON_INFORMATION) 
        event.Skip()
    #命令行模式
    def OnToIomClient(self, event):
        """打开命令行模式"""
        cmdstr = MyUtil.cur_file_dir()+"\\IOMClient.exe"
        os.popen('start '+cmdstr+' '+self.CurrentAdmin+' '+wx.GetApp().password)
        event.Skip()
    #弹出上传文件窗口
    def OnToUpLoads(self, event):
        """上传文件按钮方法"""
        try:
            upLoadsFileDialog = ActionDialog.UpLoadsFileDialog(self)
            ret = upLoadsFileDialog.ShowModal()
            if (ret == wx.ID_OK):
                #获得下载文件的返回信息
                self.upLoadsFileInfo = upLoadsFileDialog.OnGetResponseInfo()
                if self.upLoadsFileInfo != None:
                    pass
                    #在消息框中输出消息
                    #self.SysMessaegText.WriteText(self.upLoadsFileInfo.decode('utf-8').encode('gbk'))
            upLoadsFileDialog.Destroy()
        except Exception,e:
            message=u"系统出现异常："+str(e)
            wx.MessageBox(message,u"IOMS集中运维管理系统：",style=wx.OK|wx.ICON_ERROR)        
        event.Skip()
    #NoteBook中显示下载文件页面
    def OnDownloads(self, event):
        """下载文件按钮方法"""
        try:
            #发送查看可下载文件的命令
            SocketUtil.serverSocket.send("cmd=dir")
            #接收消息,获得可下载文件列表
            data = SocketUtil.serverSocket.recv();
            fileList = []
            if data != None:
                #如果消息不为空，进行解析
                fileList = SocketUtil.analysisData(data)
            page_bmp = wx.ArtProvider.GetBitmap(wx.ART_NORMAL_FILE, wx.ART_OTHER, wx.Size(16, 16))
            self.ctrl.AddPage(self.createDownload(0, fileList),u"文件下载", True, page_bmp)
        except Exception,e:
            message=u"系统出现异常："+str(e)
            wx.MessageBox(message,u"IOMS集中运维管理系统：",style=wx.OK|wx.ICON_ERROR)        
        event.Skip()
    #NoteBook中显示删除文件页面
    def OnRemoveFiles(self, event):
        """删除文件按钮方法"""
        try:
            #发送查看可下载文件的命令
            SocketUtil.serverSocket.send("cmd=dir")
            #接收消息,获得可下载文件列表
            data = SocketUtil.serverSocket.recv();
            fileList = []
            if data != None or data != 'Not files can be download.没有可以下载的文件.':
                #如果消息不为空，进行解析，或者服务器返回无可下载文件
                fileList = SocketUtil.analysisData(data)
            self.createShowGrid(None)
            check = self.CheckPages(u"删除文件")
            if check[0]:
                self.ctrl.SetSelection(check[1])
                self.createDelete(1,fileList)
            else:
                self.createDelete(0, fileList)
                
        except Exception,e:
            message=u"系统出现异常："+str(e)
            wx.MessageBox(message,u"IOMS集中运维管理系统：",style=wx.OK|wx.ICON_ERROR)        
        event.Skip()
    #远程执行命令（命令仅限在数据库中规定的）
    def OnToExecCommand(self, event):
        """执行命令按钮方法"""
        cmd_info = []
        if self.checkItems(self.GainInfo()):
            for i in self.GainInfo():
                cmd_info.append(i[1])
            if cmd_info ==[] or (u" " in cmd_info):
                pass
            else:
                try:
                    ExecCommandDialog = ActionDialog.ExecCommandDialog(self,cmd_info)
                    ret = ExecCommandDialog.ShowModal()
                    rs = ''
                    if (ret == wx.ID_OK):
                        #获得下载文件的返回信息
                        self.ExecCommandInfo = ExecCommandDialog.OnGetResponseInfo()
                        if self.ExecCommandInfo != None:
                            rs = self.ExecCommandInfo
                            self.TextEditorShow(rs)
                    ExecCommandDialog.Destroy()
                    if rs != '':
                        self.TextEditorShow(rs)
                except Exception,e:
                    message=u"系统出现异常："+str(e)
                    wx.MessageBox(message,u"IOMS集中运维管理系统：",style=wx.OK|wx.ICON_ERROR)
        event.Skip()
    #服务器自更新
    def OnToUpdateSelf(self, event):
        """自更新按钮方法"""
        cmd_info = []
        if self.checkItems(self.GainInfo()):
            for i in self.GainInfo():
                cmd_info.append(i[1])
            if cmd_info ==[] or (u" " in cmd_info):
                pass
            else:
                try:
                    updateSelfDialog = ActionDialog.UpdateSelfDialog(self, cmd_info)
                    ret = updateSelfDialog.ShowModal()
                    rs = ''
                    if (ret == wx.ID_OK):
                        #获得下载文件的返回信息
                        self.updateSelfInfo = updateSelfDialog.OnGetResponseInfo()
                        if self.updateSelfInfo != None:
                            rs = self.updateSelfInfo
                    updateSelfDialog.Destroy()
                    if rs != '':
                        self.TextEditorShow(rs)
                               
                except Exception,e:
                    message=u"系统出现异常："+str(e)
                    wx.MessageBox(message,u"IOMS集中运维管理系统：",style=wx.OK|wx.ICON_ERROR)        
        event.Skip()
    #显示CPU曲线图
    def OnServerCpuCurve(self, event):
        """显示CPU曲线按钮方法"""
        agentId = []
        if self.checkItems(self.GainInfo()):
            for i in self.GainInfo():
                agentId.append(i[0])
            if agentId ==[] or (u" " in agentId):
                pass
            elif len(agentId)>1:
                message = u"只能选择一个进行查询"
                wx.MessageBox(message,u"IOMS集中运维管理系统：",style=wx.OK|wx.ICON_ERROR)
            else:
                #开始时间
                startTime = datetime.datetime.now().strftime('%Y-%m-%d')
                #结束时间
                endTime = (datetime.datetime.now() + datetime.timedelta(days =1)).strftime('%Y-%m-%d')
                server = DBUtil.Server()
                #调用IOMSERVER获取CPU走势数据
                cpuCurveList = server.getServerCpuInfo(str(agentId[0]), startTime, endTime)
                
                cpuCurveDataList = []
                cpuDataHours = ""
                cpuDataLoad = 0
                for _cpuCurveList in cpuCurveList:
                    '''循环对数据进行解析重新组合'''
                    cpuLoad = _cpuCurveList[0]
                    cpuTime = time.strftime('%H', time.strptime(_cpuCurveList[1], '%Y-%m-%d %H:%M:%S'))
                    if cpuDataHours == '':
                        cpuDataHours = cpuTime
                        cpuDataLoad = 0
                    if cpuDataHours != cpuTime:
                        cpuCurveDataList.append([int(cpuDataHours), int(cpuDataLoad // 60)])
                        cpuDataHours = cpuTime
                        cpuDataLoad = 0
                    cpuDataLoad += float(cpuLoad)
                if cpuDataHours != "":
                    cpuCurveDataList.append([int(cpuDataHours), int(cpuDataLoad // 60)])
                    data = []
                    for i in range(24):
                        data.append([i*20, 0])
                    for _cpuCurveDataList in cpuCurveDataList:
                        data[_cpuCurveDataList[0]][1] = _cpuCurveDataList[1] * 2 + 5
                    #data集合中格式为x坐标位置,y坐标位置
                    #CurveUtil.LineChartExample(父窗体可为Null, 窗体ID可为-1, 左上角边框标题, 数据集合, 居中显示的标题)
                    curve = CurveUtil.LineChartExample(None, -1, u"CPU走势图", data, u"CPU走势图")
                else:
                    wx.MessageBox(u"没有搜索到数据", u"IOMS集中运维管理系统：", style=wx.OK|wx.ICON_WARNING)
        event.Skip()
    #编辑所选服务器
    def OnSingleEdit(self, event):
        """编辑按钮，编辑所选服务器信息"""
        agentId = []
        if self.checkItems(self.GainInfo()):
            if len(self.GainInfo())==1:
                for i in self.GainInfo():
                    agentId.append(i[0])
                if agentId ==[] or (u" " in agentId):
                    pass
                else:
                    page_bmp = wx.ArtProvider.GetBitmap(wx.ART_NORMAL_FILE, wx.ART_OTHER, wx.Size(16, 16))
                    self.ctrl.AddPage(self.createSingleEdit(str(agentId[0]),self.ctrl), u"编辑页面", True, page_bmp)
            elif len(self.GainInfo())<1:
                message =u"未获取到选中的信息"
                wx.MessageBox(message,u"IOMS集中运维管理系统：", style=wx.OK|wx.ICON_INFORMATION)
            else:
                #这部分代码还未添加，多选情况下应该将所有服务器的共性部分弹出供用户编辑
                message =u"多选模式"
                wx.MessageBox(message,u"IOMS集中运维管理系统：", style=wx.OK|wx.ICON_INFORMATION)
    #NoteBook中服务器进入回收站
    def OnServerGC(self, event):
        """服务器进入回收站方法"""
        try:
            agentId = []
            if self.checkItems(self.GainInfo()):
                if len(self.GainInfo()) < 1:
                    message =u"未获取到选中的信息"
                    wx.MessageBox(message,u"IOMS集中运维管理系统：", style=wx.OK|wx.ICON_INFORMATION)
                else:
                    for i in self.GainInfo():
                        agentId.append(i[0])
                    if agentId ==[] or (u" " in agentId):
                        pass
                    else:
                        #检查选择的服务器是否都不是活动状态
                        length = len(agentId)
                        activeServerLs = ServerList.AllServerList
                        activeFlag = False
                        for j in range(length):
                            for activeServer in activeServerLs:
                                if activeServer[0] == agentId[j]:
                                    activeFlag = True
                                    break
                            if activeFlag:
                                break
                        if activeFlag:
                            message=u"只有不在线的服务器才可以放入回收站。"
                        else:
                            yndlg = wx.MessageDialog(None, u'确定要删除进回收站吗？',u'警告信息：', wx.YES_NO | wx.ICON_QUESTION)
                            if yndlg.ShowModal()==wx.ID_YES:
                                server = DBUtil.Server()
                                #保存进数据库
                                if server.updateServerGC(agentId) :
                                    message=u"服务器已成功放入回收站。"
                                else :
                                    message=u"服务器放入回收站失败。"
                    wx.MessageBox(message,style=wx.OK|wx.ICON_INFORMATION)
        except Exception,e:
            message=u"系统出现异常："+str(e)
            wx.MessageBox(message,u"IOMS集中运维管理系统：",style=wx.OK|wx.ICON_ERROR)        
        event.Skip()
#页面中相应的处理方法------------------------------------------------------------------------------------------------
    #下载文件页面，下载事件处理方法
    def doDownloads(self, event):
        """执行下载文件命令"""
        if event.GetCol()==3:
            cmd_info = []
            if self.checkItems(self.GainInfo()):
                for i in self.GainInfo():
                    cmd_info.append(i[1])
                if cmd_info ==[] or (u" " in cmd_info):
                    pass
                else:
                    #获得选中的服务器列表
                    checkedServerList = []
                    for checked in cmd_info:
                        checkedServerList.append(checked)
                    #获得文件名
                    fileName = self.grid_1.GetCellValue(event.GetRow(), 0)
                    #显示确认下载提示
                    downLoadFileDialog = ActionDialog.DownLoadFileDialog(fileName, checkedServerList)
                    ret = downLoadFileDialog.ShowModal()
                    rs =''
                    if (ret == wx.ID_OK):
                        #获得下载文件的返回信息
                        self.downLoadFileInfo = downLoadFileDialog.OnGetResponseInfo()
                        if self.downLoadFileInfo != None:
                            #在消息框中输出消息
                            rs = self.downLoadFileInfo
                    downLoadFileDialog.Destroy()
                    if rs != '':
                        self.TextEditorShow(rs)
        event.Skip()
    #删除文件页面中，删除事件处理方法
    def doRemoveFiles(self, event):
        """执行删除文件命令"""
        if event.GetCol()==3:
            #获得文件名
            fileName = self.grid_2.GetCellValue(event.GetRow(), 0)
            #显示确认下载提示
            removeFilesDialog = ActionDialog.RemoveFilesDialog(self, fileName)
            ret = removeFilesDialog.ShowModal()
            if (ret == wx.ID_OK):
                #获得删除文件的返回信息
                self.removeFilesInfo = removeFilesDialog.OnGetResponseInfo()
                if self.removeFilesInfo != None:
                    self.OnRemoveFiles(event)
            removeFilesDialog.Destroy()
        event.Skip()
    #监控显示模式，执行查询
    def OnQuery(self, event):
        """监控显示模式，执行查询方法"""
        list = []
        sel_value = self.cb.GetValue()
        sel_value2 = self.cb2.GetValue()
        if sel_value == '':
            sel_value = "None"
        if sel_value == u"--请选择--":
            sel_value = "None"
        if sel_value2 == '':
            sel_value2 = "None"
        if sel_value2 == u"--请选择--":
            sel_value2 = "None"
        list.append(sel_value)
        list.append(sel_value2)
        data = self.MonitorPageData(list)
        dataType = self.MonitorPageTypeData()
        dataCol = self.MonitorPageColData()
        if data ==[]:
            data=[[u'无数据']]
        grid = self.getShowGrid()
        if data ==[[u'无数据']]:
            dataTypes=[gridlib.GRID_VALUE_STRING]
            colLabels=["-"*80+u"无相关数据"+"-"*80]
            grid.SetData(colLabels,dataTypes,data,False)
            grid.SetCellAlignment(0, 0, wx.ALIGN_CENTRE, wx.ALIGN_CENTRE)
            grid.SetReadOnly(0,0)
        else:
            grid.SetData(dataCol,dataType,data,True,7)
        grid.ForceRefresh()
    #编辑页面，提交按钮，更新修改的信息到服务器
    def OnUpdateServerButton(self,event):
        """更新服务器信息配置按钮方法"""
        try:
            #获得所有服务器列表进行循环
            self.allServerList = ServerList.AllServerList 
            for server_child in self.allServerList:
                if server_child[0] == self.agentId.GetValue():
                    #找到需要修改的服务，修改信息
                    server_child[13] = str(self.inputInfo4.GetValue())       #硬件
                    server_child[14] = str(self.inputInfo3.GetValue())       #所在机柜和层数
                    server_child[15] = str(self.inputInfo1.GetValue())       #硬件所在地址
                    server_child[16] = str(self.inputInfo13.GetValue())      #负责人
                    server_child[17] = str(self.inputInfo14.GetValue())      #负责人联系电话
                    server_child[18] = str(self.inputInfo2.GetValue())       #服务器类型
                    server = DBUtil.Server()
                    #保存进数据库
                    if server.updateServerInfo(server_child, "1") :
                        message=u"数据已成功更新。"
                    else :
                        message=u"数据更新失败。"
            
            wx.MessageBox(message,style=wx.OK|wx.ICON_INFORMATION)
        except Exception,e:
            message=u"更新数据出现异常："+str(e)
            wx.MessageBox(message,u"IOMS集中运维管理系统：",style=wx.OK|wx.ICON_ERROR)
        event.Skip()
#辅助功能函数----------------------------------------------------------------------------------------------------
    #检查页面是否存在，返回是否存在，和存在的页面位置
    def CheckPages(self,page):
        exist = [False,0]
        pages = self.ctrl.GetPageCount()
        for i in range(pages):
            #已经存在，转到以前产生的tab
            if page == self.ctrl.GetPageText(i):
                exist[0] = True
                exist[1] = i
                break
            else:
                pass
        return exist
    #获得选择服务器信息
    def GainInfo(self):
        """获得选择的服务器info"""
        items = []
        try:
            #print "row = %d" %(gridList[gridListIndex].GetNumberRows())
            #print gridListIndex
            grid = self.getShowGrid()
            rows = grid.GetNumberRows()
            cols = grid.GetNumberCols()
            id_col = 1
            nc_col = 1
            #找到为ID的列
            for i in range(cols):
                if grid.GetColLabelValue(i) == u'ID':
                    id_col = i
                    break
            for j in range(cols):
                if grid.GetColLabelValue(j) == u"网卡1":
                    nc_col = j
                    break
            #找到值为1的行
            for k in range(rows):
                if grid.GetCellValue(k,0)==u'■':
                    item = []
                    item.append(grid.GetCellValue(k,id_col))
                    item.append(grid.GetCellValue(k,nc_col))
                    items.append(item)

        except Exception,e:
            items.append("Exception")
        return items
    #检查选择服务器是否合法
    def checkItems(self,items):
        result = False
        if "Exception" in items:
            message = u"未发现数据项！"
            wx.MessageBox(message,u"IOMS集中运维管理系统：",style=wx.OK|wx.ICON_INFORMATION)
        elif [u' ', u' '] in items:
            message = u"有数据项为空！"
            wx.MessageBox(message,u"IOMS集中运维管理系统：",style=wx.OK|wx.ICON_INFORMATION)
        elif items == []:
            message = u"请至少选择一项有数据行！"
            wx.MessageBox(message,u"IOMS集中运维管理系统：",style=wx.OK|wx.ICON_INFORMATION)
        else:
            result=True
        return result
    #间隔一秒显示时间
    def Notify(self):
        """每隔1秒显示时间方法"""
        t = time.localtime(time.time())
        st = time.strftime("%Y-%m-%d %H:%M:%S", t)
        self.SetStatusText(u"系统时间："+str(st),3)
    #窗体关闭方法
    def OnClose(self, event):
        Intologs=DBUtil.User()
        yndlg = wx.MessageDialog(None, u'确定要退出系统？',u'警告信息：', wx.YES_NO | wx.ICON_QUESTION)
        if yndlg.ShowModal()==wx.ID_YES:
            Intologs.actionLog(self.CurrentAdmin, "UiLogout", u"UiLogout Succ", socket.gethostbyname(socket.gethostname()))
            self.Destroy()
    #运行结果收集程序
    def TextEditorShow(self, result):
            app = wx.PySimpleApp()
            frame=wxTextEditor.MainWindow(None,-1, u'运行结果收集程序')
            if hasattr(sys, "frozen") and getattr(sys, "frozen") == "windows_exe": 
                #以下这行专用于打包exe版本，否则运行命令出错              
                frame.readtxt(result.decode('utf-8').encode('gbk'))
            else:
                #以下这行专用于eclipse运行版本
                frame.readtxt(result)            
            app.MainLoop()
    #功能未开放提示方法
    def createInfo(self,parent=None):
        if not parent:
            parent =self
        dlg = wx.MessageDialog(self, u'此功能未开放','MessageBox',wx.OK | wx.ICON_WARNING)
        dlg.ShowModal()
        dlg.Destroy()
#事件绑定--------------------------------------------------------------------------------------------------------
    def BindEvents(self):
        self.Bind(wx.EVT_TIMER,self.Notify,self.timer)
        self.Bind(wx.EVT_CLOSE, self.OnClose)
        self.Bind(wx.EVT_TREE_SEL_CHANGED, self.OnSelChanged,self.tree)
        self.Bind(wx.EVT_TOOL, self.OnRestart, id=ID_SampleItem+1)
        self.Bind(wx.EVT_TOOL, self.OnToExecCommand, id=ID_SampleItem+2)
        self.Bind(wx.EVT_TOOL, self.OnToUpLoads, id=ID_SampleItem+3)
        self.Bind(wx.EVT_TOOL, self.OnToUpdateSelf, id=ID_SampleItem+4)
        self.Bind(wx.EVT_TOOL, self.OnToIomClient, id=ID_SampleItem+5)
        self.Bind(wx.EVT_TOOL, self.OnRemoveFiles, id=ID_SampleItem+6)
        self.Bind(wx.EVT_TOOL, self.OnSingleEdit, id=ID_SampleItem+7)
        self.Bind(wx.EVT_TOOL, self.OnServerCpuCurve, id=ID_SampleItem+8)
        self.Bind(wx.EVT_TOOL, self.OnDownloads, id=ID_SampleItem+9)
        self.Bind(wx.EVT_TOOL, self.OnServerGC, id=ID_SampleItem+10)
#欢迎页面图片
def GetIntroText():
    text = \
    "<html><body>" \
    "<img src ='"+MyUtil.cur_file_dir()+"\\img\\welcome.jpg'/>" \
    "</body></html>"
    return text
