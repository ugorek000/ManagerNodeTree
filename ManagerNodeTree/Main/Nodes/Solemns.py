import bpy
from .Bases import ManagerNodeAlertness

from ...uu_ly import LyNiceColorProp
from ..Utils import dict_mngNdErrorEss
from .Bases import dict_mngNdColInacDurBlk

from ... import opa as opa
from ..Utils import GlobalsUtilsInUserExec as utils

def NsUpdateSolemn(self, _context):
    try:
        exec(self.txtExecOnUpdate, {'bpy':bpy, 'C':bpy.context, 'D':bpy.data, 'opa':opa, 'utils':utils, 'self':self, 'val':self.value}, {})
        dict_mngNdErrorEss[self] = ""
    except Exception as ex:
        print (f"Error in {self.__mng_repr__()}: {ex}") #См. тоже самое в NodeAssertor.
        dict_mngNdErrorEss[self] = str(ex)

class ManagerNodeSolemn(ManagerNodeAlertness):
    nclass = 8
    bl_icon = 'SOLO_OFF' #SOLO_OFF  BRUSH_DATA
    bl_width_max = 1024
    bl_width_min = 64
    bl_width_default = 256.1415926536 #Потому что я так захотел; для "щепотки эстетики".
    possibleDangerousGradation = 2
    mngCategory = "3Solemn", 0
    pathHlFromTheme = ''
    txtEvalAlertState = compile("False", "", 'eval')
    txtCeremonial: bpy.props.StringProperty(name="Solemn Text", default="Ceremonial")
    txtExecOnUpdate: bpy.props.StringProperty(name="Exec On Update", default="", description="{'bpy':bpy, 'C':bpy.context, 'D':bpy.data, 'opa':opa, 'utils':utils, 'self':self, 'val':getattr(self, self.txtPropSelfSolemn)}")
    value = property(lambda s: getattr(s, s.txtPropSelfSolemn), lambda s, v: setattr(s, s.txtPropSelfSolemn, v))
    def InitNodePreChain(self, _context):
        ManagerNodeAlertness.InitNodePreChain(self, _context)
        self.txtExecOnUpdate = "#log = print; log(val)"
    def LyDrawExtNodePreChain(self, _context, colLy, _prefs):
        ManagerNodeAlertness.LyDrawExtNodePreChain(self, _context, colLy, _prefs)
        LyNiceColorProp(colLy, self,'txtCeremonial', align=True)
        colLy.prop(self,'txtExecOnUpdate', text="", icon='SCRIPT')
    def LyDrawNodePreChain(self, context, colLy, _prefs):
        def GetColFromTheme():
            list_atts = self.pathHlFromTheme.split(".")
            return getattr(getattr(context.preferences.themes[0].user_interface, list_atts[0]), list_atts[1])
        #Из-за CtrlZ'ов и запуска .blend приходится вызывать ProcAlertState в рисовании, а не в событиях изменения их txtPropSelfSolemn.
        if (self.alertColor[3])and(alert:=eval(self.txtEvalAlertState, {'self':self}, {})):
            if self.pathHlFromTheme: #Устанавливать цвет для погаснувшего мигающего алерта из pathHlFromTheme.
                colFromTheme = GetColFromTheme()
                key = self.__mng_repr__()
                val = colFromTheme[:3] if (self.isHlFromTheme)and(self.value) else None
                tgl = (key in dict_mngNdColInacDurBlk)and(dict_mngNdColInacDurBlk[key]!=val) #Для переключений isHlFromTheme во время погаснувшего мигающего алерта.
                dict_mngNdColInacDurBlk[key] = val
                if tgl: #MngProcBlinkingAlert использует dict_mngNdColInacDurBlk, поэтому тут такая топология с tgl.
                    MngProcBlinkingAlert(self, anyway=True)
            self.ProcAlertState(alert)
        elif self.pathHlFromTheme:
            self.ProcAlertState((self.isHlFromTheme)and(self.value), colToAlert=GetColFromTheme())
        else:
            self.ProcAlertState(False)
    def LyDrawNodePostChain(self, _context, colLy, _prefs):
        ManagerNodeAlertness.LyDrawNodePostChain(self, _context, colLy, _prefs)
        if txt:=dict_mngNdErrorEss.get(self, ""):
            colLy.label(text=txt, icon='ERROR')

def NsbUpdateDecor(self, _context):
    if not(self.isHlFromTheme or self.decorVars):
        self['decorVars'] = 1
class NodeSolemnBool(ManagerNodeSolemn):
    bl_idname = 'MngNodeSolemnBool'
    bl_label = "Solemn Bool"
    pathHlFromTheme = 'wcol_option.inner_sel'
    txtEvalAlertState = compile("self.bool^(not self.alerting)", "", 'eval')
    txtPropSelfSolemn = 'bool'
    bool: bpy.props.BoolProperty(name="Bool", default=False, update=NsUpdateSolemn)
    alerting: bpy.props.BoolProperty(name="Alert trigger", default=True)
    isHlFromTheme: bpy.props.BoolProperty(name="Highlighting from theme", default=True, update=NsbUpdateDecor)
    decorVars: bpy.props.IntProperty(name="Decor", default=1, min=0, max=3, update=NsbUpdateDecor)
    decorIcon0: bpy.props.StringProperty(name="Icon for False", default="CHECKBOX_HLT")
    decorIcon1: bpy.props.StringProperty(name="Icon for True", default="CHECKBOX_DEHLT")
    def InitNode(self, _context):
        self.bool = True
    def LyDrawExtNode(self, _context, colLy, prefs):
        colLy.prop(self,'alerting')
        colLy.prop(self,'isHlFromTheme')
        colLy.prop(self,'decorVars') #.row().prop_inac(self,'decorVars', active=(self.isHlFromTheme)or(self.decorVars))
        LyNiceColorProp(colLy, self,'decorIcon0', align=True)
        LyNiceColorProp(colLy, self,'decorIcon1', align=True)
    def LyDrawNode(self, _context, colLy, prefs):
        suDecorVars = self.decorVars
        suTxtCeremonial = self.txtCeremonial
        colLy.prop(self,'bool', text=" " if ((suDecorVars>>1)%2)and(not suTxtCeremonial)and(not (suDecorVars>>2)) else suTxtCeremonial, icon=(self.decorIcon0 if self.bool else self.decorIcon1) if (suDecorVars>>1)%2 else 'NONE', emboss=suDecorVars%2)

class NodeSolemnFactor(ManagerNodeSolemn):
    bl_idname = 'MngNodeSolemnFactor'
    bl_label = "Solemn Factor"
    pathHlFromTheme = 'wcol_numslider.item'
    txtEvalAlertState = compile("not( (self.factor==0.0)and(self.alerting<1)or(self.factor==1.0)and(self.alerting>-1) )", "", 'eval')
    txtPropSelfSolemn = 'factor'
    factor: bpy.props.FloatProperty(name="Factor", default=0.0, min=0, max=1, subtype='FACTOR', update=NsUpdateSolemn)
    alerting: bpy.props.IntProperty(name="Alert trigger", default=0, min=-1, max=1)
    isHlFromTheme: bpy.props.BoolProperty(name="Highlighting from theme", default=True)
    def InitNode(self, _context):
        self.factor = 0.5
    def LyDrawExtNode(self, _context, colLy, prefs):
        colLy.prop(self,'alerting')
        colLy.prop(self,'isHlFromTheme')
    def LyDrawNode(self, _context, colLy, prefs):
        colLy.prop(self,'factor', text=self.txtCeremonial)

class NodeSolemnInteger(ManagerNodeSolemn):
    bl_idname = 'MngNodeSolemnInteger'
    bl_label = "Solemn Integer"
    txtEvalAlertState = compile("self.integer", "", 'eval')
    txtPropSelfSolemn = 'integer'
    integer: bpy.props.IntProperty(name="Integer", default=0, update=NsUpdateSolemn)
    def LyDrawNode(self, _context, colLy, prefs):
        colLy.prop(self,'integer', text=self.txtCeremonial)

class NodeSolemnFloat(ManagerNodeSolemn):
    bl_idname = 'MngNodeSolemnFloat'
    bl_label = "Solemn Float"
    txtEvalAlertState = compile("self.float", "", 'eval')
    txtPropSelfSolemn = 'float'
    float: bpy.props.FloatProperty(name="Float", default=0.0, step=10, update=NsUpdateSolemn)
    def LyDrawNode(self, _context, colLy, prefs):
        colLy.prop(self,'float', text=self.txtCeremonial)

class NodeSolemnColor(ManagerNodeSolemn):
    bl_idname = 'MngNodeSolemnColor'
    bl_label = "Solemn Color"
    txtEvalAlertState = compile("any(self.colour)", "", 'eval')
    txtPropSelfSolemn = 'colour'
    colour: bpy.props.FloatVectorProperty(name="Color", size=4, min=0.0, max=1.0, subtype='COLOR_GAMMA', update=NsUpdateSolemn) #Как ловко я выкрутился от конфликта api, но с сохранением эстетики.
    decorVars: bpy.props.IntProperty(name="Decor", default=2, min=0, max=2)
    def InitNode(self, context):
        self.colour = context.preferences.themes[0].user_interface.wcol_numslider.item
        self.alertColor = self.colour
    def LyDrawExtNode(self, _context, colLy, prefs):
        colLy.prop(self,'decorVars')
    def LyDrawNode(self, _context, colLy, prefs):
        if not self.txtCeremonial:
            colLy.prop(self,'colour', text="")
        else:
            suDecorVars = self.decorVars
            if not suDecorVars:
                colLy.prop(self,'colour', text=self.txtCeremonial)
            elif suDecorVars==1:
                colLy.row(align=True).prop(self,'colour', text=self.txtCeremonial)
            else:
                LyNiceColorProp(colLy, self,'colour', text=self.txtCeremonial)

class NodeSolemnLayout(ManagerNodeSolemn):
    bl_idname = 'MngNodeSolemnLayout'
    bl_label = "Solemn Layout"
    txtPropSelfSolemn = 'txtExec'
    fit = "{'bpy':bpy, 'C':bpy.context, 'D':bpy.data, 'opa':opa, 'utils':utils, 'self':self, 'ly':colLy}"
    txtExec: bpy.props.StringProperty(name="Text Exec", update=NsUpdateSolemn, description=fit) #update для txtPropSelfSolemn в 'val':getattr для exec в NsUpdateSolemn().
    isShowOnlyLayout: bpy.props.BoolProperty(name="Layout display only", default=False)
    del fit
    def InitNode(self, _context):
        self.txtExec = "ly.row().prop(C.scene.render,'engine', expand=True)"
    def LyDrawExtNode(self, _context, colLy, prefs):
        colLy.prop(self,'isShowOnlyLayout')
    def LyDrawNode(self, _context, colLy, prefs):
        if not self.isShowOnlyLayout:
            colLy.prop(self,'txtExec', text="", icon='SCRIPT')
        try:
            exec(self.txtExec, {'bpy':bpy, 'C':bpy.context, 'D':bpy.data, 'opa':opa, 'utils':utils, 'self':self, 'ly':colLy}, {})
        except Exception as ex:
            print (f"Error in {self.__mng_repr__()}: {ex}")
            colLy.label(text=str(ex), icon='ERROR')

dict_nspCompileCache = {}
def NspPollPointer(self, poi):
    suTxt = self.txtEvalPoll
    if suTxt not in dict_nspCompileCache:
        dict_nspCompileCache[suTxt] = compile(suTxt, "", 'eval')
    return eval(dict_nspCompileCache[suTxt], {'bpy':bpy, 'C':bpy.context, 'D':bpy.data, 'opa':opa, 'utils':utils, 'self':self, 'poi':poi}, {}) if self.txtEvalPoll else True
class NodeSolemnPointer(ManagerNodeSolemn): #Свершилось. То, о чём я мечтал очень давно. Не супер-идеально конечно же, но оно уже пригодно для производства; не то что мой предыдущий кринж.
    bl_idname = 'MngNodeSolemnPointer'
    bl_label = "Solemn Pointer"
    txtPropSelfSolemn = 'pointer'
    for li in bpy.types.ID.__subclasses__():
        getattr(bpy.types, str(li).split("types.")[1].split("'>")[0]) #https://projects.blender.org/blender/blender/issues/127127
    tup_itemsAvailableTypes = tuple((li.bl_rna.identifier, li.bl_rna.name, li.bl_rna.description) for li in bpy.types.ID.__subclasses__())
    typePoi: bpy.props.EnumProperty(name="Pointer Type", default=tup_itemsAvailableTypes[0][0], items=tup_itemsAvailableTypes)
    for dnf, name, descr in tup_itemsAvailableTypes:
        exec(f"pointer{dnf}: bpy.props.PointerProperty(name=\"Pointer to {name}\", type=bpy.types.{dnf}, description=\"{descr}\", poll=NspPollPointer, update=NsUpdateSolemn)")
    pointer = property(lambda s: getattr(s, 'pointer'+s.typePoi), lambda s, v: setattr(s, 'pointer'+s.typePoi, v)) #Заметка: value в ManagerNodeSolemn.
    txtEvalPoll: bpy.props.StringProperty(name="Poll function", default="", description="{'bpy':bpy, 'C':bpy.context, 'D':bpy.data, 'opa':opa, 'utils':utils, 'self':self, 'poi':poi}")
    decorTypeToNode: bpy.props.BoolProperty(name="Decor Type to node", default=False)
    def InitNode(self, _context):
        self.typePoi = 'Object'
        self.txtEvalPoll = "True #Poll function"
        self.decorTypeToNode = True
    def LyDrawExtNode(self, _context, colLy, prefs):
        row = colLy.row(align=True)
        colLy.prop(self,'txtEvalPoll', text="", icon='SCRIPT')
        colLy.prop(self,'typePoi', text="")
        colLy.prop(self,'decorTypeToNode')
    def LyDrawNode(self, _context, colLy, prefs):
        if self.decorTypeToNode:
            colLy.prop(self,'typePoi', text="")
        colLy.prop(self,'pointer'+self.typePoi, text="")

Wh.Lc(*globals().values())