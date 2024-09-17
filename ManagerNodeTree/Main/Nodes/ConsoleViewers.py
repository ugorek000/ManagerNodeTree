import bpy, sys, datetime, functools
from .Bases import ManagerNodeRoot

from .. import Utils
from ...uu_ly import LyNiceColorProp

from ... import opa as opa
from ..Utils import GlobalsUtilsInUserExec as utils

list_consoleLog = [""]

def NcvLog(txtData):
    for cyc, li in enumerate(txtData.split("\n")):
        if cyc:
            list_consoleLog.append("")
        list_consoleLog[-1] += li
    if bpy.data.__class__.__name__!="_RestrictData":
        assert bpy.data.__class__.__name__=="BlendData"
        for li in Utils.DgCollectEvalDoubleGetFromDict(dict_necvNdSubscribeToUpdate):
            li[1].WriteLog(txtData)
class NcvOverrideStdOut():
    def write(txt):
        sys.__stdout__.write(txt)
        NcvLog(txt)
class NcvOverrideStdErr():
    def write(txt):
        sys.__stderr__.write(txt)
        import ctypes; MessageBox = ctypes.windll.user32.MessageBoxW; MessageBox(None, "Омайгад, оно используется!", "Mng Debug", 0)
        NcvLog(txt)

class ManagerNodeConsole(ManagerNodeRoot):
    nclass = 33
    bl_width_max = 2048
    bl_width_min = 256
    def free(self):
        sys.stdout = sys.__stdout__
        sys.stderr = sys.__stderr__
    def LyDrawExtNodePreChain(self, _context, colLy, _prefs):
        ManagerNodeRoot.LyDrawExtNodePreChain(self, _context, colLy, _prefs)
        colLy.prop(self,'count')
    def LyDrawNodePreChain(self, _context, colLy, prefs):
        ManagerNodeRoot.LyDrawNodePreChain(self, _context, colLy, prefs)
        if prefs.isAllowNcWorking:
            if sys.stdout!=NcvOverrideStdOut: #sys.stdout==sys.__stdout__ #"Явная" суета для перерегистраций.
                sys.stdout = NcvOverrideStdOut
            if sys.stderr!=NcvOverrideStdOut: #sys.stderr==sys.__stderr__
                sys.stderr = NcvOverrideStdOut
        else:
            if sys.stdout!=sys.__stdout__:
                sys.stdout = sys.__stdout__
            if sys.stderr!=sys.__stderr__:
                sys.stderr = sys.__stderr__

class NodeSimpleConsoleViewer(ManagerNodeConsole):
    bl_idname = 'MngNodeSimpleConsoleViewer'
    bl_label = "Simple Console Viewer"
    bl_width_default = 448
    possibleDangerousGradation = 1
    mngCategory = "4Hacking", 1
    count: bpy.props.IntProperty(name="Count of lines", default=32, min=0, max=1024)
    def LyDrawNode(self, _context, colLy, _prefs):
        colList = colLy.column(align=True)
        for li in list_consoleLog[-self.count-1:-1]:
            colList.label(text=li)

dict_necvNdSubscribeToUpdate = {}

def NecvLiUpdateMsg(self, _context):
    self['msg'] = self.msgProvReadOnly
class NecvLineItem(Utils.PgNodeCollectionItemWithGetNdSelf):
    msg: bpy.props.StringProperty(name="Line Body", default="", update=NecvLiUpdateMsg)
    msgProvReadOnly: bpy.props.StringProperty(update=NecvLiUpdateMsg)
def NecvUpdateCount(self, _context):
    self.WriteLog("")
class NodeConsoleViewer(ManagerNodeConsole):
    bl_idname = 'MngNodeConsoleViewer'
    bl_label = "Console Viewer"
    bl_icon = 'CONSOLE'
    bl_width_default = 660
    possibleDangerousGradation = 2
    mngCategory = "4Hacking", 2
    lines: bpy.props.CollectionProperty(type=NecvLineItem)
    count: bpy.props.IntProperty(name="Limit of lines", default=16, min=1, max=256, update=NecvUpdateCount)
    isDisplayAsProp: bpy.props.BoolProperty(name="Display as prop", default=True)
    isDisplayTime: bpy.props.BoolProperty(name="Display time", default=True)
    txtTimeFormat: bpy.props.StringProperty(name="Time format", default="%y.%m.%d  %H:%M:%S")
    txtExecOnUpdate: bpy.props.StringProperty(name="Exec on update", default="", description="{'bpy':bpy, 'C':bpy.context, 'D':bpy.data, 'opa':opa, 'utils':utils, 'self':self, 'msg':txtData}")
    decorVars: bpy.props.IntProperty(name="Decor", default=1, min=0, max=15)
    def InitNode(self, _context):
        self.lines.add().name = datetime.datetime.now().strftime(self.txtTimeFormat)
        #self.txtExecOnUpdate = "if \"\\n\" in msg: self.label = str(int(self.label if self.label else 0)+1)"
    def DrawLabel(self):
        Utils.DgProcAddSelfInDictSpec(self, dict_necvNdSubscribeToUpdate)
        return ""
    def LyDrawExtNode(self, _context, colLy, _prefs):
        colLy.prop(self,'isDisplayAsProp')
        colGroup = colLy.column(align=True)
        colGroup.prop(self,'isDisplayTime')
        row = colGroup.row(align=True)
        LyNiceColorProp(row, self,'txtTimeFormat', text="Time f:", align=True)
        row.active = self.isDisplayTime
        colGroup = colLy.column(align=True)
        colGroup.prop(self,'decorVars')
        LyNiceColorProp(colLy, self,'txtExecOnUpdate', text="On Update:", icon='SCRIPT', align=True)
        row = colLy.row(align=True)
        row.operator(Utils.OpSimpleExec.bl_idname, text="Clear").exc = f"nd = {self.__mng_repr__()}; nd.lines.clear(); nd.lines.add(); bpy.context.area.tag_redraw()"
        row.label()
    def LyDrawNode(self, _context, colLy, _prefs):
        colList = colLy.column(align=True)
        suDecorVars = self.decorVars
        suIsDisplayAsProp = self.isDisplayAsProp
        for ci in self.lines[:-1]:
            rowItem = colList.row(align=True)
            if self.isDisplayTime:
                rowTime = rowItem.row(align=True)
                rowTime.active = suDecorVars//4%2
                rowTime.alert = suDecorVars//8%2
                rowTime.alignment = 'CENTER'
                rowTime.label(text=ci.name)
            rowMsg = rowItem.row(align=True)
            rowMsg.active = suDecorVars%2
            rowMsg.alert = suDecorVars//2%2
            if suIsDisplayAsProp:
                rowMsg.prop(ci,'msg', text="")
            else:
                rowMsg.label(text=ci.msg)
    def DoLog(self, txtData):
        for cyc, li in enumerate(txtData.split("\n")):
            txt = datetime.datetime.now().strftime(self.txtTimeFormat) #str(int(self.lines[-1].name)+1)
            if cyc:
                self.lines.add().name = txt
            else:
                self.lines[-1].name = txt
            ci = self.lines[-1]
            ci.msgProvReadOnly += li
        for cyc in range(self.count+1, length(self.lines)):
            self.lines.remove(0)
    def WriteLog(self, txtData):
        if self.txtExecOnUpdate:
            exec(self.txtExecOnUpdate, {'bpy':bpy, 'C':bpy.context, 'D':bpy.data, 'opa':opa, 'utils':utils, 'self':self, 'msg':txtData}, {})
        try: #"Нельзя писать в рисовании".
            self.lines[-1].name = self.lines[-1].name
        except:
            bpy.app.timers.register(functools.partial(self.DoLog, txtData))
            return
        self.DoLog(txtData)

Wh.Lc(*globals().values())