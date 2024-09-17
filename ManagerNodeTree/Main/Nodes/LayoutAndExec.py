import bpy
from .Bases import ManagerNodeAlertness

from ..Utils import OpSimpleExec
from ... import uu_ly

from ... import opa as opa
from ..Utils import GlobalsUtilsInUserExec as utils

class NlaeOp(bpy.types.Operator):
    bl_idname = 'mng.nlae'
    bl_label = "NlaeOp"
    bl_options = {'UNDO'}
    def execute(self, context):
        context.node.Execute(self) #Вся надежда на 'context.node'.
        return {'FINISHED'}

dict_nlaeNdCompiledCache = {}

def NlaeUpdateForReCompile(self, _context):
    dict_nlaeNdCompiledCache[self] = None
class NodeLayoutAndExec(ManagerNodeAlertness):
    nclass = 10
    bl_idname = 'MngNodeLayoutAndExec'
    bl_label = "Layout and Exec"
    #bl_icon = 'SYNTAX_ON'
    bl_width_max = 2048
    bl_width_min = 64
    bl_width_default = 220
    possibleDangerousGradation = 2
    mngCategory = "2Script", 1
    fit = "Exec: {'bpy':bpy, 'C':bpy.context, 'D':bpy.data, 'opa':opa, 'utils':utils, 'self':self}\nLayout |= {'bop':NlaeOp.bl_idname}"
    txtCode: bpy.props.StringProperty(name="Text Code", default="",            update=NlaeUpdateForReCompile, description=fit)
    tbPoi:   bpy.props.PointerProperty(name="Text Block", type=bpy.types.Text, update=NlaeUpdateForReCompile, description=fit)
    isTb:    bpy.props.BoolProperty(name="Use Text Block", default=False,      update=NlaeUpdateForReCompile)
    txtVaribleForAlert: bpy.props.StringProperty(name="Varible for alert",      default="alert")
    txtNameLyFunc:      bpy.props.StringProperty(name="Name for Ly function",   default="Layout")
    txtNameExecFunc:    bpy.props.StringProperty(name="Name for Exec function", default="Execute")
    del fit
    def GetTextCode(self): #Повторение-алерт; у NodeAssertor такая же.
        if self.isTb:
            if self.tbPoi:
                return self.tbPoi.as_string()
            else:
                return ""
        else:
            return self.txtCode
    def InitNode(self, _context):
        self.txtCode = "print№(f\"*init nlae code* (from \\\"{self.name}\\\")\")\n\ndef Layout(ly):\n  ly.operator(bop, text=\"Hello World\")\n".replace("№", "")
        self.txtCode += "\ndef Execute(op):\n  op.report({'INFO'}, \"Hello World\")\n  self.label = \"(see console)\"\n  print№(\"Hello World\")".replace("№", "")
    def LyDrawExtNode(self, _context, colLy, _prefs):
        colList = colLy.column(align=True)
        colList.prop(self,'isTb')
        rowCode = colList.row(align=True)
        rowCode.prop(self,'txtCode', text="", icon='SCRIPT', placeholder="Code")
        rowCode.active = not self.isTb
        rowCpPs = rowCode.row(align=True)
        rowCpPs.operator(OpSimpleExec.bl_idname, text="", icon='COPYDOWN').exc = f"bpy.context.window_manager.clipboard = {self.__mng_repr__()}.txtCode"
        rowCpPs.operator(OpSimpleExec.bl_idname, text="", icon='PASTEDOWN').exc = f"{self.__mng_repr__()}.txtCode = bpy.context.window_manager.clipboard"
        rowCpPs.scale_x = 2.0
        rowTb = colList.row(align=True)
        rowTb.prop(self,'tbPoi', text="", icon='TEXT')
        rowTb.active = self.isTb
        uu_ly.LyNiceColorProp(colList, self,'txtVaribleForAlert')
        uu_ly.LyNiceColorProp(colList, self,'txtNameLyFunc')
        uu_ly.LyNiceColorProp(colList, self,'txtNameExecFunc')
    ##
    def DoExecAsAlways(self, txtSearchFunc, *, argsSearchFunc=(), dict_vars={}): #Не используется.
        if not(dict_nlaeNdCompiledCache.get(self)):
            dict_nlaeNdCompiledCache[self] = compile(self.GetTextCode(), "", 'exec')
        dict_globals = {'bpy':bpy, 'C':bpy.context, 'D':bpy.data, 'opa':opa, 'utils':utils, 'self':self}|dict_vars
        exec(dict_nlaeNdCompiledCache[self], dict_globals, dict_globals)
        return self.ProcPostExec(dict_globals, txtSearchFunc, argsSearchFunc)
    def DoExecAsFrozen(self, txtSearchFunc, *, argsSearchFunc=(), dict_vars={}):
        if not(dict_nlaeNdCompiledCache.get(self)):
            dict_globals = {'bpy':bpy, 'C':bpy.context, 'D':bpy.data, 'opa':opa, 'utils':utils, 'self':self}|dict_vars
            exec(compile(self.GetTextCode(), "", 'exec'), dict_globals, dict_globals)
            dict_nlaeNdCompiledCache[self] = dict_globals
        dict_globals = dict_nlaeNdCompiledCache[self]
        return self.ProcPostExec(dict_globals, txtSearchFunc, argsSearchFunc)
    def ProcPostExec(self, dict_globals, txtSearchFunc, argsSearchFunc):
        if txtSearchFunc in dict_globals:
            dict_globals[txtSearchFunc](*argsSearchFunc)
        if self.txtVaribleForAlert in dict_globals:
            self.ProcAlertState(dict_globals[self.txtVaribleForAlert])
        return dict_globals
    ##
    def LyDrawNode(self, _context, colLy, _prefs):
        with uu_ly.TryAndErrInLy(colLy):
            self.DoExecAsFrozen(self.txtNameLyFunc, argsSearchFunc=(colLy,), dict_vars={'bop':NlaeOp.bl_idname}) #Заметка: Здесь не `'ly':colLy`, иначе краш; ("я сначала не понял, а потом каак понял").
    def Execute(self, op=None):
        self.DoExecAsFrozen(self.txtNameExecFunc, argsSearchFunc=(op,))

Wh.Lc(*globals().values())