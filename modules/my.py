from collections import namedtuple
import wx
import wx.grid
import wx.lib.newevent

Evt, MY_EVT = wx.lib.newevent.NewCommandEvent()

EVT_FIELD_ADDED         = (100)
EVT_FIELD_DELETED       = (110)


EVT_REG_ADDED           = (200)
EVT_REG_DELETED         = (205)
EVT_REG_NAME_CHANGED    = (210)
EVT_REG_ACCS_CHANGED    = (220)


EVT_PER_ADDED           = (300)
EVT_PER_DELETED         = (305)
EVT_PER_NAME_CHANGED    = (310)
EVT_PER_OFFS_CHANGED    = (320)
EVT_PER_GROUP_CHANGED   = (330)
EVT_PER_REF_CHANGED     = (340)


EVT_DEV_NAME_CHANGED    = (405)

EVT_INT_ADDED           = (500)
EVT_INT_DELETED         = (505)

EVT_SELECTED            = (600)


def post_event(dest, event, object):
    ev = Evt(event)
    ev.SetClientData(object)
    wx.PostEvent(dest, ev)


class myTable(wx.grid.PyGridTableBase):
    wItem = namedtuple('WorkItem', 'atrib, item')

    def __init__(self, parent, data):
        wx.grid.PyGridTableBase.__init__(self)
        self.parent = parent
        self.data = data
        self.colorInactive = wx.SystemSettings.GetColour(wx.SYS_COLOUR_GRAYTEXT)

        self.editor = wx.grid.GridCellChoiceEditor(['default', 'read-only', 'read-write', 'write-only', 'writeOnce', 'read-writeOnce'])
        #self.editor.IncRef()
        #self.editor.IncRef()

        self.attr_dd = wx.grid.GridCellAttr()
        self.attr_dd.SetEditor(self.editor)
        #self.attr_dd.IncRef()

        self.attr_dg = wx.grid.GridCellAttr()
        self.attr_dg.SetEditor(self.editor)
        self.attr_dg.SetTextColour(self.colorInactive)
        #self.attr_dg.IncRef()

        self.attr_ro = wx.grid.GridCellAttr()
        self.attr_ro.SetReadOnly(True)
        self.attr_ro.SetTextColour(self.colorInactive)
        #self.attr_ro.IncRef()

        self.attr_g = wx.grid.GridCellAttr()
        self.attr_g.SetTextColour(self.colorInactive)
        #self.attr_g.IncRef()

    #def __del__(self):
        #self.attr_g.DecRef()
        #self.attr_ro.DecRef()
        #self.attr_dg.DecRef()
        #self.attr_dd.DecRef()
        #self.editor.DecRef()
        #wx.grid.GridTableBase.__del__(self)

    def Attr(self, atype):
        attr = {'ReadOnly': self.attr_ro.Clone(),
                'DropDown': self.attr_dd.Clone(),
                'DropGray': self.attr_dg.Clone(),
                'Gray': self.attr_g.Clone()
        }.get(atype, None)
        #if attr:
            #attr.IncRef()
            #attr.SetEditor(self.editor)
        return attr


class myGrid(wx.grid.Grid):
    def __init__(self, parent):
        wx.grid.Grid.__init__(self, parent)
        self.parent = parent
        self.DisableDragGridSize()

    def FitWidth(self, col):

        self.BeginBatch()
        pw, ph = self.GetClientSize()
        self.AutoSize()
        cw = self.GetRowLabelSize()
        for x in range(0, self.GetNumberCols()):
            cw += self.GetColSize(x)
        delta = pw - cw
        nw = self.GetColSize(col) + delta
        if nw > 20:
            self.SetColSize(col, nw)
            dw, dh = self.GetSize()
            dw += delta
            self.SetSize((dw, ph))
        self.EndBatch()
