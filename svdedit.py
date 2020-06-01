#!/usr/bin/python

import wx

import modules.devview as devview
import modules.my as my
import modules.perview as perview
import modules.regview as regview
import modules.svd as svd
import modules.tview as tview


class MyFrame(wx.Frame):
    def __init__(self, parent, id, title):
        wx.Frame.__init__(self, parent, id, title)

        self.dev = svd.device()
        self.filename = None
        self.saved = True
        self.errcount = 0

        MainMenu = wx.MenuBar()
        FileMenu = wx.Menu()
        NewFile = FileMenu.Append(wx.ID_NEW, 'New', 'New SVD')
        LoadFile = FileMenu.Append(wx.ID_OPEN, 'Load', 'Load SVD')
        SaveFile = FileMenu.Append(wx.ID_SAVE, 'Save', 'Save SVD')
        SaveAsFile = FileMenu.Append(wx.ID_SAVEAS, 'Save As', 'Save SVD')
        AppExit = FileMenu.Append(wx.ID_EXIT, 'Exit', 'Exit application')

        EditMenu = wx.Menu()
        AddItem = EditMenu.Append(wx.ID_ADD, 'Add Item', 'Add Item')
        DelItem = EditMenu.Append(wx.ID_DELETE, 'Delete Item', 'Delete Item')
        CloneItem = EditMenu.Append(wx.ID_DUPLICATE, 'Clone Item', 'Clone Item')

        ToolsMenu = wx.Menu()
        ValidItem = ToolsMenu.Append(wx.ID_ANY, 'Validate', 'Run Validation')
        CompactItem = ToolsMenu.Append(wx.ID_ANY, 'Compact', 'Compact')

        InfoMenu = wx.Menu()
        AboutNfo = InfoMenu.Append(wx.ID_ABOUT, 'About', 'About this program')

        MainMenu.Append(FileMenu, '&File')
        MainMenu.Append(EditMenu, '&Edit')
        MainMenu.Append(ToolsMenu, '&Tools')
        MainMenu.Append(InfoMenu, '&Info')
        self.SetMenuBar(MainMenu)

        self.Bind(wx.EVT_MENU, self.OnLoad, LoadFile)
        self.Bind(wx.EVT_MENU, self.OnNew, NewFile)
        self.Bind(wx.EVT_MENU, self.OnSave, SaveFile)
        self.Bind(wx.EVT_MENU, self.OnSaveAs, SaveAsFile)
        self.Bind(wx.EVT_MENU, self.OnExit, AppExit)

        self.Bind(wx.EVT_MENU, self.OnAddItem, AddItem)
        self.Bind(wx.EVT_MENU, self.OnDelItem, DelItem)
        self.Bind(wx.EVT_MENU, self.OnCloneItem, CloneItem)

        self.Bind(wx.EVT_MENU, self.OnValidItem, ValidItem)
        self.Bind(wx.EVT_MENU, self.OnCompactItem, CompactItem)

        self.Bind(wx.EVT_MENU, self.OnAbout, AboutNfo)

        self.Bind(my.MY_EVT, self.OnMyCommand)
        
        accel_tbl = wx.AcceleratorTable([
                                            (wx.ACCEL_CTRL,  ord('A'), wx.ID_ADD ),
                                            (wx.ACCEL_CTRL,  ord('S'), wx.ID_SAVE),
                                            (wx.ACCEL_CTRL,  ord('C'), wx.ID_DUPLICATE),
                                        ])
        self.SetAcceleratorTable(accel_tbl)

        # Create a main window
        self.splitter = wx.SplitterWindow(self)
        self.tree = tview.View(self.splitter, self.dev)
        self.view = devview.View(self.splitter, self.dev)
        self.splitter.SplitVertically(self.tree, self.view)

        self.OnNew(None)

        mSizer = wx.BoxSizer(wx.VERTICAL)
        mSizer.Add(self.splitter, 1, wx.EXPAND | wx.ALL, 0)
        self.SetSizerAndFit(mSizer)

        p = self.splitter.GetSashPosition()
        self.splitter.SetSashPosition(p)

        self.Bind(wx.EVT_SPLITTER_DCLICK, self.onTryUnsplit)

        self.Centre()

    def onTryUnsplit(self, event):
        event.Veto()

    def OnMyCommand(self, event):
        eid = event.GetId()
        eobj = event.GetClientData()
        if eid == my.EVT_SELECTED:
            old = self.view
            new = None
            self.splitter.Freeze()
            if isinstance(eobj, svd.register):
                new = regview.View(self.splitter, eobj)
            if isinstance(eobj, svd.peripheral):
                new = perview.View(self.splitter, eobj)
            if isinstance(eobj, svd.device):
                new = devview.View(self.splitter, eobj)
            if new is not None and new != old:
                self.splitter.ReplaceWindow(old, new)
                self.view = new
                old.Destroy()
            self.splitter.Thaw()
            return
        elif eid == my.EVT_REG_NAME_CHANGED or eid == my.EVT_PER_NAME_CHANGED or eid == my.EVT_DEV_NAME_CHANGED:
            self.tree.Reload(eobj)
        elif eid == my.EVT_REG_DELETED or eid == my.EVT_PER_DELETED:
            self.tree.Remove(eobj)
        elif eid == my.EVT_REG_ADDED or eid == my.EVT_PER_ADDED:
            self.tree.Append(eobj)
        if self.saved:
            self.SetLabel('* %s' % (self.GetLabel()))
            self.saved = False

    def OnCompactItem(self, event):
        for p in self.dev.peripherals:
            for r in p.registers:
                if r.rsize == r.parent.vsize:
                    r._rsize = None
                if r.rvalue is not None and int(r.rvalue, 0) == int(r.parent.vvalue, 0):
                    r.rvalue = None
                if r.access == r.parent.vaccess:
                    r._access = None
                for f in r.fields:
                    if f._access == f.parent.vaccess:
                        f._access = None

    def ValidateCallback(self, msg):
        self.errcount = self.errcount + 1
        res = wx.MessageBox(msg, 'Continue validation ?', wx.YES_NO | wx.ICON_ERROR)
        return True if res == wx.NO else False

    def OnValidItem(self, event):
        self.errcount = 0
        if self.dev.validate(self.ValidateCallback):
            wx.MessageBox('Validation canceled')
        else:
            wx.MessageBox('%s errors found' % (self.errcount if self.errcount else 'No'))

    def OnAddItem(self, event):
        obj = self.FindFocus()
        self.view.AddItem(obj)
        self.tree.AddItem(obj)

    def OnCloneItem(self, event):
        obj = self.FindFocus()
        self.view.CloneItem(obj)
        self.tree.CloneItem(obj)

    def OnDelItem(self, event):
        obj = self.FindFocus()
        self.view.DelItem(obj)
        self.tree.DelItem(obj)

    def OnNew(self, event):
        self.dev.fromString(svd.default_xml)
        self.tree.LoadDevice(self.dev)
        self.filename = None
        self.SetLabel('New - SVD editor')

    def OnLoad(self, event):
        LoadSvdDialog = wx.FileDialog(self,
                                      'Open System View Description file', '', '',
                                      'SVD files(*.svd)|*.svd', wx.FD_OPEN)
        if LoadSvdDialog.ShowModal() == wx.ID_OK:
            self.filename = LoadSvdDialog.GetPath()
            self.dev.load(self.filename)
            self.tree.LoadDevice(self.dev)
            self.saved = True
            self.SetLabel('%s - SVD editor' % (self.filename))

    def OnSave(self, event):
        if self.filename:
            self.dev.save(self.filename)
            self.saved = True
            self.SetLabel('%s - SVD editor' % (self.filename))

    def OnSaveAs(self, event):
        SaveSvdDialog = wx.FileDialog(self,
                                      'Save System View Description file', '', self.dev.name + '.svd',
                                      'SVD files(*.svd)|*.svd', wx.FD_SAVE | wx.FD_OVERWRITE_PROMPT)
        if SaveSvdDialog.ShowModal() == wx.ID_OK:
            self.filename = SaveSvdDialog.GetPath()
            self.dev.save(self.filename)
            self.saved = True
            self.SetLabel('%s - SVD editor' % (self.filename))

    def OnAbout(self, event):
        info = wx.AboutDialogInfo()
        info.SetName('SVD editor')
        info.SetVersion(svd.__version__)
        info.SetDescription('CMSIS System View Description editor tool')
        info.SetCopyright('(C) 2017 Dmitry Filimonchuk')
        lfile = open('LICENSE', 'r')
        if lfile:
            info.SetLicense(lfile.read())
        info.WebSite = ('http://github.com/dmitrystu')
        wx.AboutBox(info)

    def OnExit(self, event):
        self.Destroy()


class MyApp(wx.App):
    def OnInit(self):
        frame = MyFrame(None, -1, 'SVD editor')
        frame.Show(True)
        self.SetTopWindow(frame)
        return True


if __name__ == '__main__':
    app = MyApp(0)
    app.MainLoop()
