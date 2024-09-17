import bpy, time, functools
from .Bases import ManagerNodeAlertness

from .. import Utils
from ...uu_ly import LyNiceColorProp

from ... import opa as opa
from ..Utils import GlobalsUtilsInUserExec as utils

dict_naNdCompileCache = {}
dict_naNdLastRunTime = {} #И снова "нельзя писать в рисовании".
dict_naNdAwLastAlertState = {}
dict_naNdIsAlwaysWorks = {}

def NaTimerNdWorkingAlways(reprNd):
    reprGetTree, reprTreeGetNd = dict_naNdIsAlwaysWorks[reprNd]
    if (not eval(reprGetTree))or(not(ndRepr:=eval(reprTreeGetNd)))or(not ndRepr.isAlwaysWorks):
        del dict_naNdIsAlwaysWorks[reprNd]
        return None
    tgl = ndRepr.Assert()
    if (ndRepr not in dict_naNdAwLastAlertState)or(dict_naNdAwLastAlertState[ndRepr]!=tgl):
        dict_naNdAwLastAlertState[ndRepr] = tgl
        ndRepr.label = ndRepr.label
    return ndRepr.speedLimit
def NaUpdateForReCompile(self, _context):
    dict_naNdCompileCache[self] = None
    dict_naNdLastRunTime[self] = 0.0
class NodeAssertor(ManagerNodeAlertness):
    nclass = 5 #42 #10 #40 #41
    bl_idname = 'MngNodeAssertor'
    bl_label = "Assert"
    bl_icon = 'STYLUS_PRESSURE' #STYLUS_PRESSURE  CAMERA_STEREO  MEMORY  HAND
    bl_width_max = 1200
    bl_width_min = 140
    bl_width_default = 300
    possibleDangerousGradation = 2
    mngCategory = "2Script", 2
    fit = "{'bpy':bpy, 'C':bpy.context, 'D':bpy.data, 'opa':opa, 'utils':utils, 'self':self}"
    method: bpy.props.EnumProperty(name="Method", default='EVAL', items=( ('EXEC',"Exec",""), ('EVAL',"Eval","") ), update=NaUpdateForReCompile)
    txtAssert: bpy.props.StringProperty(name="Text Assert", default="",          update=NaUpdateForReCompile, description=fit)
    tbPoi:     bpy.props.PointerProperty(name="Text Block", type=bpy.types.Text, update=NaUpdateForReCompile, description=fit)
    isTb:      bpy.props.BoolProperty(name="Use Text Block", default=False,      update=NaUpdateForReCompile)
    speedLimit: bpy.props.FloatProperty(name="Speed limit", default=1.0, min=0.0, max=60.0)
    isCaching:      bpy.props.BoolProperty(name="Caching",        default=True)
    isAlwaysWorks:  bpy.props.BoolProperty(name="Always works",   default=False)
    isLyReadOnly:   bpy.props.BoolProperty(name="Read only",      default=False)
    isAlertOnError: bpy.props.BoolProperty(name="Alert on error", default=False)
    decorText: bpy.props.StringProperty(name="Decor Text", default="")
    decorIcon: bpy.props.StringProperty(name="Icon", default='NONE', update=Utils.UpdateDecorIcon)
    decorHeight: bpy.props.FloatProperty(name="Decor Height", default=0.0, min=0.0, max=4.0)
    del fit
    def GetTextAssert(self):
        if self.isTb:
            if self.tbPoi:
                return self.tbPoi.as_string()
            else:
                return ""
        else:
            return self.txtAssert
    def InitNode(self, _context):
        self.method = 'EXEC'
        self.txtAssert = "result = True"
        self.decorHeight = 0.17
        self.alertColor = (1.0, 1.0, 1.0, 1.0)
    def Assert(self):
        if not self.mute:
            tpc = time.perf_counter()
            if tpc-dict_naNdLastRunTime.get(self, 0.0)>self.speedLimit:
                try:
                    isAsExec = self.method=='EXEC'
                    if not( (self.isCaching)and(dict_naNdCompileCache.get(self)) ):
                        dict_naNdCompileCache[self] = compile(self.GetTextAssert(), "", 'exec') if isAsExec else compile("True" if (False)and(self.isTb)and(not self.tbPoi) else self.GetTextAssert(), "", 'eval')
                    dict_globals = {'bpy':bpy, 'C':bpy.context, 'D':bpy.data, 'opa':opa, 'utils':utils, 'self':self}
                    if isAsExec:
                        exec(dict_naNdCompileCache[self], dict_globals, dict_globals)
                        if 'result' in dict_globals:
                            result = dict_globals['result']
                        else:
                            self.ProcAlertState(self.isAlertOnError)
                            Utils.dict_mngNdErrorEss[self] = ('INFO', "The execution should create the `result` variable.")
                            result = self.isAlertOnError
                            dict_naNdLastRunTime[self] = 0.0
                            return result
                    else:
                        result = eval(dict_naNdCompileCache[self], dict_globals, {})
                    self.ProcAlertState(not result)
                    Utils.dict_mngNdErrorEss[self] = ()
                    dict_naNdLastRunTime[self] = tpc #Не знаю, как по правильному, перед оценкой или после.
                except Exception as ex:
                    self.ProcAlertState(self.isAlertOnError)
                    print (f"Error in {self.__mng_repr__()}: {ex}") #Когда сообщение об ошибке слишком длинное и не влезает в нод -- дополнительно отправить в консоль.
                    Utils.dict_mngNdErrorEss[self] = ('ERROR', str(ex))
                    result = self.isAlertOnError
                    dict_naNdLastRunTime[self] = 0.0
                return result
        return None
    def DrawLabel(self):
        self.Assert()
        if self.isAlwaysWorks:
            if key:=Utils.DgProcAddSelfInDictSpec(self, dict_naNdIsAlwaysWorks):
                bpy.app.timers.register(functools.partial(NaTimerNdWorkingAlways, key))
        return ( self.decorText if self.isLyReadOnly else ( (self.tbPoi.name if self.tbPoi else "" ) if self.isTb else self.txtAssert ) ) if self.hide else ""
    def LyDrawExtNode(self, _context, colLy, _prefs):
        colList = colLy.column(align=True)
        colList.row().prop(self,'method', expand=True) #colList.prop(self,'method')
        colList.prop(self,'isTb')
        colList.prop(self,'speedLimit')
        colList.prop(self,'isCaching')
        colList.prop(self,'isAlwaysWorks')
        colList.prop(self,'isLyReadOnly')
        colList.prop(self,'isAlertOnError')
        row = colList.row()
        LyNiceColorProp(row, self,'decorText')
        row.active = self.isLyReadOnly
        LyNiceColorProp(colList, self,'decorIcon')
        colList.prop(self,'width', text="Node Width", slider=True)
        colList.row().prop(self,'decorHeight', slider=True)
    def LyDrawNode(self, _context, colLy, _prefs):
        #Туда:
        if self.decorHeight:
            row = colLy.row()
            row.label()
            row.scale_y = self.decorHeight
        fac = max((self.width/140.0-1.0)/2.0, 0.05) #Из-за fac==0.0 не центрируется и прилипает.
        rowMain = colLy.row(align=True)
        if fac:
            row = rowMain.row(align=True)
            row.alignment = 'CENTER'
            row.label()
            row.scale_x = fac
        #Приехали
        if self.decorIcon not in Utils.set_allIcons:
            Utils.LyInvalidDecorIcon(rowMain, self)
        else:
            if self.isLyReadOnly:
                box = rowMain.box()
                box.scale_y = 0.5
                rowLabel = box.row()
                rowLabel.alignment = 'CENTER'
                rowLabel.label(text=self.decorText if self.decorText else ((self.tbPoi.name if self.tbPoi else "" ) if self.isTb else self.txtAssert ), icon=self.decorIcon)
            else:
                if self.isTb:
                    rowMain.prop(self,'tbPoi', text="", icon=self.decorIcon if self.decorIcon!='NONE' else 'TEXT')
                else:
                    rowMain.prop(self,'txtAssert', text="", icon=self.decorIcon if self.decorIcon!='NONE' else 'SCRIPT')
        #Обратно:
        if fac:
            row = rowMain.row(align=True)
            row.alignment = 'CENTER'
            row.label()
            row.scale_x = fac
        if self.decorHeight:
            row = colLy.row()
            row.label()
            row.scale_y = self.decorHeight
        #Показ ошибки
        if tup_err:=Utils.dict_mngNdErrorEss.get(self):
            colLy.label(text=tup_err[1], icon=tup_err[0])

Wh.Lc(*globals().values())