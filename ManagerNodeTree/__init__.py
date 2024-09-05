bl_info = {'name':"ManagerNodeTree", 'author':"ugorek",
           'version':(2,4,0), 'blender':(4,2,1), 'created':"2024.09.05",
           'description':"Nodes for special high level managenment",
           'location':"NodeTreeEditor > N Panel > Mng",
           'warning':"!",
           'category':"System",
           'tracker_url':"https://github.com/ugorek000/ManagerNodeTree/issues", 'wiki_url':"https://github.com/ugorek000/ManagerNodeTree/wiki"}
#№№ as package

from builtins import len as length
import bpy, re
import math, mathutils

if __name__!="__main__":
    import sys
    assert __file__.endswith("__init__.py")
    sys.path.append(__file__[:-11])

import opa
import uu_ly

#import nodeitems_utils
import functools
import time
from random import random as Random
PrintToConsole = print


class AddonPrefs(bpy.types.AddonPreferences):
    bl_idname = bl_info['name'] if __name__=="__main__" else __name__
txt_regResetToDefault = ""

if True: #Для защиты от всяких `bpy.types.Node.__repr__ = lambda a: f"||{a.name}||"`, (которые я использовал в своём RANTO для дебага например)
    bpy.types.Node.__mng_repr__ = lambda nd: f"{nd.id_data.__repr__()}.nodes[\"{nd.name}\"]" #Но всё равно пришлось делать вручную, ибо повторные активации аддона.
    bpy.types.Node.__mng_repr__.__doc__ = f"Backup from {AddonPrefs.bl_idname} addon."
else:
    bpy.types.Node.__mng_repr__ = bpy.types.Node.__repr__
    #В этом случае Node.__repr__ не имеет .__code__, так что не получится 'import types; types.FunctionType(bpy.types.Node.__repr__.__code__, ...)', чтобы изменить __doc__ у копии.

class TryAndPass():
    def __enter__(self):
        pass
    def __exit__(self, *_):
        return True

class OpSimpleExec(bpy.types.Operator): #Бомбезно-гениально-удобно!
    bl_idname = 'mng.simple_exec'
    bl_label = "OpSimpleExec"
    bl_options = {'UNDO'}
    exc: bpy.props.StringProperty(name="Exec", default="")
    def invoke(self, context, event):
        exec(self.exc, {'bpy':bpy, 'event':event}, {})
        return {'FINISHED'}

dict_mngNdErrorEss = {}

set_allIcons = set(bpy.types.UILayout.bl_rna.functions['prop'].parameters['icon'].enum_items.keys())


def RandomColor(alpha=1.0):
    return (Random(), Random(), Random(), alpha)

def ClsNodeIsRegistered(cls):
    #return cls.bl_rna.identifier==cls.bl_idname #https://projects.blender.org/blender/blender/issues/127165
    return True #Нужно придумать/найти, как проверить класс на зарегистрированность.


def DgConvertReprNdAsDoubleGet(reprNd):
    list_spl = reprNd.split("]")
    return (list_spl[0].replace("[", ".get(")+", None)", list_spl[0]+"]"+list_spl[1].replace("[", ".get(")+", None)")
def DgProcAddSelfInDictSpec(nd, dict_doubleGet):
    key = nd.__mng_repr__() #Простой ключ-repr-без-изменений, чтобы сэкономить ещё чутка производительности от строковых замен в DgConvertReprNdAsDoubleGet.
    if key not in dict_doubleGet:
        dict_doubleGet[key] = DgConvertReprNdAsDoubleGet(key)
        return key
def DgCollectEvalDoubleGetFromDict(dict_doubleGet):
    list_result = []
    tgl = True
    while tgl:
        tgl = False
        for dk, (reprGetTree, reprTreeGetNd) in dict_doubleGet.items():
            if (not eval(reprGetTree))or(not(ndRepr:=eval(reprTreeGetNd))):
                #Для переименований нода, CtrlZ'ов, и прочих неожиданностей.
                del dict_doubleGet[dk]
                tgl = True
                list_result.clear()
                break
            list_result.append((dk, ndRepr))
    return list_result


class ConvNclassTagNameId:
    dict_сonvertTagName = {0:"INPUT",    1:"OUTPUT",   2:"none",     3:"OP_COLOR", 4:"OP_VECTOR",  5:"OP_FILTER", 6:"GROUP",     8:"CONVERTER",  9:"MATTE",
                           10:"DISTORT", 12:"PATTERN", 13:"TEXTURE", 32:"SCRIPT",  33:"INTERFACE", 40:"SHADER",   41:"GEOMETRY", 42:"ATTRIBUTE", 100:"LAYOUT"}
    dict_сonvertIdToTag = dict(( (cyc, dk) for cyc, dk in enumerate(dict_сonvertTagName.keys()) ))
    dict_сonvertTagToId = dict(( (dv, dk) for dk, dv in dict_сonvertIdToTag.items() ))
    tup_сonvertTagName = tuple(dict_сonvertTagName.items())
    #for dk, dv in tuple(dict_сonvertTagName.items()):
    #    dict_сonvertTagName[dv] = dk
    del dict_сonvertTagName


def MngUpdateDecorIcon(self, _context):
    if not self.decorIcon:
        self['decorIcon'] = self.bl_rna.properties['decorIcon'].default
    self['decorIcon'] = self.decorIcon.replace(" ", "") #Замена нужна, чтобы красное поле ввода отображало placeholder, а не тупо какой-то прямоугольник вытянутый сплошного цвета.
def LyInvalidDecorIcon(where, self):
    row0 = where.row(align=True)
    row1 = row0.row(align=True)
    row1.label(text="", icon='ERROR')
    row1.alert = True
    row1.alignment = 'LEFT'
    row1.prop(self,'decorIcon', text="", placeholder="Icon")
    row0.alert = True
    row0.alignment = 'CENTER'
    row0.label(text="..."*100) #Если нод адски широкий и пользователь где-то посередине, то чтобы не было ощущения, что макет просто исчез.


class PgNodeCollectionItemWithGetNdSelf(bpy.types.PropertyGroup):
    def GetSelfNode(self, blidTarget, attColl): #Жаль, что реализация не предоставляет доступа к владельцу.
        for nd in self.id_data.nodes:
            if nd.bl_idname==blidTarget:
                for ln in getattr(nd, attColl):
                    if ln==self:
                        return nd
        assert False

class ManagerTree(bpy.types.NodeTree):
    bl_idname = 'ManagerNodeTree'
    bl_label = "Manager Node Tree"
    bl_icon = 'FILE_BLEND'
ManagerTree.__doc__ = bl_info['description']

class ManagerNodeFiller:
    def InitNodePreChain(self,context):pass
    def InitNode(self,context):pass
    def DrawLabelPreChain(self):return ""
    def DrawLabel(self):return ""
    def LyDrawExtNodePreChain(self,context,colLy,prefs):pass
    def LyDrawExtNode(self,context,colLy,prefs):pass
    def LyDrawNodePreChain(self,context,colLy,prefs):pass
    def LyDrawNode(self,context,colLy,prefs):pass
    def LyDrawNodePostChain(self,context,colLy,prefs):pass
class ManagerNodeRoot(bpy.types.Node, ManagerNodeFiller):
    nclass = 0
    isNotSetupNclass = True
    possibleDangerousGradation = 0 #0--безопасный  1--возможно опасный  2--имеет Exec или Eval
    @classmethod
    def poll(cls, tree):
        return True
    def init(self, context):
        if (self.possibleDangerousGradation)and(not Prefs().isDisclaimerAcceptance):
            return ""
        if context is None:
            context = bpy.context
        self.InitNodePreChain(context)
        self.InitNode(context)
    def draw_label(self):
        if self.isNotSetupNclass:
            opa.BNode(self).typeinfo.contents.nclass = self.nclass
            self.__class__.isNotSetupNclass = False
        if (self.possibleDangerousGradation)and(not Prefs().isDisclaimerAcceptance): #Тоже важно вместе с двумя другими ниже, ибо NodeAssertor.
            return ""
        return self.DrawLabelPreChain() or self.DrawLabel() #"or" без нужды, DrawLabelPreChain слишком редкий.
    def draw_buttons_ext(self, context, layout):
        colLy = layout.column()
        prefs = Prefs()
        if (self.possibleDangerousGradation)and(not prefs.isDisclaimerAcceptance): #Суета с дерегистрациями оказалось лажей -- всё крашится. Поэтому так; до лучших времён.
            return
        self.LyDrawExtNodePreChain(context, colLy, prefs)
        self.LyDrawExtNode(context, colLy, prefs)
    def draw_buttons(self, context, layout):
        self.draw_label() #Для перерегистраций и других неизвестных "тонких" моментов.
        colLy = layout.column()
        prefs = Prefs()
        if (self.possibleDangerousGradation)and(not prefs.isDisclaimerAcceptance):
            return
        self.LyDrawNodePreChain(context, colLy, prefs)
        self.LyDrawNode(context, colLy, prefs)
        self.LyDrawNodePostChain(context, colLy, prefs)
    #def register():
    #    if isNotFirstAddonRegistration:
    #        bpy.ops.wm.redraw_timer(type='DRAW_WIN', iterations=0)
    def unregister():
        assert isUnregistrationInProgress
        #Жаль здесь нет ссылки на себя.
        for cls in set_mngNodeClasses:
            cls.isNotSetupNclass = True

#Флаг ^15 -- nd.use_custom_color
#Флаг ^20 -- lastAlertState; см. в BNdToggleSetCol(col=None).
#Флаг ^21 -- isNowBlinkingAlert; А так же активация при запуске .blend.
#Флаг ^22 -- stateBlinkingAlert; Экономить перерисовки.
flagsUcsLas = 32768 | 1048576 #1<<15 | 1<<20
def BNdToggleSetCol(bNd, col=None):
    if col is None:
        if bNd.flag&1048576: #1<<20 #Нужно, чтобы при неактивном алерте можно было изменить цвет самого нода при постоянном вызове ProcAlertState. Бесполезно, ибо при активации алерта перезапишется, но всё ради эстетики.
            bNd.flag &= ~flagsUcsLas
    else:
        bNd.flag |= flagsUcsLas
        bNd.color = col #Выкуси, предупреждение "нельзя писать в рисовании", чтоб тебя.

dict_mngNdBlinkingAlertState = {}
dict_mngNdTimeStartBlinkingAlert = {}
dict_mngNdColInacDurBlk = {}

def MngDoBlinkingAlert(tns, nd, bNd, *, colInacBlk=None, anyway=False):
    def Rainbow(x, ofs, mul2):
        return max(min(2.0-abs((x+ofs)%6.0-2.0),1.0),0.0)*(1.0 if mul2==2.0 else max(mul2,1.0)%1.0)
    num = int(2_000_000_000-1_750_000_000*(1.0 if nd.alertColor[3]==2.0 else nd.alertColor[3]%1.0))
    col = nd.alertColor[:3]
    if max(col)>1.0:
        fac = (tns/num%3.0)*2.0
        BNdToggleSetCol(bNd, (Rainbow(fac, +2, col[0]), Rainbow(fac, 0, col[1]), Rainbow(fac, -2, col[2])))
        if not anyway:
            nd.label = nd.label
    else:
        if (tns%num)<(num>>1): #Сравнение с первой половиной, чтобы показывать(менять) цвет сразу при активации.
            if (not bNd.flag&4194304)or(anyway): #1<<22
                bNd.flag |= 4194304 #1<<22
                BNdToggleSetCol(bNd, col)
                if not anyway: #Топокостыль, anyway==True использует только рисование.
                    nd.label = nd.label #Изменение заголовка почему-то заставляет перерисовываться все деревья во всех окнах.
        else:
            if (bNd.flag&4194304)or(anyway): #1<<22
                bNd.flag &= ~4194304 #1<<22
                BNdToggleSetCol(bNd, colInacBlk)
                if not anyway:
                    nd.label = nd.label
def MngProcBlinkingAlert(nd, tns=None, reprNd=None, *, anyway=False): #Вынесено из-за возможности colInacBlk.
    if tns is None:
        tns = time.perf_counter_ns()
    if reprNd is None:
        reprNd = nd.__mng_repr__()
    bNd = opa.BNode(nd)
    if bNd.flag&2097152: #1<<21 #Явная проверка, чтобы не мигать вечно; но не важна, ибо см. else в DrawLabelPreChain, который выключает мигание.
        MngDoBlinkingAlert(tns-dict_mngNdTimeStartBlinkingAlert[reprNd], nd, bNd, colInacBlk=dict_mngNdColInacDurBlk.get(reprNd, None), anyway=anyway)
def MngTimerBlinkingAlert():
    tns = time.perf_counter_ns()
    for dk, nd in DgCollectEvalDoubleGetFromDict(dict_mngNdBlinkingAlertState):
        MngProcBlinkingAlert(nd, tns, dk)
    return 0.05 if dict_mngNdBlinkingAlertState else None

def MnaUpdateAlertColor(self, _context):
    self['alertColor'] = self.alertColor[:3]+(0.0 if self.alertColor[3]<0.5 else max(1.0, min(self.alertColor[3], 2.0)),)
class ManagerNodeAlertness(ManagerNodeRoot):
    alertColor: bpy.props.FloatVectorProperty(name="Alert Color", size=4, min=0.0, max=2.0, subtype='COLOR_GAMMA', update=MnaUpdateAlertColor)
    def DelSelfFromDictBlinking(self):
        key = self.__mng_repr__()
        if key in dict_mngNdBlinkingAlertState:
            del dict_mngNdBlinkingAlertState[key]
    def free(self):
        #Так-то идеально, да, но: удалить нод с мигающим алертом; отменить; повторить -- и free() не вызывается. От чего эта процедура в целом бесполезна.
        self.DelSelfFromDictBlinking()
    def DrawLabelPreChain(self):
        ManagerNodeRoot.DrawLabelPreChain(self)
        #Плакала производительность... Ох уж эти CtrlZ'ы и "нельзя писать в рисовании". Но оно того стоило.
        bNd = opa.BNode(self)
        if bNd.flag&2097152: #1<<21
            if key:=DgProcAddSelfInDictSpec(self, dict_mngNdBlinkingAlertState):
                dict_mngNdTimeStartBlinkingAlert[key] = time.perf_counter_ns()
                if not bpy.app.timers.is_registered(MngTimerBlinkingAlert):
                    bpy.app.timers.register(MngTimerBlinkingAlert)
        else:
            self.DelSelfFromDictBlinking()
    #Заметка: draw_label() не вызывается, если label!="" и нод свёрнут, но вызывается, если развёрнут.
    def LyDrawExtNodePreChain(self, context, colLy, prefs):
        uu_ly.LyNiceColorProp(colLy, self,'alertColor')
    def ProcAlertState(self, ess, colToAlert=None):
        if colToAlert is None:
            colToAlert = self.alertColor
        bNd = opa.BNode(self)
        if (not self.mute)and(not not ess)and(colToAlert[3]):
            if colToAlert[3]>1.0:
                if not(bNd.flag&2097152): #1<<21
                    bNd.flag |= 2097152 #1<<21
                    MngDoBlinkingAlert(0, self, bNd, anyway=True) #Отправляется 0, а не time.perf_counter_ns(), потому что мигания "локальны", см. dict_mngNdTimeStartBlinkingAlert.
                    self.DrawLabelPreChain() #Иначе запуск произойдёт при следующем вызове ManagerNodeAlertness.DrawLabelPreChain(), а нужно сразу.
            else:
                if bNd.flag&2097152: #1<<21
                    bNd.flag &= ~2097152 #1<<21
                    self.DelSelfFromDictBlinking()
                if max(colToAlert[:3])>1.0:
                    colToAlert = RandomColor() #tuple(map(lambda z: z[0] if z[1]==2.0 else z[1]%1.0*z[0], zip(RandomColor(), colToAlert)))
                BNdToggleSetCol(bNd, colToAlert[:3])
        else:
            if bNd.flag&2097152: #1<<21
                bNd.flag &= ~2097152 #1<<21
                self.DelSelfFromDictBlinking()
            BNdToggleSetCol(bNd)

class PresetsAndEx:
    def AddNodeByBlid(tree, meta_cat="1Utility"):
        list_addedNodes = []
        ndNqle = tree.nodes.new(NodeQuickLayoutExec.bl_idname)
        list_addedNodes.append(ndNqle)
        ndNqle.width = 360
        ndNqle.name = "AddNodeByBlid"
        ndNqle.label = "Add node by bl_idname"
        ndNqle.method = 'EXEC'
        ndNqle.decorExec = "Add"
        ndNqle.visibleButtons = 7
        ndNqle.lines.clear()
        ndNqle.lines.add().txtExec = "NodeNote"
        ndNqle.lines[-1].isActive = False
        ndNqle.lines.add().txtExec = "bpy.ops.node.add_node('INVOKE_DEFAULT', type=C.node.lines[0].txtExec.replace(\"#\", \"\"), use_transform=True)"
        ndNqle.count = ndNqle.count
        return list_addedNodes
    def DoubleBigExec(tree, meta_cat="0Preset"):
        list_addedNodes = []
        ndNqle0 = tree.nodes.new(NodeQuickLayoutExec.bl_idname)
        list_addedNodes.append(ndNqle0)
        ndNqle0.width = 415
        ndNqle0.name = "DoubleBigExec0"
        ndNqle0.label = "Speed up aiming for cursor work by large button size."
        ndNqle0.isShowOnlyLayout = True
        ndNqle0.visibleButtons = 1
        ndNqle1 = tree.nodes.new(NodeQuickLayoutExec.bl_idname)
        list_addedNodes.append(ndNqle1)
        ndNqle1.location.y = -140
        ndNqle1.width = 820
        ndNqle1.name = "DoubleBigExec1"
        ndNqle1.label = "Big button's code below"
        ndNqle1.method = 'EXEC'
        ndNqle1.decorExec = ""
        ndNqle1.visibleButtons = 14
        ##
        ndNqle0.lines.clear()
        ndNqle0.lines.add().txtExec = f"ndTar = self.id_data.nodes.get(\"{ndNqle1.name}\")"
        ndNqle0.lines.add().txtExec = "row = ly.row(align=True)"
        ndNqle0.lines.add().txtExec = f"row.operator('{OpSimpleExec.bl_idname}', text=self.lines[-1].txtExec).exc = " "f\"{repr(ndTar)}.ExecuteAll()\""
        ndNqle0.lines.add().txtExec = "row.scale_y = 5.0"
        ndNqle0.lines.add().txtExec = "Big button for anti-missclick"
        ndNqle0.lines[-1].isActive = False
        ndNqle0.count = ndNqle0.count
        ##
        ndNqle1.lines.clear()
        ndNqle1.lines.add().txtExec = "def PopupMessage(self, context):"
        ndNqle1.lines.add().txtExec = "  col = self.layout.column(align=True)"
        ndNqle1.lines.add().txtExec = "  col.label(text=\"The big button works successfully.\", icon='INFO')"
        ndNqle1.lines.add().txtExec = "  for cyc in range(1): col.label(text=\" \"*1)"
        ndNqle1.lines.add().txtExec = f"bpy.context.window_manager.popup_menu(PopupMessage, title=\"{ndNqle0.name}\", icon='NONE')"
        ndNqle1.lines.add().txtExec = "import random; C.node.id_data.nodes[C.node.lines[0].txtExec.split(\"(\\\"\")[-1][:-2]].label = \"Big button's code below: \"+str(random.random())"
        ndNqle1.lines.add().isTb = True
        ndNqle1.count = 7
        return list_addedNodes
    def ThemeRoundness(tree, meta_cat="2Example"):
        list_addedNodes = []
        ndNsf = tree.nodes.new(NodeSolemnFactor.bl_idname)
        list_addedNodes.append(ndNsf)
        ndNsf.name = "ThemeRoundness0"
        ndNsf.isHlFromTheme = False
        ndNqle0 = tree.nodes.new(NodeQuickLayoutExec.bl_idname)
        list_addedNodes.append(ndNqle0)
        ndNqle0.name = "ThemeRoundness1"
        ndNqle0.location.y = -60
        ndNqle0.width = 700
        ndNqle0.method = 'EXEC'
        ndNqle0.visibleButtons = 0
        ndNqle0.decorExec = ""
        ndNqle1 = tree.nodes.new(NodeQuickLayoutExec.bl_idname)
        list_addedNodes.append(ndNqle1)
        ndNqle1.name = "ThemeRoundness2"
        ndNqle1.location = (-100, 20)
        ndNqle1.width = 440
        ndNqle1.method = 'EXEC'
        ndNqle1.isShowOnlyLayout = True
        ndNqle1.decorExec = "Press me to init"
        ndNqle1.visibleButtons = 0
        ndNqle2 = tree.nodes.new(NodeQuickLayoutExec.bl_idname)
        list_addedNodes.append(ndNqle2)
        ndNqle2.name = "ThemeRoundness3"
        ndNqle2.label = "List"
        ndNqle2.location.y = -250
        ndNqle2.width = 230
        ndNqle2.hide = True
        ndNqle2.isShowOnlyLayout = True
        list_addedNodes[0], list_addedNodes[2] = list_addedNodes[2], list_addedNodes[0]
        ##
        ndNsf.txtExecOnUpdate = f"self.id_data.nodes[\"{ndNqle0.name}\"].ExecuteAll()"
        ##
        ndNqle0.lines.clear()
        ndNqle0.lines.add().txtExec = "theme = C.preferences.themes[0].user_interface"
        ndNqle0.lines.add().txtExec = "txtAtts = \"regular  tool  toolbar_item  radio  text  option  toggle  num  numslider  box  menu  pulldown  menu_back  pie_menu  tooltip  menu_item  scroll  progress  list_item  tab\""
        ndNqle0.lines.add().txtExec = f"if ndTar:=C.space_data.edit_tree.nodes.get(\"{ndNsf.name}\"):"
        ndNqle0.lines.add().txtExec = "  val = ndTar.value"
        ndNqle0.lines.add().txtExec = "  for li in txtAtts.split():"
        ndNqle0.lines.add().txtExec = "    setattr(getattr(C.preferences.themes[0].user_interface, \"wcol_\"+li),'roundness', val)"
        ndNqle0.lines.add().txtExec = "  C.preferences.themes[0].user_interface.panel_roundness = val"
        ndNqle0.count = ndNqle0.count
        ##
        ndNqle1.lines.clear()
        ndNqle1.lines.add().txtExec = ndNqle0.lines[0].txtExec
        ndNqle1.lines.add().txtExec = ndNqle0.lines[1].txtExec
        ndNqle1.lines.add().txtExec = ndNqle0.lines[2].txtExec
        ndNqle1.lines.add().txtExec = "  acc = 0.0"
        ndNqle1.lines.add().txtExec = ndNqle0.lines[4].txtExec
        ndNqle1.lines.add().txtExec = "    acc += getattr(getattr(C.preferences.themes[0].user_interface, \"wcol_\"+li),'roundness')"
        ndNqle1.lines.add().txtExec = "  ndTar[ndTar.txtPropSelfSolemn] = acc/len(txtAtts.split())"
        ndNqle1.lines.add().txtExec = "  ndTar.select = False"
        ndNqle1.lines.add().txtExec = "C.node.id_data.nodes.remove(C.node)"
        ndNqle1.lines.add().txtExec = f"self.id_data.nodes[\"{ndNqle0.name}\"].select = False"
        ndNqle1.lines.add().txtExec = f"self.id_data.nodes[\"{ndNqle2.name}\"].select = False"
        ndNqle1.count = ndNqle1.count
        ##
        ndNqle2.lines.clear()
        ndNqle2.lines.add().txtExec = ndNqle0.lines[0].txtExec
        ndNqle2.lines.add().txtExec = ndNqle0.lines[1].txtExec
        ndNqle2.lines.add().txtExec = "colList = ly.column(align=True)"
        fit = ["Regular", "Tool", "Toolbar Item", "Radio Buttons", "Text", "Option", "Toggle", "Number Field", "Value Slider", "Box", "Menu", "Pulldown", "Menu Background", "Pie Menu", "Tooltip", "Menu Item", "Scroll Bar", "Progress Bar", "List Item", "Tab"]
        ndNqle2.lines.add().txtExec = "list_names = [\""+"\", \"".join(fit)+"\"]"
        ndNqle2.lines.add().txtExec = "for cyc, li in enumerate(txtAtts.split()):"
        ndNqle2.lines.add().txtExec = "  colList.prop(getattr(C.preferences.themes[0].user_interface, \"wcol_\"+li),'roundness', text=list_names[cyc])"
        ndNqle2.lines.add().txtExec = "colList.prop(C.preferences.themes[0].user_interface,'panel_roundness')"
        ndNqle2.count = ndNqle2.count
        return list_addedNodes
    def AssertFrameStep(tree, meta_cat="2Example"):
        list_addedNodes = []
        ndNa = tree.nodes.new(NodeAssertor.bl_idname)
        list_addedNodes.append(ndNa)
        ndNa.width = 560
        ndNa.name = "AssertFrameStep"
        ndNa.method = 'EVAL'
        ndNa.txtAssert = "(C.scene.frame_step == 1) and (C.scene.render.resolution_y % 2 == 0)"
        ndNa.decorText = "Frame Step is 1  and  Even Resolution[1]"
        ndNa.alertColor = (0.85, 0.425, 0.0, 1.0)
        return list_addedNodes
    def StatOfTbLines(tree, meta_cat="1Utility"):
        list_addedNodes = []
        ndNqle = tree.nodes.new(NodeQuickLayoutExec.bl_idname)
        list_addedNodes.append(ndNqle)
        ndNqle.width = 310
        ndNqle.name = "StatOfTbLines"
        ndNqle.label = "Statistic of textblock lines"
        ndNqle.isShowOnlyLayout = True
        ndNqle.lines.clear()
        ndNqle.lines.add().txtExec = "colList = ly.column(align=True)"
        ndNqle.lines.add().txtExec = "def LyAddItem(where, *, text):"
        ndNqle.lines.add().txtExec = "  rowItem = where.row(align=True); rowSize = rowItem.row(align=False)"
        ndNqle.lines.add().txtExec = "  box = rowSize.box(); box.scale_y = 0.5; rowNum = box.row()"
        ndNqle.lines.add().txtExec = "  rowNum.ui_units_x = 3.5; rowNum.alignment = 'RIGHT'"
        ndNqle.lines.add().txtExec = "  rowNum.label(text=text); rowNum.active = False"
        ndNqle.lines.add().txtExec = "  return rowItem"
        ndNqle.lines.add().txtExec = "set_ignoreNames = set(self.lines[-1].txtExec.split(\"§\")); list_sucessIgnoredTb = []"
        ndNqle.lines.add().txtExec = "sco = 0"
        ndNqle.lines.add().txtExec = "for tb in sorted(bpy.data.texts, key=lambda a: len(a.lines), reverse=True):"
        ndNqle.lines.add().txtExec = "  if tb.name not in set_ignoreNames:"
        ndNqle.lines.add().txtExec = "    LyAddItem(colList, text=f\" {len(tb.lines)} lines\").prop(tb,'name', text=\"\")#, icon='TEXT')"
        ndNqle.lines.add().txtExec = "    sco += len(tb.lines)"
        ndNqle.lines.add().txtExec = "  else: list_sucessIgnoredTb.append(tb)"
        ndNqle.lines.add().txtExec = "row = LyAddItem(colList, text=f\" {sco} total\")#.row(); row.label(icon='ASSET_MANAGER'); row.active = False"
        ndNqle.lines.add().txtExec = "LyAddItem(colList, text=\"Ignoring\").prop(self.lines[-1],'txtExec', text=\"\")"
        ndNqle.lines.add().txtExec = "for tb in sorted(list_sucessIgnoredTb, key=lambda a: len(a.lines), reverse=True):"
        ndNqle.lines.add().txtExec = "  rowItem = colList.row(align=True); rowLines = rowItem.row(align=False)"
        ndNqle.lines.add().txtExec = "  rowItem.active = False; rowLines.ui_units_x = 4; rowLines.alignment = 'RIGHT'"
        ndNqle.lines.add().txtExec = "  rowLines.label(text=f\" {len(tb.lines)} lines \"); rowItem.separator(); rowItem.label(text=tb.name)"
        ndNqle.lines.add().txtExec = "Log§Log.py§Log.txt§§§§§§§§§§§§§"
        ndNqle.lines[-1].isActive = False
        ndNqle.count = ndNqle.count
        return list_addedNodes
    def RedrawCheck(tree, meta_cat="1Utility"):
        list_addedNodes = []
        ndNqle = tree.nodes.new(NodeQuickLayoutExec.bl_idname)
        list_addedNodes.append(ndNqle)
        ndNqle.name = "RedrawCheck"
        ndNqle.label = "Redraw Check"
        ndNqle.width = 200
        ndNqle.visibleButtons = 0
        ndNqle.lines.clear()
        ndNqle.lines.add().txtExec = "import random; ly.label(text=str(random.random()), icon=\"SEQUENCE_COLOR_0\"+str(random.randint(1, 9)))"
        ndNqle.isShowOnlyLayout = True
        return list_addedNodes
    def NodeFlagViewer(tree, meta_cat="1Utility"):
        list_addedNodes = []
        ndNqle = tree.nodes.new(NodeQuickLayoutExec.bl_idname)
        list_addedNodes.append(ndNqle)
        ndNqle.width = 340
        ndNqle.name = "NodeFlagViewer"
        ndNqle.label = "Node flag viewer"
        ndNqle.isShowOnlyLayout = True
        ndNqle.lines.clear()
        ndNqle.lines.add().txtExec = "if (ndAc:=self.id_data.nodes.active)or(ndAc:=self):"
        ndNqle.lines.add().txtExec = "  def Recr(txt, depth=3):"
        ndNqle.lines.add().txtExec = "    return txt if not depth else Recr(txt[:len(txt)//2], depth-1)+\" \"*depth+Recr(txt[len(txt)//2:], depth-1)"
        ndNqle.lines.add().txtExec = "  def LyLabel(where, *, header, txt):"
        ndNqle.lines.add().txtExec = "    rowMain = where.row(align=True); rowMain.alignment = 'CENTER'; row = rowMain.row(); row.alignment = 'CENTER'"
        ndNqle.lines.add().txtExec = "    row.active = False; row.label(text=header); rowMain.label(text=txt)"
        ndNqle.lines.add().txtExec = "  ly.prop(ndAc,'name', text=\"\", icon='NODE')"
        ndNqle.lines.add().txtExec = "  suFlag = opa.BNode(ndAc).flag"
        ndNqle.lines.add().txtExec = "  LyLabel(ly, header=\"bin\", txt=Recr(bin(suFlag).replace(\"0b\", \"\").rjust(32, \"0\")))"
        ndNqle.lines.add().txtExec = "  LyLabel(ly, header=\"dec\", txt=str(suFlag))"
        ndNqle.count = ndNqle.count
        return list_addedNodes
    def UserAgreement(tree, meta_cat="2Example"):
        list_addedNodes = []
        ndSb = tree.nodes.new(NodeSolemnBool.bl_idname)
        list_addedNodes.append(ndSb)
        ndSb.name = "UserAgreement"
        ndSb.label = "Agreement"
        ndSb.alertColor = (1.0, 0.0, 0.0, 1.75)
        ndSb.txtCeremonial = "Blender the best!"
        ndSb.txtExecOnUpdate = "if self.value==False: print№(\"Oh nooo...\")".replace("№", "")
        ndSb.alerting = False
        ndSb.isHlFromTheme = False
        return list_addedNodes
    def NqleAlerting(tree, meta_cat="2Example"):
        list_addedNodes = []
        ndNqle = tree.nodes.new(NodeQuickLayoutExec.bl_idname)
        list_addedNodes.append(ndNqle)
        ndNqle.name = "NqleAlerting"
        ndNqle.label = "Nqle Alerting Example"
        ndNqle.width = 650
        ndNqle.alertColor = (2.0, 2.0, 2.0, 1.5)
        ndNqle.lines.clear()
        ndNqle.lines.add().txtExec = "curLoc = C.space_data.cursor_location"
        ndNqle.lines.add().txtExec = "if C.region.view2d.view_to_region(curLoc.x, curLoc.y)!=(12000, 12000):"
        ndNqle.lines.add().txtExec = "  isX = (curLoc.x>self.location.x)and(curLoc.x<self.location.x+self.width)"
        ndNqle.lines.add().txtExec = "  scaleUi = C.preferences.system.dpi/72"
        ndNqle.lines.add().txtExec = "  isY = (curLoc.y<self.location.y)and(curLoc.y>self.location.y-self.dimensions.y/scaleUi)" #Огм, у меня без "s" свойство почему-то периодически существует.
        ndNqle.lines.add().txtExec = "  alert = (isX)and(isY)"
        ndNqle.lines.add().txtExec = "#ly.prop(C.preferences.view,'ui_scale')"
        ndNqle.count = ndNqle.count
        return list_addedNodes
    def RedrawAlways(tree, meta_cat="1Utility"):
        list_addedNodes = []
        ndNqle = tree.nodes.new(NodeQuickLayoutExec.bl_idname)
        list_addedNodes.append(ndNqle)
        ndNqle.name = "RedrawAlways"
        ndNqle.label = "Always Redraw"
        ndNqle.width = 160
        ndNqle.isShowOnlyLayout = True
        ndNqle.lines.clear()
        ndNqle.lines.add().txtExec = "import functools"
        ndNqle.lines.add().txtExec = "def TimerRedrawAlways(reprNd):"
        ndNqle.lines.add().txtExec = "  nd = eval(reprNd); nd.label = nd.label"
        ndNqle.lines.add().txtExec = "bpy.app.timers.register(functools.partial(TimerRedrawAlways, self.__mng_repr__()))"
        ndNqle.lines.add().txtExec = "ly.label(text=\"Now all always redrawn\")"
        ndNqle.count = ndNqle.count
        return list_addedNodes
    def NyanCat(tree, meta_cat="2Example"):
        list_addedNodes = []
        ndNqle = tree.nodes.new(NodeQuickLayoutExec.bl_idname)
        list_addedNodes.append(ndNqle)
        ndNqle.name = "NyanCat"
        ndNqle.label = "Gen Node NyanCat"
        ndNqle.method = 'EXEC'
        ndNqle.decorExec = "Add"
        ndNqle.lines.clear()
        ndNqle.lines.add().txtExec = "class NodeNyanCat(bpy.types.Node):"
        ndNqle.lines.add().txtExec = "  bl_idname = 'NodeNyanCat'; bl_label = \"Nyan Cat\""
        ndNqle.lines.add().txtExec = "  bl_width_default = 395; bl_width_max = bl_width_default; bl_width_min = bl_width_default"
        ndNqle.lines.add().txtExec = "  dataNc0 = 59848220393505127239812029565181019984602839718346832464044499915353041225157356464361977225358310398295950169558930459303653980581214246578965855232364045303618309868936117863898944061598245251290541322050362399782530263712462846665086680306385984844721317547232328082294664339353304636083224431426746384205325410746737201238073223361959934871222361260191475321827434483247853704682486781268225712137660174042332408405615962523497863491760529311968684592891149273502406720791414783597035064901331093832"
        ndNqle.lines.add().txtExec = "  dataNc1 = 783920978098536105529342389099202157604459721101978794996878577541581259259886061298589059875915609307637251465055954278792746860301294416975715108462624129065236001377854197692876849264009636081337502837259169350505400882162360809552816205441285740424235973211997040603523419790996525979858410995208894693349020343690454493135767765158595764536833652755450569590045340918151510104890400096412746593179909009624356960412596117297104797644482427842132150970451578091860410011293465668361911680912884434703780168"
        ndNqle.lines.add().txtExec = "  dataNc2 = 1178072778365569050686920271707930615824525933259477222098588426997003586923990053469211099549277786592492034761484948758268394288122267828594010908317240345946730939750734214849029698940495677792650557840472388069558757126685816676725052920228342902995196232730247054879120027026286366683757414718246368012318884848247896053624800129173906504054627176414040253712831394573991016994004569328471877545220125990956606282522405315496153619045564762037102584658851197865085514488144445735487383625976"
        ndNqle.lines.add().txtExec = "  dataNc3 = 441681619054659837831573114026833132635586524360429182107149838046564197844623894563917535925805220215914465976223306640157749123543524623930843093240465266694877521860865792790528287840478307608059941834164801204280759616101765358505484901159087308105601460952927778783362519121084264073429794485010219256518053060350037252767511173712170450078760855138891009109160286526373681413951601436239298430503599769810253426293106101756326520902005017893379952583055108009815204427670972785316654620875842462249738488"
        ndNqle.lines.add().txtExec = "  dataNc4 = 9184997782576515018469869432515341113422019091052109736926224274084577397168653342689848940964242074923755121135038965600951704898397625971560895512188995800595843419055857773845941620984038268597223456627497165839726427356358489512784448745073221760193760067802789208764174316960928470636621583656002397262959529421398652492810461277817330931340328047629221521830820855039349773834143656368253471684076274714567473730482003988173033755144763838298547970805982981368429153774948085253465006328"
        ndNqle.lines.add().txtExec = "  dataNc5 = 661850521198768960657675037194481064075845942779582763479388992010367158526912464920563875288307115137608982586164348338977744979713031665674394171899920478412590108771574789307679747527534329571387697110458122285998358049916654270525780574883222148653266077935123750348126795999283427950273619407902121750507503229819503811301621815432662958991429066585239575170724990432941681252628619232571024872237099217123858955797834824728069416612143498613704792275245183544458623619553003165092710071468982659613024504"
        ndNqle.lines.add().txtExec = "  def draw_label(self):"
        ndNqle.lines.add().txtExec = "    opa.BNode(self).typeinfo.contents.nclass = 33"
        ndNqle.lines.add().txtExec = "    return \"\""
        ndNqle.lines.add().txtExec = "  def draw_buttons(self, context, layout):"
        ndNqle.lines.add().txtExec = "    self.draw_label()"
        ndNqle.lines.add().txtExec = "    colRows = layout.column(align=True); colRows.scale_y = 0.59"
        ndNqle.lines.add().txtExec = "    bNd = opa.BNode(self); inx = bNd.flag>>25; bNd.flag = (bNd.flag&2**25-1)+(((inx+1)%6)<<25)"
        ndNqle.lines.add().txtExec = "    num = getattr(self, f'dataNc{inx}'); sco = 0"
        ndNqle.lines.add().txtExec = "    while num>0:"
        ndNqle.lines.add().txtExec = "      for cyc in range(num%256//8):"
        ndNqle.lines.add().txtExec = "        if (not sco%34)and(sco!=681):"
        ndNqle.lines.add().txtExec = "          rowColimns = colRows.row(align=True); rowColimns.scale_x = 0.79; rowColimns.alignment = 'CENTER'"
        ndNqle.lines.add().txtExec = "        rowColimns.label(icon=['BLANK1', 'SEQUENCE_COLOR_04', 'SEQUENCE_COLOR_09', 'SNAP_FACE', 'SEQUENCE_COLOR_03', 'SEQUENCE_COLOR_07', 'SEQUENCE_COLOR_06', 'SEQUENCE_COLOR_07'][num%8])"
        ndNqle.lines.add().txtExec = "        sco += 1"
        ndNqle.lines.add().txtExec = "      num >>= 8"
        ndNqle.lines.add().txtExec = "bpy.utils.register_class(NodeNyanCat)"
        ndNqle.lines.add().txtExec = "bpy.ops.node.add_node('INVOKE_DEFAULT', type=NodeNyanCat.bl_idname, use_transform=True)"
        ndNqle.count = ndNqle.count
        return list_addedNodes
    def AllPointersFromNsp(tree, meta_cat="2Example"):
        list_addedNodes = []
        ndNqle = tree.nodes.new(NodeQuickLayoutExec.bl_idname)
        list_addedNodes.append(ndNqle)
        ndNqle.name = "ViewAllPointersFromNsp"
        ndNqle.width = 340
        ndNqle.isShowOnlyLayout = True
        ndNqle.lines.clear()
        ndNqle.lines.add().txtExec = "colInfo = ly.column(); colInfo.active = False"
        ndNqle.lines.add().txtExec = "if ndTar:=self.id_data.nodes.active:"
        ndNqle.lines.add().txtExec = "  colInfo.prop(ndTar,'name', text=\"\", icon='NODE')"
        ndNqle.lines.add().txtExec = "  if ndTar.bl_idname=='MngNodeSolemnPointer':"
        ndNqle.lines.add().txtExec = "    colInfo.active = True; colInfo.separator()"
        ndNqle.lines.add().txtExec = "    rowList = ly.row(align=False); colName = rowList.column(align=True)"
        ndNqle.lines.add().txtExec = "    colName.alignment = 'RIGHT'; colProp = rowList.column(align=True)  "
        ndNqle.lines.add().txtExec = "    colName.label(text=\"\"); colProp.prop(ndTar,'typePoi', text=\"\")"
        ndNqle.lines.add().txtExec = "    colName.separator(); colProp.separator()"
        ndNqle.lines.add().txtExec = "    for ti in ndTar.tup_itemsAvailableTypes:"
        ndNqle.lines.add().txtExec = "      colProp.prop(ndTar, 'pointer'+ti[0], text=\"\")"
        ndNqle.lines.add().txtExec = "      if ti[0]==ndTar.typePoi: colName.alert = True"
        ndNqle.lines.add().txtExec = "      colName.label(text=ti[1]); colName.alert = False"
        ndNqle.lines.add().txtExec = "  else: colInfo.label(text=\"Need a \\\"Solemn Pointer\\\" node.\")"
        ndNqle.lines.add().txtExec = "else: colInfo.label(text=\"Active node is None\")"
        ndNqle.count = ndNqle.count
        return list_addedNodes
    def Dummy(tree, meta_ca1t="9Dummy"):
        list_addedNodes = []
        ndAaa = tree.nodes.new(NodeAaa.bl_idname)
        list_addedNodes.append(ndAaa)
        ndAaa.name = "Dummy"
        return list_addedNodes
    dict_catPae = {}
    for dk, dv in dict(locals()).items():
        if (callable(dv))and('meta_cat' in dv.__code__.co_varnames):
            dict_catPae.setdefault(dv.__defaults__[0], []).append(dk) #dv.__code__.co_name
    list_catPae = [(li[0][1:], li[1]) for li in sorted(dict_catPae.items(), key=lambda a: a[0][0])] #list(dict_catPae.items())
    del dict_catPae

class OpPamnPresets(bpy.types.Operator):
    bl_idname = 'mng.pamn_presets'
    bl_label = "OpPamnPresets"
    bl_options = {'UNDO'}
    name: bpy.props.StringProperty(name="Preset Name", default="")
    def invoke(self, context, event):
        def OffsetNodesLocToOrigin(list_nodes, origin):
            for nd in list_nodes:
                bNd = opa.BNode(nd)
                bNd.locx += origin[0]
                bNd.locy += origin[1]
        tree = context.space_data.edit_tree
        bpy.ops.node.select_all(action='DESELECT')
        list_addedNodes = getattr(PresetsAndEx, self.name)(tree)
        bpy.ops.wm.redraw_timer(type='DRAW_WIN', iterations=0) #Нужно для cursor_location ниже.
        OffsetNodesLocToOrigin(list_addedNodes, context.space_data.cursor_location)
        bpy.ops.transform.translate('INVOKE_DEFAULT', view2d_edge_pan=True)
        tree.nodes.active = list_addedNodes[0]
        return {'FINISHED'}

class PanelAddManagerNode(bpy.types.Panel):
    bl_idname = 'MNG_PT_AddManagerNode'
    bl_label = "Add Manager Node"
    bl_space_type = 'NODE_EDITOR'
    bl_region_type = 'UI'
    bl_category = "Mng"
    bl_order = 0
    @classmethod
    def poll(cls, context):
        return not not context.space_data.edit_tree
    @classmethod
    def CreateUnfs(cls, prefs):
        for li in list_catAdds:
            prefs.pamnUnfurils.add().name = li[0]
    @staticmethod
    def PreScan(patr, list_scan, *, LKey=lambda a:a):
        if patr:
            list_found = []
            for li in list_scan:
                if patr.search(LKey(li)):
                    list_found.append(li)
            return list_found
        else:
            return list_scan
    @staticmethod
    def LyCatAddIndUnfAuto(where, name, prefs, *, active=True, anyway=False):
        ciUnf = prefs.pamnUnfurils.get(name)
        if not ciUnf:
            bpy.app.timers.register(functools.partial(PamnTimerAddUnfuril, prefs, name))
            return False
        colRoot = where.column()
        rowCat = colRoot.box().row(align=True)
        rowCat.scale_y = 0.75
        rowUnf = rowCat.row(align=True)
        rowUnf.alignment = 'LEFT'
        tgl = (ciUnf.unf)or(anyway)
        rowUnf.prop(ciUnf,'unf', text=ciUnf.name, icon='DOWNARROW_HLT' if tgl else 'RIGHTARROW', emboss=False)
        rowUnf.active = active
        rowCat.prop(ciUnf,'unf', text=" ", emboss=False)#+True, icon='BLANK1')
        if tgl:
            rowList = colRoot.row(align=True)
            rowList.label(icon='BLANK1')
            colList = rowList.column(align=True)
            return colList
        else:
            return None
    @staticmethod
    def LyAddItem(where, *, text, icon=None):
        rowItem = where.row(align=True)
        rowAdd = rowItem.row(align=True)
        rowAdd.scale_x = 1.75
        rowAdd.ui_units_x = 2.0
        rowLabel = rowItem#.row(align=True)
        rowLabel.alignment = 'LEFT'
        rowLabel.label(text=" "+text)
        if icon:
            rowIcon = rowLabel.row(align=True)
            rowIcon.alignment = 'LEFT'
            rowIcon.label(icon=icon)
        return rowAdd
    def draw(self, context):
        colLy = self.layout.column()
        prefs = Prefs()
        colLy.prop(prefs,'pamnFilter', text="", icon='SORTBYEXT' if prefs.pamnFilter else 'NONE') #Я так захотел и мне так красиво.
        colListCats = colLy.column()
        ndAc = context.space_data.edit_tree.nodes.active
        patr = re.compile(prefs.pamnFilter) if prefs.pamnFilter else None
        suInda = not prefs.isDisclaimerAcceptance
        for li in list_catAdds:
            list_found = PanelAddManagerNode.PreScan(patr, li[1], LKey=lambda a:a.bl_label)
            if suInda:
                list_found = [li for li in list_found if not li.possibleDangerousGradation] #ClsNodeIsRegistered(li)
            if (list_found)and(colListItems:=PanelAddManagerNode.LyCatAddIndUnfAuto(colListCats, li[0], prefs, anyway=not not patr)):
                for cls in list_found:
                    rowOp = PanelAddManagerNode.LyAddItem(colListItems, text=cls.bl_label, icon=getattr(cls,'bl_icon', 'NONE'))
                    fit = f"bpy.ops.node.add_node('INVOKE_DEFAULT', type=\"{cls.bl_idname}\", use_transform=True)"
                    rowOp.operator(OpSimpleExec.bl_idname, text="", icon='TRIA_LEFT', depress=(not not ndAc)and(ndAc.bl_idname==cls.bl_idname)and(ndAc.select)).exc = fit
        if suInda:
            colLy.separator()
            col = colLy.column()
            col.scale_y = 0.6
            col.label(text="Not all nodes are available.")
            col.label(text=" "*2+"Please accept disclaimer.")#, icon='BLANK1')
            col.active = False
def PamnTimerAddUnfuril(prefs, name):
    prefs.pamnUnfurils.add().name = name
class PamnUnfuril(bpy.types.PropertyGroup): #"discl" со своим "sure", "closure", и "dis", слишком не годилось; пришлось заменить на модифицированный "Unfurl". Ещё был вариант из слов "REveal DIsclosuRE".
    unf: bpy.props.BoolProperty(name="Unfurl", default=False)
class AddonPrefs(AddonPrefs):
    pamnFilter: bpy.props.StringProperty(name="Filter", default="")
    pamnUnfurils: bpy.props.CollectionProperty(type=PamnUnfuril)
txt_regResetToDefault += " pamnFilter pamnUnfurils"

class PanelAddManagerNode_SubPresetsAndEx(bpy.types.Panel):
    bl_idname = 'MNG_PT_SubPresetsAndEx'
    bl_label = "Auxiliaries"
    bl_space_type = 'NODE_EDITOR'
    bl_region_type = 'UI'
    bl_parent_id = PanelAddManagerNode.bl_idname
    bl_options = {'DEFAULT_CLOSED'}
    @classmethod
    def poll(cls, context):
        return Prefs().isDisclaimerAcceptance
    @classmethod
    def CreateUnfs(cls, prefs):
        for li in PresetsAndEx.list_catPae:
            prefs.pamnUnfurils.add().name = li[0]
    def draw(self, context):
        colLy = self.layout.column()
        prefs = Prefs()
        colLy.prop(prefs,'pspaeFilter', text="", icon='SORTBYEXT' if prefs.pspaeFilter else 'NONE')
        colListCats = colLy.column()
        patr = re.compile(prefs.pspaeFilter) if prefs.pspaeFilter else None
        for li in PresetsAndEx.list_catPae:
            list_found = PanelAddManagerNode.PreScan(patr, li[1])
            if (list_found)and(colListItems:=PanelAddManagerNode.LyCatAddIndUnfAuto(colListCats, li[0], prefs, anyway=not not patr)):
                for li in list_found:
                    rowOp = PanelAddManagerNode.LyAddItem(colListItems, text=li)
                    rowOp.operator(OpPamnPresets.bl_idname, text="", icon='FRAME_PREV').name = li #BACK  FRAME_PREV  REW  PLAY_REVERSE
class AddonPrefs(AddonPrefs):
    pspaeFilter: bpy.props.StringProperty(name="Filter", default="")
    #Вместо pspaeUnfurils используются pamnUnfurils.
txt_regResetToDefault += " pspaeFilter"


class PanelManagerActiveNode(bpy.types.Panel):
    bl_idname = 'MNG_PT_ManagerActiveNode'
    bl_label = "Manager Active Node"
    bl_space_type = 'NODE_EDITOR'
    bl_region_type = 'UI'
    bl_category = "Mng"
    bl_order = 1
    @classmethod
    def poll(cls, context):
        tree = context.space_data.edit_tree
        return (tree)and(tree.nodes.active)and(tree.nodes.active.__class__ in set_mngNodeClasses)# tree.nodes.active.bl_idname in set_mngNodeBlids
    def draw(self, context):
        colLy = self.layout.column()
        ndAc = context.space_data.edit_tree.nodes.active
        colLy.prop(ndAc,'name', text="", icon='NODE')
        ndAc.draw_buttons_ext(context, colLy)

class ManagerNodeNote(ManagerNodeRoot):
    nclass = 32
    bl_width_max = 2048
    bl_width_default = 256

class NodeSimpleNote(ManagerNodeNote):
    bl_idname = 'NodeNote'
    bl_label = "Simple Note"
    bl_width_min = 64
    mngCategory = "0Text", 0
    body: bpy.props.StringProperty(name="Note body", default="")
    def DrawLabel(self):
        return self.body if self.hide else ""
    def LyDrawExtNode(self, _context, colLy, _prefs):
        uu_ly.LyNiceColorProp(colLy, self,'body') #colLy.prop(self,'body')
    def LyDrawNode(self, _context, colLy, _prefs):
        colLy.prop(self,'body', text="")


class NodeNote(ManagerNodeNote):
    bl_idname = 'MngNodeNote'
    bl_label = "Note"
    bl_width_min = 140
    mngCategory = "0Text", 1
    note: bpy.props.StringProperty(name="Note body", default="")
    isLyReadOnly: bpy.props.BoolProperty(name="Read only", default=False)
    isLyCenter: bpy.props.BoolProperty(name="Center", default=False)
    decorIcon: bpy.props.StringProperty(name="Icon", default='NONE', update=MngUpdateDecorIcon)
    decorIsActive: bpy.props.BoolProperty(name="Active", default=True)
    decorIsAlert: bpy.props.BoolProperty(name="Alert", default=False)
    decorPlaceholder: bpy.props.StringProperty(name="Placeholder", default="Note")
    def InitNode(self, _context):
        self.decorIcon = "OUTLINER_DATA_GP_LAYER"
    def DrawLabel(self):
        return self.note if self.hide else self.bl_label
    def LyDrawExtNode(self, _context, colLy, _prefs):
        uu_ly.LyNiceColorProp(colLy, self,'note', text="Text:", align=True) #colLy.prop(self,'note', text="")
        colLy.prop(self,'isLyReadOnly')
        row = colLy.row()
        row.prop(self,'isLyCenter')
        row.active = self.isLyReadOnly
        colLy.prop(self,'decorIsActive')
        colLy.prop(self,'decorIsAlert')
        uu_ly.LyNiceColorProp(colLy, self,'decorIcon')
        uu_ly.LyNiceColorProp(colLy, self,'decorPlaceholder')
    def LyDrawNode(self, _context, colLy, _prefs):
        if self.decorIcon not in set_allIcons:
            LyInvalidDecorIcon(colLy, self)
            return
        colLy.active = self.decorIsActive
        colLy.alert = self.decorIsAlert
        if self.isLyReadOnly:
            row = colLy.row()
            if self.isLyCenter:
                row.alignment = 'CENTER'
            if self.note:
                row.label(text=self.note, icon=self.decorIcon)
            else:
                row.active = False
                row.label(text=self.decorPlaceholder, icon=self.decorIcon)
        else:
            colLy.prop(self,'note', text="", placeholder=self.decorPlaceholder, icon=self.decorIcon)


def NnpUpdateCount(self, _context):
    len = length(self.lines)
    if self.isAutoCount:
        for cyc in reversed(range(len)):
            if not self.lines[cyc].body:
                self.lines.remove(cyc)
        if not self.isLyReadOnly:
            self.lines.add().name = str(length(self.lines))
    else:
        for cyc in range(len, self.count):
            self.lines.add().name = str(cyc)
        for cyc in reversed(range(self.count, len)):
            if not(self.isProtectErasion and self.lines[cyc].body):
                self.lines.remove(cyc)
    self['count'] = length(self.lines)
    if not self.count:
        self['count'] = 1
        self.lines.add().name = "0"
def NnpUpdateLineBody(self, context):
    ndSelf = self.GetSelfNode(NodeNotepad.bl_idname, 'lines')
    if (not self.body)or(int(self.name)==length(ndSelf.lines)-1):
        NnpUpdateCount(ndSelf, context)
    if False:
        ndSelf.txtBackupLines = "\n".join(ci.body for ci in ndSelf.lines)
class NnpLine(PgNodeCollectionItemWithGetNdSelf):
    body: bpy.props.StringProperty(name="Body", default="", update=NnpUpdateLineBody)
class NodeNotepad(ManagerNodeNote):
    bl_idname = 'MngNodeNotepad'
    bl_label = "Notepad"
    bl_width_min = 140
    mngCategory = "0Text", 2
    lines: bpy.props.CollectionProperty(type=NnpLine)
    #txtBackupLines: bpy.props.StringProperty(default="") #Не используется. Идея была, что если нод сломается, то восстановить через простое свойство будет проще, чем через PropertyGroup.
    isAutoCount: bpy.props.BoolProperty(name="Auto notepad", default=True, update=NnpUpdateCount)
    count: bpy.props.IntProperty(name="Count of lines", default=1, min=0, max=32, soft_min=1, soft_max=12, update=NnpUpdateCount)
    isLyReadOnly: bpy.props.BoolProperty(name="Read only", default=False, update=NnpUpdateCount)
    isProtectErasion: bpy.props.BoolProperty(name="Protect erasion", default=True)
    decorLineAlignment: bpy.props.EnumProperty(name="Lines alignment", default='DOCK', items=( ('FLAT',"Flat",""), ('DOCK',"Docking",""), ('GAP',"Gap","") ))
    decorIncludeNumbering: bpy.props.IntProperty(name="Include numbering", default=2, min=0, max=2)
    decorVars: bpy.props.IntProperty(name="Decor", default=4, min=0, max=15)
    def InitNode(self, _context):
        self.count = 1 #Чтобы затриггерить NnpUpdateCount().
    def LyDrawExtNode(self, _context, colLy, _prefs):
        colList = colLy.column(align=True)
        colList.prop(self,'isAutoCount')
        col = colList.column(align=True)
        col.prop(self,'count')
        col.prop(self,'isProtectErasion')
        col.active = not self.isAutoCount
        colList.prop(self,'isLyReadOnly')
        row = colList.column(align=True)
        uu_ly.LyNiceColorProp(row, self,'decorLineAlignment')
        row.active = (self.count>1)and(not self.isLyReadOnly)
        colList.prop(self,'decorIncludeNumbering')
        colList.prop(self,'decorVars')
    def LyDrawNode(self, _context, colLy, _prefs):
        colLines = colLy.column(align=self.decorLineAlignment!='GAP')
        len = length(str(self.count)) #length(self.lines)
        decorNum = self.decorIncludeNumbering
        txt = ":" if decorNum==2 else ""
        suDecorVars = self.decorVars
        for cyc, ci in enumerate(self.lines):
            rowLine = ( colLines.row() if self.decorLineAlignment=='DOCK' else colLines ).row(align=True)
            if decorNum:
                rowNum = rowLine.row(align=True)
                rowNum.alignment = 'LEFT'
                rowNum.active = suDecorVars%2
                rowNum.alert = (suDecorVars>>1)%2
                rowNum.label(text=str(cyc+1).zfill(len)+txt)
            rowBody = rowLine.row(align=True)
            rowBody.active = (suDecorVars>>2)%2
            rowBody.alert = (suDecorVars>>3)
            if self.isLyReadOnly:
                rowBody.label(text=ci.body)
            else:
                rowBody.prop(ci,'body', text="")

from mathutils import Color

def NscUpdateCol(self, _context):
    self.use_custom_color = not self.isClassicLy
    if self.isGamma:
        self.color = self.colGamm
        self['col'] = self.colGamm
    else:
        self.color = tuple(map(lambda x: x**(1/2.2), self.col))
        self['colGamm'] = self.col
class NodeSimpleColor(ManagerNodeRoot):
    nclass = 33#2
    bl_idname = 'MngNodeSimpleColor'
    bl_label = "Color"
    bl_width_max = 384
    bl_width_min = 64
    bl_width_default = 140
    mngCategory = "1Color", 0
    isGamma: bpy.props.BoolProperty(name="Gamma", default=True, update=NscUpdateCol)
    col: bpy.props.FloatVectorProperty(name="Color", size=3, soft_min=0.0, soft_max=1.0, subtype='COLOR', update=NscUpdateCol)
    colGamm: bpy.props.FloatVectorProperty(name="ColorGamm", size=3, soft_min=0.0, soft_max=1.0, subtype='COLOR_GAMMA', update=NscUpdateCol)
    decorHeight: bpy.props.IntProperty(name="Decor Height", default=3, min=2, max=6)
    isClassicLy: bpy.props.BoolProperty(name="Classic layout", default=False, update=NscUpdateCol)
    def InitNode(self, _context):
        setattr(self, 'colGamm' if self.isGamma else 'col', RandomColor()[:3])
    def LyDrawExtNode(self, _context, colLy, _prefs):
        colList = colLy.column(align=True)
        row = colList.row()
        row.prop(self,'colGamm' if self.isGamma else 'col', text="")
        row.prop(self,'isGamma')
        colList.prop(self,'decorHeight')
        colList.prop(self,'isClassicLy')
    def LyDrawNode(self, _context, colLy, _prefs):
        rowCol = colLy.row()
        rowCol.prop(self,'colGamm' if self.isGamma else 'col', text="", emboss=self.isClassicLy) #emboss==False для color prop -- это потрясающе!!
        rowCol.scale_y = 0.5*self.decorHeight


def NcnUpdateColor(self, _context):
    self.use_custom_color = not self.isClassicLy
    if self.isReadOnly:
        self['col'] = self.col4ProvReadOnly[:3]
        self['colGamm'] = self.col4ProvReadOnly[:3]
        self['colA'] = self.col4ProvReadOnly
        self['colAGamm'] = self.col4ProvReadOnly
    else:
        if self.isAlpha:
            if self.isGamma:
                self.color = self.colAGamm[:3]
                self['colA'] = self.colAGamm
            else:
                self.color = tuple(map(lambda x: x**(1/2.2), self.colA[:3]))
                self['colAGamm'] = self.colA
        else:
            if self.isGamma:
                self.color = self.colGamm
                self['col'] = self.colGamm
            else:
                self.color = tuple(map(lambda x: x**(1/2.2), self.col))
                self['colGamm'] = self.col
    if self.isAlpha:
        tup_rgbaByte = tuple(map(lambda x: int(x*255), self.colA))
        self.soldTxtRgbByte = "R:{} G:{} B:{} A:{}".format(*tup_rgbaByte)
        txtPrec = str(self.precisionLyNums)
        self.soldTxtRgbFloat = "r:{:.&} g:{:.&} b:{:.&} a:{:.&}".replace("&", txtPrec).format(*self.colA).replace("0.", ".").replace("1.0", "1.")
        muv = 3*self.isReverseHex
        txtHex = hex(tup_rgbaByte[abs(muv-3)]+tup_rgbaByte[abs(muv-2)]*256+tup_rgbaByte[abs(muv-1)]*65536+tup_rgbaByte[abs(muv)]*16777216)[2:]
        self.soldTxtHex = f"Hex-{'abgr' if muv else 'rgba'}:"+self.txtHexPrefixReplace+(txtHex.upper() if self.isUpperHex else txtHex)
        tup_hsv = Color(self.colA[:3]).hsv
    else:
        tup_rgbByte = tuple(map(lambda x: int(x*255), self.col))
        self.soldTxtRgbByte = "R:{} G:{} B:{}".format(*tup_rgbByte)
        txtPrec = str(self.precisionLyNums)
        self.soldTxtRgbFloat = "r:{:.&} g:{:.&} b:{:.&}".replace("&", txtPrec).format(*self.col).replace("0.", ".").replace("1.0", "1.")
        muv = 2*self.isReverseHex
        txtHex = hex(tup_rgbByte[abs(muv-2)]+tup_rgbByte[abs(muv-1)]*256+tup_rgbByte[abs(muv)]*65536)[2:]
        self.soldTxtHex = f"Hex-{'bgr' if muv else 'rgb'}:"+self.txtHexPrefixReplace+(txtHex.upper() if self.isUpperHex else txtHex)
        tup_hsv = Color(self.col).hsv
    self.soldTxtHsvNum = "H:{:.&f}° S:{:.&f}% V:{:.&f}%".replace("&", str(int(txtPrec)-2)).format(tup_hsv[0]*360, tup_hsv[1]*100, tup_hsv[2]*100)
    self.soldTxtHsvFloat = "h:{:.&} s:{:.&} v:{:.&}".replace("&", txtPrec).format(*tup_hsv)
def NcnUpdateReadOnly(self, _context):
    assert tuple(self.col)==tuple(self.colGamm)
    assert tuple(self.colA)==tuple(self.colAGamm)
    self.col4ProvReadOnly = self.colA
def NcnUpdateAlpha(self, context):
    if self.isAlpha:
        for cyc in range(3):
            self.colA[cyc] = self.col[cyc]
            self.colAGamm[cyc] = self.colGamm[cyc]
    else:
        self.col = self.colA[:3]
        self.colGamm = self.colAGamm[:3]
    NcnUpdateColor(self, context)
class NodeColorNote(ManagerNodeRoot):
    nclass = 33#2
    bl_idname = 'MngNodeColorNote'
    bl_label = "Color Note"
    bl_width_max = 512
    bl_width_min = 140
    bl_width_default = 200
    mngCategory = "1Color", 1
    isAlpha: bpy.props.BoolProperty(name="Alpha", default=True, update=NcnUpdateAlpha)
    isGamma: bpy.props.BoolProperty(name="Gamma", default=True, update=NcnUpdateColor)
    col: bpy.props.FloatVectorProperty(name="Color", size=3, soft_min=0.0, soft_max=1.0, subtype='COLOR', update=NcnUpdateColor)
    colA: bpy.props.FloatVectorProperty(name="ColorAlpha", size=4, soft_min=0.0, soft_max=1.0, subtype='COLOR', update=NcnUpdateColor)
    colGamm: bpy.props.FloatVectorProperty(name="ColorGamm", size=3, soft_min=0.0, soft_max=1.0, subtype='COLOR_GAMMA', update=NcnUpdateColor)
    colAGamm: bpy.props.FloatVectorProperty(name="ColorAlphaGamm", size=4, soft_min=0.0, soft_max=1.0, subtype='COLOR_GAMMA', update=NcnUpdateColor)
    col4ProvReadOnly: bpy.props.FloatVectorProperty(size=4, soft_min=0.0, soft_max=1.0, subtype='COLOR', update=NcnUpdateColor)
    isReadOnly: bpy.props.BoolProperty(name="Read only", default=False, update=NcnUpdateReadOnly)
    soldTxtRgbByte: bpy.props.StringProperty()
    soldTxtRgbFloat: bpy.props.StringProperty()
    soldTxtHsvNum: bpy.props.StringProperty()
    soldTxtHsvFloat: bpy.props.StringProperty()
    soldTxtHex: bpy.props.StringProperty()
    decorHeight: bpy.props.IntProperty(name="Decor Height", default=4, min=0, max=12)
    isClassicLy: bpy.props.BoolProperty(name="Classic layout", default=False, update=NcnUpdateColor)
    isLyRgbByte:  bpy.props.BoolProperty(name="Byte RGB",   default=False, description="RGBA")
    isLyRgbFloat: bpy.props.BoolProperty(name="Float RGB",  default=False, description="rgba")
    isLyHsvNum:   bpy.props.BoolProperty(name="Number HSV", default=False, description="HSV")
    isLyHsvFloat: bpy.props.BoolProperty(name="Float HSV",  default=False, description="hsv")
    isLyHex:      bpy.props.BoolProperty(name="Hex",        default=False, description="Hex")
    precisionLyNums: bpy.props.IntProperty(name="Precision", default=3, min=2, max=6, update=NcnUpdateColor)
    txtHexPrefixReplace: bpy.props.StringProperty(name="Hex prefix", default="#", update=NcnUpdateColor)
    isLySubstrate: bpy.props.BoolProperty(name="Substrate", default=False)
    isReverseHex: bpy.props.BoolProperty(name="Reverse hex", default=False, update=NcnUpdateColor)
    isUpperHex: bpy.props.BoolProperty(name="Upper hex", default=False, update=NcnUpdateColor)
    def GetCurColAtt(self):
        return ('colAGamm' if self.isGamma else 'colA') if self.isAlpha else ('colGamm' if self.isGamma else 'col')
    def InitNode(self, _context):
        setattr(self, self.GetCurColAtt(), RandomColor())
        self.isLyHex = True #isLyRgbByte
        self.isLySubstrate = True
    def LyDrawExtNode(self, _context, colLy, _prefs):
        colList = colLy.column(align=True)
        colList.prop(self,'isAlpha')
        row = colList.row()
        row.prop(self, self.GetCurColAtt(), text="")
        row.prop(self,'isGamma')
        colList.prop(self,'decorHeight')
        colList.prop(self,'isReadOnly')
        colList.prop(self,'isClassicLy')
        for att in ("RgbByte", "RgbFloat", "HsvNum", "HsvFloat", "Hex"):
            row0 = colList.row(align=True)
            row1 = row0.row(align=True)
            txt = "isLy"+att
            text = self.bl_rna.properties[txt].description
            row1.prop(self, txt, text=(text if self.isAlpha else text.replace("A", "").replace("a", "")))
            txt = getattr(self, "soldTxt"+att)
            list_spl = re.split("(?<= )|:", txt)
            uu_ly.LyHighlightingText(row0, *list_spl)
            row0.operator(OpSimpleExec.bl_idname, text="", icon='COPYDOWN').exc = f"bpy.context.window_manager.clipboard = {repr((txt, ' '.join(list_spl[1::2])))}[1-event.shift]"
        row = colList.row()
        row.prop(self,'precisionLyNums')
        row.prop(self,'txtHexPrefixReplace', text="")
        row = colList.row()
        row.prop(self,'isLySubstrate')
        row.prop(self,'isReverseHex')
        row = colList.row()
        row.label()
        row.prop(self,'isUpperHex')
    def LyDrawNode(self, _context, colLy, _prefs):
        if self.decorHeight>0:
            rowCol = colLy.row()
            rowCol.prop(self, self.GetCurColAtt(), text="", emboss=self.isClassicLy) #emboss==False для color prop -- это потрясающе!!
            rowCol.scale_y = 0.5*self.decorHeight
        colList = colLy.column()
        for att in ("RgbByte", "RgbFloat", "HsvNum", "HsvFloat", "Hex"):
            if getattr(self, "isLy"+att):
                row = colList.row(align=True)
                row.alignment = 'CENTER'
                if self.isLySubstrate:
                    row = row.box().row()
                    row.scale_y = 0.5
                uu_ly.LyHighlightingText(row, *re.split("(?<= )|:", getattr(self, "soldTxt"+att)))


def NcqgUpdateGamma(self, _context):
    self['colP'] = tuple(map(lambda x: x**(1/self.gamma), self.col))
    self['colN'] = tuple(map(lambda x: x**self.gamma, self.col))
    self['colGP'] = self.colP
    self['colGN'] = self.colN
    self['colG'] = self.col
for chIsG in ("", "G"):
    for chSide in "PN":
        exec(f"def NcqgUpdateGamma{chIsG}{chSide}(self, _context): self.col = tuple(map(lambda x: x**({'1/'*(chSide=='N')}self.gamma), self.col{chIsG}{chSide}))")
def NcqgUpdateGammaG(self, _context):
    self.col = self.colG
class NodeColorQuickGamma(ManagerNodeRoot):
    nclass = 33
    bl_idname = 'MngNodeColorQuickGamma'
    bl_label = "Quick Gamma"
    bl_width_max = 400
    bl_width_min = 140
    bl_width_default = 140
    mngCategory = "1Color", 2
    gamma: bpy.props.FloatProperty(name="Gamma", default=2.2, min=1.0, soft_max=6.0, precision=3, subtype='FACTOR', update=NcqgUpdateGamma)
    decorHeight: bpy.props.IntProperty(name="Decor Height", default=2, min=2, max=12, soft_max=6)
    for chIsG in ("", "G"):
        for chSide in " PN":
            exec(f"col{chIsG}{chSide}: bpy.props.FloatVectorProperty(name=\"Color\", size=4, soft_min=0, soft_max=1, subtype='{'COLOR_GAMMA' if chIsG else 'COLOR'}', update=NcqgUpdateGamma{chIsG}{chSide})")
    def InitNode(self, _context):
        self.col = RandomColor()
    def LyDrawExtNode(self, _context, colLy, _prefs):
        colList = colLy.column(align=True)
        colList.prop(self,'decorHeight')
    def LyDrawNode(self, _context, colLy, _prefs):
        colLy.prop(self,'gamma')
        colList = colLy.column(align=True)
        colList.scale_y = 0.5*self.decorHeight
        row = colList.row(align=True)
        row.prop(self,'colP', text="")
        row.prop(self,'colGP', text="")
        row = colList.row(align=True)
        row.prop(self,'col', text="")
        row.prop(self,'colG', text="")
        row = colList.row(align=True)
        row.prop(self,'colN', text="")
        row.prop(self,'colGN', text="")

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

def NqleUpdateForReCompile(self, _context):
    dict_nqleNdCompiledCache[self.GetSelfNode(NodeQuickLayoutExec.bl_idname, 'lines')] = None
class NqleLineItem(PgNodeCollectionItemWithGetNdSelf):
    fit = "Exec: {'bpy':bpy, 'C':bpy.context, 'D':bpy.data, 'opa':opa, 'self':self}\nLayout |= {'ly': colLy}"
    isActive:  bpy.props.BoolProperty(name="Active",     default=True,        update=NqleUpdateForReCompile)
    isTb:      bpy.props.BoolProperty(name="Toggle",     default=False,       update=NqleUpdateForReCompile)
    tbPoi:  bpy.props.PointerProperty(name="Text Block", type=bpy.types.Text, update=NqleUpdateForReCompile, description=fit)
    txtExec: bpy.props.StringProperty(name="Text Exec",  default="",          update=NqleUpdateForReCompile, description=fit)
    del fit

dict_nqleNdCompiledCache = {}

def NqleUpdateCount(self, _context):
    len = length(self.lines)
    #if len!=self.count: #Заметка: Поскольку изменение количества добавляет и удаляет только пустые, в перекомпиляции нет нужды.
    #    dict_nqleNdCompiledCache[self] = None
    for cyc in range(len, self.count):
        self.lines.add().name = str(cyc)
    for cyc in reversed(range(self.count, len)):
        if not(self.lines[cyc].txtExec or self.lines[cyc].tbPoi):
            self.lines.remove(cyc)
    self['count'] = length(self.lines) #nqleIsCountUpdating
def NqleUpdateMethod(self, _context):
    self.soldIsAsExc = self.method=='EXEC'
class NodeQuickLayoutExec(ManagerNodeAlertness):
    nclass = 10 #8
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
        row.operator(OpSimpleExec.bl_idname, text="Copy as script").exc = f"bpy.context.window_manager.clipboard = {self.__mng_repr__()}.GetCollectedFullText()"
        row.operator(OpSimpleExec.bl_idname, text="Paste as script").exc = f"{self.__mng_repr__()}.SetLinesFromFullText(bpy.context.window_manager.clipboard)"
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
                    row.operator(OpSimpleExec.bl_idname, text="", icon='TRIA_RIGHT').exc = f"{self.__mng_repr__()}.ExecuteOne({cyc})"
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
                colLy.operator(OpSimpleExec.bl_idname, text=self.decorExec).exc = f"{self.__mng_repr__()}.ExecuteAll()"
        elif prefs.isAllowNqleWorking:
            with uu_ly.TryAndErrInLy(colLy): #Заметка: Лучше оставить, ибо часто будут использоваться функции.
                #Заметка: Компиляция с кешированием должны быть по нужде, а не сразу при изменении содержания; чтобы при редактировании через скрипты не вызывать бесполезные вычисления.
                if not( (self.isCaching)and(dict_nqleNdCompiledCache.get(self, None)) ):
                    dict_nqleNdCompiledCache[self] = compile(self.GetCollectedFullText(), "", 'exec')
                dict_globals = self.DoExecute(dict_nqleNdCompiledCache[self], dict_vars={'ly': colLy.column()})
                if self.txtVaribleForAlert in dict_globals:
                    self.ProcAlertState(dict_globals[self.txtVaribleForAlert])
    def DoExecute(self, ess, *, dict_vars={}):
        dict_globals = {'bpy':bpy, 'C':bpy.context, 'D':bpy.data, 'opa':opa, 'self':self}|dict_vars
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
        self.count = length(self.lines)

def NntUpdateTagId(self, context):
    opa.BNode(self.id_data.nodes.active).typeinfo.contents.nclass = ConvNclassTagNameId.dict_сonvertIdToTag[self.idTag]
def NntTimerSetTagId(self, nclass):
    self['idTag'] = ConvNclassTagNameId.dict_сonvertTagToId[nclass]
    self.label = self.label #Теперь нужно явно затриггерить перерисовку; blid нода в макете обновляется, а слайдер -- нет.
class NodeNclassTagViewer(ManagerNodeRoot):
    nclass = 100 #100 #33
    bl_idname = 'MngNodeNclassToggler'
    bl_label = "Nclass Toggler"
    bl_icon = 'EXPERIMENTAL' #Очень жаль, что разрабы рисование кастомных иконок удалили. А с этой иконкой этот нод был таким красивым...
    bl_width_min = 140
    bl_width_default = 200
    possibleDangerousGradation = 1
    mngCategory = "4Hacking", 0
    idTag: bpy.props.IntProperty(name="Tag", default=0, min=0, max=17, update=NntUpdateTagId)
    def LyDrawNode(self, context, colLy, _prefs):
        ndAc = self.id_data.nodes.active
        uu_ly.LyBoxAsLabel(colLy, text=ndAc.bl_label if ndAc else "Active node is None", icon='NODE', active=not not ndAc, alignment='LEFT')
        if ndAc:
            tup_item = ConvNclassTagNameId.tup_сonvertTagName[self.idTag]
            nclass = opa.BNode(ndAc).typeinfo.contents.nclass
            if tup_item[0]!=nclass:
                bpy.app.timers.register(functools.partial(NntTimerSetTagId, self, nclass))
            colLy.prop(self,'idTag', text=f"{tup_item[0]}  —  {tup_item[1]}", slider=True) #-- – —

def NsUpdateSolemn(self, _context):
    try:
        exec(self.txtExecOnUpdate, {'bpy':bpy, 'C':bpy.context, 'D':bpy.data, 'opa':opa, 'self':self, 'val':self.value}, {})
        dict_mngNdErrorEss[self] = ""
    except Exception as ex:
        PrintToConsole(f"Error in {self.__mng_repr__()}: {ex}") #См. тоже самое в NodeAssertor.
        dict_mngNdErrorEss[self] = str(ex)

class ManagerNodeSolemn(ManagerNodeAlertness):
    nclass = 8
    bl_icon = 'SOLO_OFF' #SOLO_OFF  BRUSH_DATA
    bl_width_max = 1024
    bl_width_min = 64
    bl_width_default = 253+math.pi #Потому что я так захотел; для "щепотки эстетики".
    possibleDangerousGradation = 2
    mngCategory = "3Solemn", 0
    pathHlFromTheme = ''
    txtEvalAlertState = compile("False", "", 'eval')
    txtCeremonial: bpy.props.StringProperty(name="Solemn Text", default="Ceremonial")
    txtExecOnUpdate: bpy.props.StringProperty(name="Exec On Update", default="", description="{'bpy':bpy, 'C':bpy.context, 'D':bpy.data, 'opa':opa, 'self':self, 'val':getattr(self, self.txtPropSelfSolemn)}")
    value = property(lambda s: getattr(s, s.txtPropSelfSolemn), lambda s, v: setattr(s, s.txtPropSelfSolemn, v))
    def InitNodePreChain(self, _context):
        ManagerNodeAlertness.InitNodePreChain(self, _context)
        self.txtExecOnUpdate = "#log = print; log(val)" #"print (val)".replace(" ", "")
    def LyDrawExtNodePreChain(self, _context, colLy, _prefs):
        ManagerNodeAlertness.LyDrawExtNodePreChain(self, _context, colLy, _prefs)
        uu_ly.LyNiceColorProp(colLy, self,'txtCeremonial', align=True)
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
        uu_ly.LyNiceColorProp(colLy, self,'decorIcon0', align=True)
        uu_ly.LyNiceColorProp(colLy, self,'decorIcon1', align=True)
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
                uu_ly.LyNiceColorProp(colLy, self,'colour', text=self.txtCeremonial)

class NodeSolemnLayout(ManagerNodeSolemn):
    bl_idname = 'MngNodeSolemnLayout'
    bl_label = "Solemn Layout"
    txtPropSelfSolemn = 'txtExec'
    fit = "{'bpy':bpy, 'C':bpy.context, 'D':bpy.data, 'opa':opa, 'self':self, 'ly':colLy}"
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
            exec(self.txtExec, {'bpy':bpy, 'C':bpy.context, 'D':bpy.data, 'opa':opa, 'self':self, 'ly':colLy}, {})
        except Exception as ex:
            PrintToConsole(f"Error in {self.__mng_repr__()}: {ex}")
            colLy.label(text=str(ex), icon='ERROR')

dict_nspCompileCache = {}
def NspPollPointer(self, poi):
    suTxt = self.txtPoll
    if suTxt not in dict_nspCompileCache:
        dict_nspCompileCache[suTxt] = compile(suTxt, "", 'eval')
    return eval(dict_nspCompileCache[suTxt], {'bpy':bpy, 'C':bpy.context, 'D':bpy.data, 'opa':opa, 'self':self, 'poi':poi}, {}) if self.txtPoll else True
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
    txtPoll: bpy.props.StringProperty(name="Poll function", default="", description="{'bpy':bpy, 'C':bpy.context, 'D':bpy.data, 'opa':opa, 'self':self, 'poi':poi}")
    decorTypeToNode: bpy.props.BoolProperty(name="Decor Type to node", default=False)
    def InitNode(self, _context):
        self.typePoi = 'Object'
        self.txtPoll = "True #Poll function"
        self.decorTypeToNode = True
    def LyDrawExtNode(self, _context, colLy, prefs):
        row = colLy.row(align=True)
        colLy.prop(self,'txtPoll', text="", icon='SCRIPT')
        colLy.prop(self,'typePoi', text="")
        colLy.prop(self,'decorTypeToNode')
    def LyDrawNode(self, _context, colLy, prefs):
        if self.decorTypeToNode:
            colLy.prop(self,'typePoi', text="")
        colLy.prop(self,'pointer'+self.typePoi, text="")

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
    mngCategory = "2Script", 1
    fit = "{'bpy':bpy, 'C':bpy.context, 'D':bpy.data, 'opa':opa, 'self':self}"
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
    decorIcon: bpy.props.StringProperty(name="Icon", default='NONE', update=MngUpdateDecorIcon)
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
                    if not( (self.isCaching)and(dict_naNdCompileCache.get(self, None)) ):
                        dict_naNdCompileCache[self] = compile(self.GetTextAssert(), "", 'exec') if isAsExec else compile("True" if (False)and(self.isTb)and(not self.tbPoi) else self.GetTextAssert(), "", 'eval')
                    dict_globals = {'bpy':bpy, 'C':bpy.context, 'D':bpy.data, 'opa':opa, 'self':self}
                    if isAsExec:
                        exec(dict_naNdCompileCache[self], dict_globals, dict_globals)
                        if 'result' in dict_globals:
                            result = not dict_globals['result']
                        else:
                            self.ProcAlertState(self.isAlertOnError)
                            dict_mngNdErrorEss[self] = ('INFO', "The execution should create the `result` variable.")
                            result = self.isAlertOnError
                            dict_naNdLastRunTime[self] = 0.0
                            return result
                    else:
                        result = not eval(dict_naNdCompileCache[self], dict_globals, {})
                    self.ProcAlertState(result)
                    dict_mngNdErrorEss[self] = ()
                    dict_naNdLastRunTime[self] = tpc #Не знаю, как по правильному, перед оценкой или после.
                except Exception as ex:
                    self.ProcAlertState(self.isAlertOnError)
                    PrintToConsole(f"Error in {self.__mng_repr__()}: {ex}") #Когда сообщение об ошибке слишком длинное и не влезает в нод -- дополнительно отправить в консоль.
                    dict_mngNdErrorEss[self] = ('ERROR', str(ex))
                    result = self.isAlertOnError
                    dict_naNdLastRunTime[self] = 0.0
                return result
        return None
    def DrawLabel(self):
        self.Assert()
        if self.isAlwaysWorks:
            if key:=DgProcAddSelfInDictSpec(self, dict_naNdIsAlwaysWorks):
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
        uu_ly.LyNiceColorProp(row, self,'decorText')
        row.active = self.isLyReadOnly
        uu_ly.LyNiceColorProp(colList, self,'decorIcon')
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
        if self.decorIcon not in set_allIcons:
            LyInvalidDecorIcon(rowMain, self)
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
        if tup_err:=dict_mngNdErrorEss.get(self, None):
            colLy.label(text=tup_err[1], icon=tup_err[0])

import sys, datetime

list_consoleLog = [""]

def NcvLog(txtData):
    for cyc, li in enumerate(txtData.split("\n")):
        if cyc:
            list_consoleLog.append("")
        list_consoleLog[-1] += li
    for li in DgCollectEvalDoubleGetFromDict(dict_necvNdSibscribeToUpdate):
        li[1].WriteLog(txtData)
class NcvOverrideStdOut():
    def write(txt):
        sys.__stdout__.write(txt)
        NcvLog(txt)
class NcvOverrideStdErr():
    def write(txt):
        sys.__stderr__.write(txt)
        import ctypes; MessageBox = ctypes.windll.user32.MessageBoxW; MessageBox(None, "Омг, оно используется!", "Mng Debug", 0)
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

dict_necvNdSibscribeToUpdate = {}

def NecvLiUpdateMsg(self, _context):
    self['msg'] = self.msgProvReadOnly
class NecvLineItem(PgNodeCollectionItemWithGetNdSelf):
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
    txtExecOnUpdate: bpy.props.StringProperty(name="Exec on update", default="", description="{'bpy':bpy, 'C':bpy.context, 'D':bpy.data, 'opa':opa, 'self':self, 'msg':txtData}")
    decorVars: bpy.props.IntProperty(name="Decor", default=1, min=0, max=15)
    def InitNode(self, _context):
        self.lines.add().name = datetime.datetime.now().strftime(self.txtTimeFormat)
        #self.txtExecOnUpdate = "if \"\\n\" in msg: self.label = str(int(self.label if self.label else 0)+1)"
    def DrawLabel(self):
        DgProcAddSelfInDictSpec(self, dict_necvNdSibscribeToUpdate)
        return ""
    def LyDrawExtNode(self, _context, colLy, _prefs):
        colLy.prop(self,'isDisplayAsProp')
        colGroup = colLy.column(align=True)
        colGroup.prop(self,'isDisplayTime')
        row = colGroup.row(align=True)
        uu_ly.LyNiceColorProp(row, self,'txtTimeFormat', text="Time f:", align=True)
        row.active = self.isDisplayTime
        colGroup = colLy.column(align=True)
        colGroup.prop(self,'decorVars')
        uu_ly.LyNiceColorProp(colLy, self,'txtExecOnUpdate', text="On Update:", icon='SCRIPT', align=True)
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
            exec(self.txtExecOnUpdate, {'bpy':bpy, 'C':bpy.context, 'D':bpy.data, 'opa':opa, 'self':self, 'msg':txtData}, {})
        try: #"Нельзя писать в рисовании".
            self.lines[-1].name = self.lines[-1].name
        except:
            bpy.app.timers.register(functools.partial(self.DoLog, txtData))
            return
        self.DoLog(txtData)

list_mngAlertClause = [False, False]
class MngOpAcceptDisclaimer(bpy.types.Operator):
    bl_idname = 'mng.mng_accept_disclaimer'
    bl_label = "Accept Disclaimer"
    bl_options = {'UNDO'}
    def execute(self, context):
        prefs = Prefs()
        list_mngAlertClause[0] = not prefs.isDisclaimerAcceptanceUserExec
        list_mngAlertClause[1] = not prefs.isDisclaimerAcceptancePossibleDangerous
        if (prefs.isDisclaimerAcceptanceUserExec)and(prefs.isDisclaimerAcceptancePossibleDangerous):
            prefs.isDisclaimerAcceptance = True
        return {'FINISHED'}
def MngUpdateDisclaimerAcceptance(self, _context):
    for cyc, si in enumerate(set_mngUnsafeNodeCls):
        try:
            if self.isDisclaimerAcceptance:
                bpy.utils.register_class(si)
            #else: #А ещё здесь был ClsNodeIsRegistered()...
            #    bpy.utils.unregister_class(si) #План оказался лажа. Также см. проверку isDisclaimerAcceptance в ManagerNodeRoot.
        except:
            pass
def MngUpdateDisclaimerClauses(self, _context):
    list_mngAlertClause[0] = False if self.isDisclaimerAcceptanceUserExec else list_mngAlertClause[0]
    list_mngAlertClause[1] = False if self.isDisclaimerAcceptancePossibleDangerous else list_mngAlertClause[1]
class AddonPrefs(AddonPrefs):
    isDisclaimerAcceptance: bpy.props.BoolProperty(default=False, update=MngUpdateDisclaimerAcceptance)
    isDisclaimerAcceptanceUserExec: bpy.props.BoolProperty(name="Disclaimer Acceptance User Exec", default=False, update=MngUpdateDisclaimerClauses)
    isDisclaimerAcceptancePossibleDangerous: bpy.props.BoolProperty(name="Disclaimer Acceptance Possible Dangerous", default=False, update=MngUpdateDisclaimerClauses)
    def LyDrawDisclaimerAcceptance(self, where):
        def LyDisclaimerClause(where, prop, text, *, alert=False):
            row = where.row()
            col = row.column()
            col.alignment = 'CENTER'
            for cyc, txt in enumerate(text.split("\n")):
                col.alert = (alert)and(not cyc)
                col.prop(self, prop, text=txt, icon='BLANK1' if cyc else 'NONE', emboss=not cyc)
            row.alignment = 'CENTER'
        if self.isDisclaimerAcceptance:
            return
        colBox = where.box().column()
        colBox.label(text="To access all nodes, please agree to the disclaimer.")
        colDis = colBox.box().column()
        row = colDis.row()
        row.alignment = 'CENTER'
        row.alert = True
        row.label(text="Disclaimer".upper())
        fit = "The addon has a lot of `exec()` from user input.\nIf you write something wrong, you can make things worse for yourself."
        LyDisclaimerClause(colDis, 'isDisclaimerAcceptanceUserExec', text=fit, alert=list_mngAlertClause[0])
        fit = "The addon has an unknown non-zero risk of (non-zero) data corruption.\nBe careful and make backups."+" "*55
        LyDisclaimerClause(colDis, 'isDisclaimerAcceptancePossibleDangerous', text=fit, alert=list_mngAlertClause[1])
        row = colDis.row()
        row.operator(MngOpAcceptDisclaimer.bl_idname, text="Register unsafe nodes")
        row.active = (self.isDisclaimerAcceptanceUserExec)and(self.isDisclaimerAcceptancePossibleDangerous)


def Prefs():
    return bpy.context.preferences.addons[bl_info['name']].preferences

def MngUpdateRegisterTreeType(self, _context):
    try: #Что-то я не знаю, как проверить зарегистрированность дерева.
        if self.isRegisterTreeType:
            bpy.utils.register_class(ManagerTree)
        else:
            bpy.utils.unregister_class(ManagerTree)
    except:
        pass
class AddonPrefs(AddonPrefs):
    isRegisterTreeType: bpy.props.BoolProperty(name="Register Tree Type", default=True, update=MngUpdateRegisterTreeType)
    isAllowNqleWorking: bpy.props.BoolProperty(name="Quick Layout Node is working", default=True)
    isAllowNcWorking: bpy.props.BoolProperty(name="Console Node is working", default=True)
    def draw(self, _context):
        colLy = self.layout.column()
        self.LyDrawDisclaimerAcceptance(colLy)
        colMain = uu_ly.LyAddHeaderedBox(colLy, text="preferences", active=False)
        colMain.prop(self,'isRegisterTreeType')
        if self.isDisclaimerAcceptance:
            colMain.prop(self,'isAllowNqleWorking')
            colMain.prop(self,'isAllowNcWorking')

def RecrGetSubclasses(cls):
    list_result = [cls]
    for li in cls.__subclasses__():
        list_result.extend(RecrGetSubclasses(li))
    return list_result

set_mngNodeClasses = set()
dict_catAdds = {}
for li in RecrGetSubclasses(ManagerNodeRoot):
    if hasattr(li, 'bl_idname'):
        set_mngNodeClasses.add(li)
        assert hasattr(li, 'mngCategory')
        dict_catAdds.setdefault(li.mngCategory[0], []).append(li)
list_catAdds = [(li[0][1:], li[1]) for li in sorted(dict_catAdds.items(), key=lambda a: a[0][0])] #Отсортировать порядок категорий и избавиться от их начальных цифр.
del dict_catAdds
for li in list_catAdds: #Отсортировать ноды в категориях.
    li[1].sort(key=lambda a: a.mngCategory[1])
#set_mngNodeBlids = set(si.bl_idname for si in set_mngNodeClasses)
set_mngUnsafeNodeCls = set()
for si in set_mngNodeClasses:
    if si.possibleDangerousGradation:
        set_mngUnsafeNodeCls.add(si)


dict_globals = globals()
tmp = dict_globals['AddonPrefs']
del dict_globals['AddonPrefs']
dict_globals['AddonPrefs'] = tmp
del tmp, dict_globals

list_classes = []
def register():
    def ResetPrefsToDefault(prefs):
        for li in txt_regResetToDefault.split():
            pr = prefs.bl_rna.properties[li]
            if hasattr(pr,'default_flag'):
                setattr(prefs, li, pr.default_flag)
            elif hasattr(pr,'default'):
                setattr(prefs, li, pr.default)
            else:
                getattr(prefs, li).clear()
    for dv in globals().copy().values():
        if dv.__class__.__name__ in {"RNAMeta", "RNAMetaPropGroup"}:
            list_classes.append(dv)
            if dv in {ManagerTree}:
                continue
            if (dv in set_mngNodeClasses)and(dv.possibleDangerousGradation):
                continue
            try:
                bpy.utils.register_class(dv)
            except:
                pass
    prefs = Prefs()
    prefs.isDisclaimerAcceptance = prefs.isDisclaimerAcceptance
    prefs.isRegisterTreeType = prefs.isRegisterTreeType
    ResetPrefsToDefault(prefs)
    PanelAddManagerNode.CreateUnfs(prefs)
    PanelAddManagerNode_SubPresetsAndEx.CreateUnfs(prefs)
def unregister():
    global isUnregistrationInProgress
    isUnregistrationInProgress = True
    for li in reversed(list_classes):
        try:
            bpy.utils.unregister_class(li)
        except:
            pass

if __name__=="__main__":
    register()
