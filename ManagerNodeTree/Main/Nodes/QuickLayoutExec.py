import bpy
from .Bases import ManagerNodeAlertness

from .. import Utils
from ... import uu_ly

from ... import opa as opa
from ..Utils import GlobalsUtilsInUserExec as utils

class NqleOpDelLine(bpy.types.Operator):
    bl_idname = 'mng.nqle_del_line'
    bl_label = "NqleOpDelLine"
    bl_options = {'UNDO'}
    repr: bpy.props.StringProperty()
    num: bpy.props.IntProperty()
    def execute(self, context):
        ndRepr = eval(self.repr)
        ndRepr.lines.remove(self.num)
        dict_nqleNdCompiledCache[ndRepr] = None
        ndRepr.count = length(ndRepr.lines)
        return {'FINISHED'}

dict_nqleNdCompiledCache = {}

def NqleUpdateForReCompile(self, _context):
    dict_nqleNdCompiledCache[self.GetSelfNode(NodeQuickLayoutExec.bl_idname, 'lines')] = None
class NqleLineItem(Utils.PgNodeCollectionItemWithGetNdSelf):
    fit = "Exec: {'bpy':bpy, 'C':bpy.context, 'D':bpy.data, 'opa':opa, 'utils':utils, 'self':self}\nLayout |= {'ly': colLy}"
    isActive:  bpy.props.BoolProperty(name="Active",     default=True,        update=NqleUpdateForReCompile)
    isTb:      bpy.props.BoolProperty(name="Toggle",     default=False,       update=NqleUpdateForReCompile)
    tbPoi:  bpy.props.PointerProperty(name="Text Block", type=bpy.types.Text, update=NqleUpdateForReCompile, description=fit)
    txtExec: bpy.props.StringProperty(name="Text Exec",  default="",          update=NqleUpdateForReCompile, description=fit)
    del fit

def NqleUpdateCount(self, _context):
    len = length(self.lines)
    #if len!=self.count: #Заметка: Поскольку изменение количества добавляет и удаляет только пустые, в перекомпиляции нет нужды.
    #    dict_nqleNdCompiledCache[self] = None
    for cyc in range(len, self.count):
        self.lines.add().name = str(cyc)
    for cyc in reversed(range(self.count, len)):
        if not(self.lines[cyc].txtExec or self.lines[cyc].tbPoi):
            self.lines.remove(cyc)
    self['count'] = length(self.lines)
def NqleUpdateMethod(self, _context):
    self.soldIsAsExc = self.method=='EXEC'
class NodeQuickLayoutExec(ManagerNodeAlertness):
    nclass = 10
    bl_idname = 'MngNodeQuickLayoutExec'
    bl_label = "Quick Layout Exec"
    bl_icon = 'LONGDISPLAY'
    bl_width_max = 2048
    bl_width_min = 64
    bl_width_default = 430
    possibleDangerousGradation = 2
    mngCategory = "2Script", 0
    lines: bpy.props.CollectionProperty(type=NqleLineItem)
    method: bpy.props.EnumProperty(name="Method", default='LAYOUT', items=( ('LAYOUT',"As Layout",""), ('EXEC',"As Exec","") ), update=NqleUpdateMethod)
    soldIsAsExc: bpy.props.BoolProperty()
    count: bpy.props.IntProperty(name="Count of lines", default=1, min=1, max=64, soft_min=1, soft_max=16, update=NqleUpdateCount)
    isCaching: bpy.props.BoolProperty(name="Caching", default=True)
    isShowOnlyLayout: bpy.props.BoolProperty(name="Layout display only", default=False)
    txtVaribleForAlert: bpy.props.StringProperty(name="Varible for alert", default="alert")
    decorExec: bpy.props.StringProperty(name="Decor Exec button", default="Exec")
    visibleButtons: bpy.props.IntProperty(name="Visibility of buttons", default=15, min=0, max=15)
    def DrawLabel(self):
        return "Quick Exec" if self.soldIsAsExc else "Quick Layout"
    def InitNode(self, _context):
        self.method = self.bl_rna.properties['method'].default #Для soldIsAsExc.
        self.count = self.bl_rna.properties['count'].default #Для NqleUpdateCount().
        self.lines[0].txtExec = "ly.label(text=\"Hello_World\")"
    def LyDrawExtNode(self, _context, colLy, _prefs):
        colList = colLy.column(align=True)
        colList.row().prop(self,'method', expand=True)
        colList.prop(self,'count')
        if self.soldIsAsExc:
            uu_ly.LyNiceColorProp(colList, self,'decorExec', text="Decor Exec:", align=True)
        else:
            colList.prop(self,'isCaching')
        colList.prop(self,'isShowOnlyLayout')
        uu_ly.LyNiceColorProp(colList, self,'txtVaribleForAlert')
        row = colList.row(align=True)
        row.prop(self,'visibleButtons')
        row.active = not self.isShowOnlyLayout
        colLy.separator()
        colOps = colLy.column(align=True)
        row = colOps.row()
        row.operator(Utils.OpSimpleExec.bl_idname, text="Copy as script").exc = f"bpy.context.window_manager.clipboard = {self.__mng_repr__()}.GetCollectedFullText()"
        row.operator(Utils.OpSimpleExec.bl_idname, text="Paste as script").exc = f"{self.__mng_repr__()}.SetLinesFromFullText(bpy.context.window_manager.clipboard)"
    def LyDrawNode(self, _context, colLy, prefs):
        if not self.isShowOnlyLayout:
            colLines = colLy.column(align=True)
            visibleButs = self.visibleButtons
            for cyc, ci in enumerate(self.lines):
                rowLine = colLines.row().row(align=True)
                rowEnb = rowLine.row(align=True)
                if visibleButs%2:
                    rowEnb.prop(ci,'isActive', text="")
                rowEnb.active = False
                rowTb = rowLine.row(align=True)
                if (visibleButs>>1)%2:
                    fit = (ci.isTb)and(not ci.txtExec)or not(ci.isTb or not ci.tbPoi) #Показать пользователю подсветкой, что на противоположном варианте что-то есть, и "не забудь про это".
                    rowTb.prop(ci,'isTb', text="", icon='WORDWRAP_OFF', emboss=True, invert_checkbox=fit) #RIGHTARROW  GREASEPENCIL  WORDWRAP_OFF  ALIGN_JUSTIFY
                rowTb.active = False
                if (self.soldIsAsExc)and((visibleButs>>2)%2):
                    row = rowLine.row(align=True)
                    row.operator(Utils.OpSimpleExec.bl_idname, text="", icon='TRIA_RIGHT').exc = f"{self.__mng_repr__()}.ExecuteOne({cyc})"
                    row.active = not(ci.isTb and not ci.tbPoi)
                if ci.isTb:
                    rowLine.prop(ci,'tbPoi', text="", icon='TEXT')
                else:
                    rowLine.prop(ci,'txtExec', text="", icon='SCRIPT')
                if (visibleButs>>3):
                    rowLine.operator_props(NqleOpDelLine.bl_idname, text="", icon='TRASH', repr=self.__mng_repr__(), num=cyc)
                rowLine.active = ci.isActive
        if self.soldIsAsExc:
            if self.decorExec:
                colLy.operator(Utils.OpSimpleExec.bl_idname, text=self.decorExec).exc = f"{self.__mng_repr__()}.ExecuteAll()"
        elif prefs.isAllowNqleWorking:
            with uu_ly.TryAndErrInLy(colLy): #Заметка: Лучше оставить, ибо часто будут использоваться функции.
                #Заметка: Компиляция с кешированием должны быть по нужде, а не сразу при изменении содержания; чтобы при редактировании через скрипты не вызывать бесполезные вычисления.
                if not( (self.isCaching)and(dict_nqleNdCompiledCache.get(self)) ):
                    dict_nqleNdCompiledCache[self] = compile(self.GetCollectedFullText(), "", 'exec')
                dict_globals = self.DoExecute(dict_nqleNdCompiledCache[self], dict_vars={'ly': colLy.column()})
                if self.txtVaribleForAlert in dict_globals:
                    self.ProcAlertState(dict_globals[self.txtVaribleForAlert])
    def DoExecute(self, ess, *, dict_vars={}):
        dict_globals = {'bpy':bpy, 'C':bpy.context, 'D':bpy.data, 'opa':opa, 'utils':utils, 'self':self}|dict_vars
        exec(ess, dict_globals, dict_globals)
        return dict_globals
    def ExecuteOne(self, inx):
        ci = self.lines[inx]
        return self.DoExecute(ci.txtExec if not ci.isTb else ci.tbPoi.as_string() if ci.tbPoi else "")
    def ExecuteAll(self):
        return self.DoExecute(self.GetCollectedFullText())
    def GetCollectedFullText(self):
        txtAcc = ""
        sco = 0
        for ci in self.lines:
            if ci.isActive:
                if ci.isTb:
                    if ci.tbPoi:
                        txtAcc += "\n"*(not not sco)+ci.tbPoi.as_string()
                        sco += 1
                else:
                    txtAcc += "\n"*(not not sco)+ci.txtExec
                    sco += 1
        return txtAcc
    def SetLinesFromFullText(self, text):
        self.lines.clear()
        for txt in text.split("\n"):
            self.lines.add().txtExec = txt
        self['count'] = length(self.lines)

Wh.Lc(*globals().values())