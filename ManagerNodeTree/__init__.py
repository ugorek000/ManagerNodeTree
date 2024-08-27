bl_info = {'name':"ManagerNodeTree", 'author':"ugorek",
           'version':(2,2,0), 'blender':(4,2,0), 'created':"2024.08.28",
           'description':"Nodes for special high level managenment",
           'location':"NodeTreeEditor > N Panel > Mng",
           'warning':"!",
           'category':"System",
           'tracker_url':"https://github.com/ugorek000/ManagerNodeTree/issues", 'wiki_url':"https://github.com/ugorek000/ManagerNodeTree/issues"}
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
import uu_regutils
rud = uu_regutils.ModuleData()
#def SmartAddToRegAndAddToKmiDefs(*args, **kwargs):
#    return uu_regutils.SmartAddToRegAndAddToKmiDefs(rud, *args, **kwargs)

#import nodeitems_utils
import functools
LogConsole = print


class AddonPrefs(bpy.types.AddonPreferences):
    bl_idname = bl_info['name'] if __name__=="__main__" else __name__
txt_regResetToDefault = ""

if True: #Для защиты от всяких `bpy.types.Node.__repr__ = lambda a: f"||{a.name}||"`, (которые я использовал в своём RANTO для дебага например)
    bpy.types.Node.__mng_repr__ = lambda nd: f"bpy.data.node_groups[\"{nd.id_data.name}\"].nodes[\"{nd.name}\"]" #Но всё равно пришлось делать вручную, ибо повторные активации аддона.
    bpy.types.Node.__mng_repr__.__doc__ = f"Backup from {AddonPrefs.bl_idname} addon."
else:
    bpy.types.Node.__mng_repr__ = bpy.types.Node.__repr__
    #А так же в этом случае Node.__repr__ не имеет .__code__, так что не получится 'import types; types.FunctionType(bpy.types.Node.__repr__.__code__, ...)', чтобы изменить __doc__ у копии.

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
        exec(self.exc)
        return {'FINISHED'}

set_allIcons = set(bpy.types.UILayout.bl_rna.functions['prop'].parameters['icon'].enum_items.keys())


class ConvNclassTagNameId:
    dict_сonvertTagName = {0:"INPUT",    1:"OUTPUT",   2:"none",     3:"OP_COLOR", 4:"OP_VECTOR",  5:"OP_FILTER", 6:"GROUP",     8:"CONVERTER",  9:"MATTE",
                           10:"DISTORT", 12:"PATTERN", 13:"TEXTURE", 32:"SCRIPT",  33:"INTERFACE", 40:"SHADER",   41:"GEOMETRY", 42:"ATTRIBUTE", 100:"LAYOUT"}
    dict_сonvertIdToTag = dict(( (cyc, dk) for cyc, dk in enumerate(dict_сonvertTagName.keys()) ))
    dict_сonvertTagToId = dict(( (dv, dk) for dk, dv in dict_сonvertIdToTag.items() ))
    tup_сonvertTagName = tuple(dict_сonvertTagName.items())
    for dk, dv in tuple(dict_сonvertTagName.items()):
        dict_сonvertTagName[dv] = dk
    del dict_сonvertTagName


list_catAdds = []


def MngUpdateDecorIcon(self, _context):
    if not self.decorIcon:
        self['decorIcon'] = self.bl_rna.properties['decorIcon'].default
    self['decorIcon'] = self.decorIcon.replace(" ", "") #Замена нужна, чтобы красное поле ввода отображало plaseholder, а не тупо какой-то прямоугольник вытянутый сплошного цвета.
def LyInvalidDecorIcon(where, self):
    row0 = where.row(align=True)
    row1 = row0.row(align=True)
    row1.label(text="", icon='ERROR')
    row1.alert = True
    row1.alignment = 'LEFT'
    row1.prop(self,'decorIcon', text="", placeholder="Icon")
    row0.alert = True
    row0.alignment = 'CENTER'
    row0.label(text="..."*100) #Если нод адски широкий и пользователь где-то по середине, то чтобы не было ощущения, что макет просто исчез.


dict_ndTxtError = {}

class ManagerTree(bpy.types.NodeTree):
    bl_idname = 'ManagerNodeTree'
    bl_label = "Manager Node Tree"
    bl_icon = 'FILE_BLEND'
ManagerTree.__doc__ = bl_info['description']

class ManagerNodeFiller:
    nclass = 0
    isNotSetupNclass = True
    def InitNodePreChain(self,context):pass
    def InitNode(self,context):pass
    def DrawLabel(self):return ""
    def LyDrawExtPreChain(self,context,colLy,prefs):pass
    def LyDrawExtNode(self,context,colLy,prefs):pass
    def LyDrawPreChain(self,context,colLy,prefs):pass
    def LyDrawNode(self,context,colLy,prefs):pass
    def LyDrawPostChain(self,context,colLy,prefs):pass
class ManagerNodeRoot(bpy.types.Node, ManagerNodeFiller):
    @classmethod
    def poll(cls, tree):
        return True
    def init(self, context):
        self.InitNodePreChain(context)
        self.InitNode(context)
    def draw_label(self):
        if self.isNotSetupNclass:
            opa.BNode(self).typeinfo.contents.nclass = self.nclass
            self.__class__.isNotSetupNclass = False
        return self.DrawLabel()
    def draw_buttons_ext(self, context, layout):
        colLy = layout.column()
        prefs = Prefs()
        self.LyDrawExtPreChain(context, colLy, prefs)
        self.LyDrawExtNode(context, colLy, prefs)
    def draw_buttons(self, context, layout):
        if "debug": self.draw_label()
        colLy = layout.column()
        prefs = Prefs()
        self.LyDrawPreChain(context, colLy, prefs)
        self.LyDrawNode(context, colLy, prefs)
        self.LyDrawPostChain(context, colLy, prefs)

def MnaUpdateAlertColor(self, _context):
    self['alertColor'] = self.alertColor[:3]+(float(self.alertColor[3]>0.5),)
class ManagerNodeAlertness(ManagerNodeRoot):
    alertColor: bpy.props.FloatVectorProperty(name="Alert Color", size=4, min=0.0, max=1.0, subtype='COLOR_GAMMA', update=MnaUpdateAlertColor)
    blinkingAlert: bpy.props.FloatProperty(name="Blinking Alert", default=0.0, min=0.0, max=1.0, subtype='FACTOR')
    #isActiveAlert: property(lambda s: any(s.alertColor[3:]))
    def LyDrawExtPreChain(self, context, colLy, prefs):
        uu_ly.LyNiceColorProp(colLy, self,'alertColor')
    #Заметка: draw_label() не вызывается, если label!="" и нод свёрнут, но вызывается, если развёрнут.
    def ProcAlertState(self, ess):
        bNd = opa.BNode(self)
        #Помимо use_custom_color используется незанятый 1<<20 для личных нужд аддона.
        #Ибо всё ещё нельзя писать в рисовании в своё кастомное поле класса 'lastIsAlert = ...'.
        #Заметка: бит 1<<20 сохраняется в .blend файле.
        num = 32768 | 1048576
        if (not self.mute)and(not not ess)and(self.alertColor[3]):
            bNd.flag |= num
            bNd.color = self.alertColor[:3] #Выкуси, предупреждение "нельзя писать в рисовании".
        elif bNd.flag & 1048576:
            bNd.flag &= ~num

class PresetsAndEx:
    def AddNodeByBlid(tree, meta_type='Preset'):
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
    def DoubleBigExec(tree, meta_type='Preset'):
        list_addedNodes = []
        ndNqle0 = tree.nodes.new(NodeQuickLayoutExec.bl_idname)
        list_addedNodes.append(ndNqle0)
        ndNqle0.width = 415
        ndNqle0.name = "DoubleBigExec0"
        ndNqle0.label = "Speed up aiming for cursor work by large button size."
        ndNqle0.isShowOnlyLayout = True
        ndNqle0.visibleButtons = 0
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
        ndNqle0.lines.add().txtExec = f"ndTar = bpy.context.space_data.edit_tree.nodes.get(\"{ndNqle1.name}\")"
        ndNqle0.lines.add().txtExec = "row = ly.row(align=True)"
        ndNqle0.lines.add().txtExec = f"row.operator('{OpSimpleExec.bl_idname}', text=\"Big button for anti-missclick\").exc = " "f\"{repr(ndTar)}.ExecuteAll()\""
        ndNqle0.lines.add().txtExec = "row.scale_y = 5.0"
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
        ndNqle1.count = ndNqle1.count
        return list_addedNodes
    def ThemeRoundness(tree, meta_type='Example'):
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
        ndNsf.txtExecOnUpdate = f"C.space_data.edit_tree.nodes[\"{ndNqle0.name}\"].ExecuteAll()"
        ##
        ndNqle0.lines.clear()
        ndNqle0.lines.add().txtExec = "theme = bpy.context.preferences.themes[0].user_interface"
        ndNqle0.lines.add().txtExec = "txtAtts = \"regular  tool  toolbar_item  radio  text  option  toggle  num  numslider  box  menu  pulldown  menu_back  pie_menu  tooltip  menu_item  scroll  progress  list_item  tab\""
        ndNqle0.lines.add().txtExec = f"if ndTar:=C.space_data.edit_tree.nodes.get(\"{ndNsf.name}\"):"
        ndNqle0.lines.add().txtExec = "  val = ndTar.value"
        ndNqle0.lines.add().txtExec = "  for li in txtAtts.split():"
        ndNqle0.lines.add().txtExec = "    setattr(getattr(bpy.context.preferences.themes[0].user_interface, \"wcol_\"+li),'roundness', val)"
        ndNqle0.lines.add().txtExec = "  bpy.context.preferences.themes[0].user_interface.panel_roundness = val"
        ndNqle0.count = ndNqle0.count
        ##
        ndNqle1.lines.clear()
        ndNqle1.lines.add().txtExec = ndNqle0.lines[0].txtExec
        ndNqle1.lines.add().txtExec = ndNqle0.lines[1].txtExec
        ndNqle1.lines.add().txtExec = ndNqle0.lines[2].txtExec
        ndNqle1.lines.add().txtExec = "  sum = 0.0"
        ndNqle1.lines.add().txtExec = ndNqle0.lines[4].txtExec
        ndNqle1.lines.add().txtExec = "    sum += getattr(getattr(bpy.context.preferences.themes[0].user_interface, \"wcol_\"+li),'roundness')"
        ndNqle1.lines.add().txtExec = "  ndTar[ndTar.txtPropSelfSolemn] = sum/len(txtAtts.split())"
        ndNqle1.lines.add().txtExec = "C.node.id_data.nodes.remove(C.node)"
        ndNqle1.count = ndNqle1.count
        ##
        ndNqle2.lines.clear()
        ndNqle2.lines.add().txtExec = ndNqle0.lines[0].txtExec
        ndNqle2.lines.add().txtExec = ndNqle0.lines[1].txtExec
        ndNqle2.lines.add().txtExec = "colList = ly.column(align=True)"
        list_names = ["Regular", "Tool", "Toolbar Item", "Radio Buttons", "Text", "Option", "Toggle", "Number Field", "Value Slider", "Box", "Menu", "Pulldown", "Menu Background", "Pie Menu", "Tooltip", "Menu Item", "Scroll Bar", "Progress Bar", "List Item", "Tab"]
        ndNqle2.lines.add().txtExec = "list_names = [\""+"\", \"".join(list_names)+"\"]"
        ndNqle2.lines.add().txtExec = "for cyc, li in enumerate(txtAtts.split()):"
        ndNqle2.lines.add().txtExec = "  colList.prop(getattr(bpy.context.preferences.themes[0].user_interface, \"wcol_\"+li),'roundness', text=list_names[cyc])"
        ndNqle2.lines.add().txtExec = "colList.prop(bpy.context.preferences.themes[0].user_interface,'panel_roundness')"
        ndNqle2.count = ndNqle2.count
        return list_addedNodes
    def AssertFrameStep(tree, meta_type='Example'):
        list_addedNodes = []
        ndNa = tree.nodes.new(NodeAssertor.bl_idname)
        list_addedNodes.append(ndNa)
        ndNa.width = 560
        ndNa.name = "AssertFrameStep"
        ndNa.txtEval = "(C.scene.frame_step == 1) and (C.scene.render.resolution_y % 2 == 0)"
        ndNa.decorText = "Frame Step is 1  and  Even Resolution[1]"
        ndNa.alertColor = (0.85, 0.425, 0.0, 1.0)
        return list_addedNodes
    def StatOfTbLines(tree, meta_type='Example'):
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
    def CheckLyRedraw(tree, meta_type='Example'):
        list_addedNodes = []
        ndNqle = tree.nodes.new(NodeQuickLayoutExec.bl_idname)
        list_addedNodes.append(ndNqle)
        ndNqle.name = "CheckLyRedraw"
        ndNqle.label = "Redraw Check"
        ndNqle.width = 200
        ndNqle.visibleButtons = 0
        ndNqle.lines.clear()
        ndNqle.lines.add().txtExec = "import random; ly.label(text=str(random.random()), icon=\"SEQUENCE_COLOR_0\"+str(random.randint(1, 9)))"
        ndNqle.isShowOnlyLayout = True
        #ndNqle.count = ndNqle.count
        return list_addedNodes
    dict_catPae = {}
    for dk, dv in dict(locals()).items():
        if callable(dv):
            dict_catPae.setdefault(dv.__defaults__[0], []).append(dv.__code__.co_name) #meta_type используется здесь.
    list_catPae = [(li[0], li[1]) for li in sorted(dict_catPae.items(), key=lambda a: {"P":0, "E":1}[a[0][0]])] #list(dict_catPae.items())

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
        colLy.prop(prefs,'pamnFilter', text="", icon='SORTBYEXT' if prefs.pamnFilter else 'NONE') #Я так захотел.
        colListCats = colLy.column()
        ndAc = context.space_data.edit_tree.nodes.active
        patr = re.compile(prefs.pamnFilter) if prefs.pamnFilter else None
        for li in list_catAdds:
            list_found = PanelAddManagerNode.PreScan(patr, li[1], LKey=lambda a:a.bl_label)
            if (list_found)and(colListItems:=PanelAddManagerNode.LyCatAddIndUnfAuto(colListCats, li[0], prefs, anyway=not not patr)):
                for cls in list_found:
                    rowOp = PanelAddManagerNode.LyAddItem(colListItems, text=cls.bl_label, icon=getattr(cls,'bl_icon', 'NONE'))
                    fit = f"bpy.ops.node.add_node('INVOKE_DEFAULT', type=\"{cls.bl_idname}\", use_transform=True)"
                    rowOp.operator(OpSimpleExec.bl_idname, text="", icon='TRIA_LEFT', depress=(not not ndAc)and(ndAc.bl_idname==cls.bl_idname)and(ndAc.select)).exc = fit
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
    bl_label = "Presets and Ex."
    bl_space_type = 'NODE_EDITOR'
    bl_region_type = 'UI'
    bl_parent_id = PanelAddManagerNode.bl_idname
    bl_options = {'DEFAULT_CLOSED'}
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
    if hasattr(context,'node'): #Удаление содержимого через Backspace (без явного редактирования).
        if (not self.body)or(int(self.name)==length(context.node.lines)-1):
            NnpUpdateCount(context.node, context)
        if False:
            context.node.txtBackupLines = "\n".join(ci.body for ci in context.node.lines)

class NnpLine(bpy.types.PropertyGroup):
    body: bpy.props.StringProperty(name="Body", default="", update=NnpUpdateLineBody)
class NodeNotepad(ManagerNodeNote):
    bl_idname = 'MngNodeNotepad'
    bl_label = "Notepad"
    bl_width_min = 140
    mngCategory = "0Text", 2
    lines: bpy.props.CollectionProperty(type=NnpLine)
    #txtBackupLines: bpy.props.StringProperty(default="") #Не используется. Идея была, что если нод сломается, то восстановить через просое свойство будет проще, чем через PropertyGroup.
    isAutoCount: bpy.props.BoolProperty(name="Auto notepad", default=True, update=NnpUpdateCount)
    count: bpy.props.IntProperty(name="Count of lines", default=1, min=0, max=32, soft_min=1, soft_max=12, update=NnpUpdateCount)
    isLyReadOnly: bpy.props.BoolProperty(name="Read only", default=False, update=NnpUpdateCount)
    isProtectErasion: bpy.props.BoolProperty(name="Protect erasion", default=True)
    decorLineAlignment: bpy.props.EnumProperty(name="Lines alignment", default='DOCK', items=( ('FLAT',"Flat",""), ('DOCK',"Docking",""), ('GAP',"Gap","") ))
    includeNumbering: bpy.props.IntProperty(name="Include numbering", default=2, min=0, max=2)
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
        colList.prop(self,'includeNumbering')
        colList.prop(self,'decorVars')
    def LyDrawNode(self, _context, colLy, _prefs):
        colLines = colLy.column(align=self.decorLineAlignment!='GAP')
        len = length(str(self.count)) #length(self.lines)
        numbering = self.includeNumbering
        txt = ":" if numbering==2 else ""
        decorVars = self.decorVars
        for cyc, ci in enumerate(self.lines):
            rowLine = ( colLines.row() if self.decorLineAlignment=='DOCK' else colLines ).row(align=True)
            if numbering:
                rowNum = rowLine.row(align=True)
                rowNum.alignment = 'LEFT'
                rowNum.active = decorVars%2
                rowNum.alert = decorVars//2%2
                rowNum.label(text=str(cyc+1).zfill(len)+txt)
            rowBody = rowLine.row(align=True)
            rowBody.active = decorVars//4%2
            rowBody.alert = decorVars//8%2
            if self.isLyReadOnly:
                rowBody.label(text=ci.body)
            else:
                rowBody.prop(ci,'body', text="")

from random import random as Rand
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
        setattr(self, 'colGamm' if self.isGamma else 'col', (Rand(), Rand(), Rand()))
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
        self['col'] = self.col4SoldReadOnly[:3]
        self['colGamm'] = self.col4SoldReadOnly[:3]
        self['colA'] = self.col4SoldReadOnly
        self['colAGamm'] = self.col4SoldReadOnly
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
    self.col4SoldReadOnly = self.colA
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
    col4SoldReadOnly: bpy.props.FloatVectorProperty(size=4, soft_min=0.0, soft_max=1.0, subtype='COLOR', update=NcnUpdateColor)
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
        setattr(self, self.GetCurColAtt(), (Rand(), Rand(), Rand(), 1.0))
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
            row0.operator(OpSimpleExec.bl_idname, text="", icon='COPYDOWN').exc = f"context.window_manager.clipboard = {repr((txt, ' '.join(list_spl[1::2])))}[1-event.shift]"
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
    bl_label = "Color Quick Gamma"
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
        self.col = (Rand(), Rand(), Rand(), 1.0)
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
        dict_nqleNdCompileCache[ndRepr] = None
        ndRepr.count = length(ndRepr.lines)
        return {'FINISHED'}

def NqleUpdateForReCompile(self, _context):
    dict_nqleNdCompileCache[self.GetSelfNode()] = None
class NqleLineItem(bpy.types.PropertyGroup):
    fit = "Exec: {'bpy':bpy, 'C':bpy.context, 'D':bpy.data, 'opa':opa, 'self':self}\nLayout |= {'ly': colLy}"
    isActive:  bpy.props.BoolProperty(name="Active",     default=True,        update=NqleUpdateForReCompile)
    isTb:      bpy.props.BoolProperty(name="Toggle",     default=False,       update=NqleUpdateForReCompile)
    tbPoi:  bpy.props.PointerProperty(name="Text Block", type=bpy.types.Text, update=NqleUpdateForReCompile, description=fit)
    txtExec: bpy.props.StringProperty(name="Text Exec",  default="",          update=NqleUpdateForReCompile, description=fit)
    del fit
    def GetSelfNode(self): #Жаль, что реализация не предоставляет доступа к владельцу; https://blender.stackexchange.com/a/323542/156014
        for nd in self.id_data.nodes:
            if nd.bl_idname==NodeQuickLayoutExec.bl_idname:
                poi = self.as_pointer()
                for ln in nd.lines:
                    if ln.as_pointer()==poi:
                        return nd
        assert False

dict_nqleNdCompileCache = {}

def NqleUpdateCount(self, _context):
    len = length(self.lines)
    #if len!=self.count: #Заметка: поскольку изменение количетсва добавляет и удаляет только пустые, в перекомплияции нет нужды.
    #    dict_nqleNdCompileCache[self] = None
    for cyc in range(len, self.count):
        self.lines.add().name = str(cyc)
    for cyc in reversed(range(self.count, len)):
        if not(self.lines[cyc].txtExec or self.lines[cyc].tbPoi):
            self.lines.remove(cyc)
    self['count'] = length(self.lines) #nqleIsCountUpdating
def NqleUpdateMethod(self, _context):
    self.soldIsAsExc = self.method=='EXEC'
class NodeQuickLayoutExec(ManagerNodeRoot):
    nclass = 8
    bl_idname = 'MngNodeQuickLayoutExec'
    bl_label = "Quick Layout Exec"
    bl_icon = 'LONGDISPLAY'
    bl_width_max = 2048
    bl_width_min = 64
    bl_width_default = 430
    mngCategory = "2Script", 0
    lines: bpy.props.CollectionProperty(type=NqleLineItem)
    method: bpy.props.EnumProperty(name="Method", default='LAYOUT', items=( ('LAYOUT',"As Layout",""), ('EXEC',"As Exec","") ), update=NqleUpdateMethod)
    soldIsAsExc: bpy.props.BoolProperty()
    count: bpy.props.IntProperty(name="Count of lines", default=1, min=1, max=64, soft_min=1, soft_max=16, update=NqleUpdateCount)
    isCaching: bpy.props.BoolProperty(name="Caching", default=True)
    isShowOnlyLayout: bpy.props.BoolProperty(name="Layout display only", default=False)
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
        row = colList.row(align=True)
        row.prop(self,'visibleButtons')
        row.active = not self.isShowOnlyLayout
        colLy.separator()
        colOps = colLy.column(align=True)
        row = colOps.row()
        row.operator(OpSimpleExec.bl_idname, text="Copy as script").exc = f"context.window_manager.clipboard = {self.__mng_repr__()}.GetCollectedFullText()"
        row.operator(OpSimpleExec.bl_idname, text="Paste as script").exc = f"{self.__mng_repr__()}.SetLinesFromFullText(context.window_manager.clipboard)"
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
                if visibleButs//2%2:
                    fit = (ci.isTb)and(not ci.txtExec)or not(ci.isTb or not ci.tbPoi) #Показать пользователю подсветкой, что на противоположном варианте что-то есть, и "не забудь про это".
                    rowTb.prop(ci,'isTb', text="", icon='WORDWRAP_OFF', emboss=True, invert_checkbox=fit) #RIGHTARROW  GREASEPENCIL  WORDWRAP_OFF  ALIGN_JUSTIFY
                rowTb.active = False
                if (self.soldIsAsExc)and(visibleButs//4%2):
                    row = rowLine.row(align=True)
                    row.operator(OpSimpleExec.bl_idname, text="", icon='TRIA_RIGHT').exc = f"{self.__mng_repr__()}.ExecuteOne({cyc})"
                    row.active = not(ci.isTb and not ci.tbPoi)
                if ci.isTb:
                    rowLine.prop(ci,'tbPoi', text="", icon='TEXT')
                else:
                    rowLine.prop(ci,'txtExec', text="", icon='SCRIPT')
                if visibleButs//8%2:
                    rowLine.operator_props(NqleOpDelLine.bl_idname, text="", icon='TRASH', repr=self.__mng_repr__(), num=cyc)
                rowLine.active = ci.isActive
        if self.soldIsAsExc:
            if self.decorExec:
                colLy.operator(OpSimpleExec.bl_idname, text=self.decorExec).exc = f"{self.__mng_repr__()}.ExecuteAll()"
        elif prefs.isAllowNqleWorking:
            with uu_ly.TryAndErrInLy(colLy): #Заметка: лучше оставить, ибо часто будут использоваться функции.
                #Заметка: компиляция с кешированием должны быть по нужде, а не сразу при изменении содержания; чтобы при редактировании через скрипты не вызывать бесполезные вычисления.
                if not( (self.isCaching)and(dict_nqleNdCompileCache.get(self, None)) ):
                    dict_nqleNdCompileCache[self] = compile(self.GetCollectedFullText(), "", 'exec')
                self.DoExecute(dict_nqleNdCompileCache[self], dict_vars={'ly': colLy})
    def DoExecute(self, ess, *, dict_vars={}):
        exec(ess, {'bpy':bpy, 'C':bpy.context, 'D':bpy.data, 'opa':opa, 'self':self}|dict_vars, None)
    def ExecuteOne(self, inx):
        ci = self.lines[inx]
        self.DoExecute(ci.txtExec if not ci.isTb else ci.tbPoi.as_string() if ci.tbPoi else "")
    def ExecuteAll(self):
        self.DoExecute(self.GetCollectedFullText())
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
    opa.BNode(context.space_data.edit_tree.nodes.active).typeinfo.contents.nclass = ConvNclassTagNameId.dict_сonvertIdToTag[self.idTag]
def NntTimerSetTagId(self, nclass):
    self['idTag'] = ConvNclassTagNameId.dict_сonvertTagToId[nclass]
    self.label = self.label #Теперь нужно явно затриггерить перерисовку; blid нода в макете обновляется, а слейдер -- нет.
class NodeNclassTagViewer(ManagerNodeRoot):
    nclass = 100 #100 #33
    bl_idname = 'MngNodeNclassToggler'
    bl_label = "Nclass Toggler"
    bl_icon = 'EXPERIMENTAL' #Очень жаль, что разрабы рисование кастомных иконок удалили. А с этой иконкой этот нод был таким красивым...
    bl_width_min = 140
    bl_width_default = 200
    mngCategory = "4Hacking", 0
    idTag: bpy.props.IntProperty(name="Tag", default=0, min=0, max=17, update=NntUpdateTagId)
    def LyDrawNode(self, context, colLy, _prefs):
        ndAc = context.space_data.edit_tree.nodes.active
        uu_ly.LyBoxAsLabel(colLy, text=ndAc.bl_label if ndAc else "Active node is None", icon='NODE', active=not not ndAc, alignment='LEFT')
        if ndAc:
            tup_item = ConvNclassTagNameId.tup_сonvertTagName[self.idTag]
            nclass = opa.BNode(ndAc).typeinfo.contents.nclass
            if tup_item[0]!=nclass:
                bpy.app.timers.register(functools.partial(NntTimerSetTagId, self, nclass))
            colLy.prop(self,'idTag', text=f"{tup_item[0]}  —  {tup_item[1]}", slider=True) #-- – —

def NsUpdateBg(self, context):
    if (self.alertColor[3])and(alertState:=eval(self.txtEvalAlertState, {'self':self})):
        #Заметка: При резком изменении alertColor[3]==1.0, здесь alertState==True, но цвет у нода почему то сразу не перерисовывается.
        self.ProcAlertState(alertState)
    elif self.pathHlFromTheme:
        self.use_custom_color = (eval(self.txtEvalBgState, {'self':self}))and(self.isHlFromTheme)
        list_atts = self.pathHlFromTheme.split(".")
        self.color = getattr(getattr(context.preferences.themes[0].user_interface, list_atts[0]), list_atts[1])[:3]
    else:
        self.use_custom_color = False
    self.lastAlertColor = self.alertColor
    try:
        exec(self.txtExecOnUpdate, {'bpy':bpy, 'C':bpy.context, 'D':bpy.data, 'opa':opa, 'self':self, 'val':getattr(self, self.txtPropSelfSolemn)}, None)
        dict_ndTxtError[self] = ""
    except Exception as ex:
        LogConsole(f"Error in {self.__mng_repr__()}: {ex}") #См. тоже самое в NodeAssertor.
        dict_ndTxtError[self] = str(ex)

class ManagerNodeSolemn(ManagerNodeAlertness):
    nclass = 8
    bl_icon = 'SOLO_OFF' #SOLO_OFF  BRUSH_DATA
    bl_width_max = 1024
    bl_width_min = 64
    bl_width_default = 253+math.pi #Потому что я так захотел; для "щепотки эстетики".
    mngCategory = "3Solemn", 0
    pathHlFromTheme = '' #Заметка топологии: См. в DoProcBg.
    txtEvalAlertState = compile("False", "", 'eval')
    #Поскольку ProcAlertState только в NsUpdateBg, нужно чтобы цвет нода реагировал от измененения 'ManagerNodeAlertness.alertColor'
    lastAlertColor: bpy.props.FloatVectorProperty(size=ManagerNodeAlertness.__annotations__['alertColor'].keywords['size'])
    txtCeremonial: bpy.props.StringProperty(name="Solemn Text", default="Ceremonial")
    alerting: bpy.props.BoolProperty(name="Alert trigger", default=False, update=NsUpdateBg)
    txtExecOnUpdate: bpy.props.StringProperty(name="Exec On Update", default="", description="{'bpy':bpy, 'C':bpy.context, 'D':bpy.data, 'opa':opa, 'self':self, 'val':getattr(self, self.txtPropSelfSolemn)}")
    value = property(lambda s: getattr(s, s.txtPropSelfSolemn), lambda s, v: setattr(s, s.txtPropSelfSolemn, v))
    def InitNodePreChain(self, _context):
        ManagerNodeAlertness.InitNodePreChain(self, _context)
        self.txtExecOnUpdate = "#log = print; log(val)" #"print (val)".replace(" ", "")
    def DrawLabel(self):
        if self.lastAlertColor[:]!=self.alertColor[:]:
            bpy.app.timers.register(functools.partial(NsUpdateBg, self, bpy.context))
        return ""
    def LyDrawExtPreChain(self, _context, colLy, _prefs):
        ManagerNodeAlertness.LyDrawExtPreChain(self, _context, colLy, _prefs)
        uu_ly.LyNiceColorProp(colLy, self,'txtCeremonial', align=True)
        colLy.prop(self,'txtExecOnUpdate', text="", icon='SCRIPT')
    def LyDrawPostChain(self, _context, colLy, _prefs):
        ManagerNodeAlertness.LyDrawPostChain(self, _context, colLy, _prefs)
        if txt:=dict_ndTxtError.get(self, ""):
            colLy.label(text=txt, icon='ERROR')

def NsbUpdateDecor(self, context):
    if not(self.isHlFromTheme or self.decorVar):
        self['decorVar'] = 1
    NsUpdateBg(self, context) #Заметка: бесполезные вызовы от decorVar.
class NodeSolemnBool(ManagerNodeSolemn):
    bl_idname = 'MngNodeSolemnBool'
    bl_label = "Solemn Bool"
    pathHlFromTheme = 'wcol_option.inner_sel'
    txtEvalBgState = compile("self.bool", "", 'eval')
    txtEvalAlertState = compile("self.bool^self.alerting", "", 'eval')
    txtPropSelfSolemn = 'bool'
    bool: bpy.props.BoolProperty(name="Bool", default=False, update=NsUpdateBg)
    alerting: bpy.props.BoolProperty(name="Alert trigger", default=False, update=NsUpdateBg)
    isHlFromTheme: bpy.props.BoolProperty(name="Highlighting from theme", default=True, update=NsbUpdateDecor)
    decorVar: bpy.props.IntProperty(name="Decor", default=1, min=0, max=3, update=NsbUpdateDecor)
    decorIcon0: bpy.props.StringProperty(name="Icon for False", default="CHECKBOX_HLT")
    decorIcon1: bpy.props.StringProperty(name="Icon for True", default="CHECKBOX_DEHLT")
    def InitNode(self, context):
        self.bool = True
    def LyDrawExtNode(self, context, colLy, prefs):
        colLy.prop(self,'alerting')
        colLy.prop(self,'isHlFromTheme')
        colLy.prop(self,'decorVar') #.row().prop_inac(self,'decorVar', active=(self.isHlFromTheme)or(self.decorVar))
        uu_ly.LyNiceColorProp(colLy, self,'decorIcon0', align=True)
        uu_ly.LyNiceColorProp(colLy, self,'decorIcon1', align=True)
    def LyDrawNode(self, context, colLy, prefs):
        decorVar = self.decorVar
        txtCeremonial = self.txtCeremonial
        colLy.prop(self,'bool', text=" " if (decorVar//2%2)and(not txtCeremonial)and(not decorVar//4) else txtCeremonial, icon=(self.decorIcon0 if self.bool else self.decorIcon1) if decorVar//2%2 else 'NONE', emboss=decorVar%2)

class NodeSolemnFactor(ManagerNodeSolemn):
    bl_idname = 'MngNodeSolemnFactor'
    bl_label = "Solemn Factor"
    pathHlFromTheme = 'wcol_numslider.item'
    txtEvalBgState = compile("not self.factor==0.0", "", 'eval')
    txtEvalAlertState = compile("not( (self.factor==0.0)and(self.alerting<1)or(self.factor==1.0)and(self.alerting>-1) )", "", 'eval')
    txtPropSelfSolemn = 'factor'
    factor: bpy.props.FloatProperty(name="Factor", default=0.0, min=0, max=1, subtype='FACTOR', update=NsUpdateBg)
    alerting: bpy.props.IntProperty(name="Alert trigger", default=0, min=-1, max=1, update=NsUpdateBg)
    isHlFromTheme: bpy.props.BoolProperty(name="Highlighting from theme", default=True, update=NsUpdateBg)
    def InitNode(self, context):
        self.factor = 0.5
    def LyDrawExtNode(self, context, colLy, prefs):
        colLy.prop(self,'alerting')
        colLy.prop(self,'isHlFromTheme')
    def LyDrawNode(self, context, colLy, prefs):
        colLy.prop(self, 'factor', text=self.txtCeremonial)

class NodeSolemnInteger(ManagerNodeSolemn):
    bl_idname = 'MngNodeSolemnInteger'
    bl_label = "Solemn Integer"
    txtEvalAlertState = compile("self.integer", "", 'eval')
    txtPropSelfSolemn = 'integer'
    integer: bpy.props.IntProperty(name="Integer", default=0, update=NsUpdateBg)
    def LyDrawNode(self, context, colLy, prefs):
        colLy.prop(self, 'integer', text=self.txtCeremonial)

class NodeSolemnFloat(ManagerNodeSolemn):
    bl_idname = 'MngNodeSolemnFloat'
    bl_label = "Solemn Float"
    txtEvalAlertState = compile("self.float", "", 'eval')
    txtPropSelfSolemn = 'float'
    float: bpy.props.FloatProperty(name="Float", default=0.0, step=10, update=NsUpdateBg)
    def LyDrawNode(self, context, colLy, prefs):
        colLy.prop(self, 'float', text=self.txtCeremonial)

class NodeSolemnColor(ManagerNodeSolemn):
    bl_idname = 'MngNodeSolemnColor'
    bl_label = "Solemn Color"
    txtEvalAlertState = "any(self.colour)"
    txtPropSelfSolemn = 'colour'
    colour: bpy.props.FloatVectorProperty(name="Color", size=4, min=0.0, max=1.0, subtype='COLOR_GAMMA', update=NsUpdateBg) #Как ловко я выкрутился от конфликта api, но с сохранением эстетики.
    decorVar: bpy.props.IntProperty(name="Decor", default=0, min=0, max=2)
    def InitNode(self, context):
        self.colour = bpy.context.preferences.themes[0].user_interface.wcol_numslider.item
        self.alertColor = self.colour
        self.decorVar = 2
    def LyDrawExtNode(self, context, colLy, prefs):
        colLy.prop(self,'decorVar')
    def LyDrawNode(self, context, colLy, prefs):
        if not self.txtCeremonial:
            colLy.prop(self,'colour', text="")
        else:
            decorVar = self.decorVar
            if not decorVar:
                colLy.prop(self,'colour', text=self.txtCeremonial)
            elif decorVar==1:
                colLy.row(align=True).prop(self,'colour', text=self.txtCeremonial)
            else:
                uu_ly.LyNiceColorProp(colLy, self,'colour', text=self.txtCeremonial)

class NodeSolemnLayout(ManagerNodeSolemn):
    bl_idname = 'MngNodeSolemnLayout'
    bl_label = "Solemn Layout"
    txtPropSelfSolemn = 'txtExec'
    txtExec: bpy.props.StringProperty(name="Text Exec", description="{'bpy':bpy, 'C':bpy.context, 'D':bpy.data, 'opa':opa, 'self':self, 'ly':colLy}", update=NsUpdateBg) #update для txtPropSelfSolemn.
    isShowOnlyLayout: bpy.props.BoolProperty(name="Layout display only", default=False)
    def InitNode(self, context):
        self.txtExec = "ly.row().prop(bpy.context.scene.render,'engine', expand=True)"
    def LyDrawExtNode(self, context, colLy, prefs):
        colLy.prop(self,'isShowOnlyLayout')
    def LyDrawNode(self, context, colLy, prefs):
        if not self.isShowOnlyLayout:
            colLy.prop(self, 'txtExec', text="", icon='SCRIPT')
        try:
            exec(self.txtExec, {'bpy':bpy, 'C':bpy.context, 'D':bpy.data, 'opa':opa, 'self':self, 'ly':colLy}, None)
        except Exception as ex:
            LogConsole(f"Error in {self.__mng_repr__()}: {ex}")
            colLy.label(text=str(ex), icon='ERROR') #todo0 А что если добавить "хиты"?, первые несколько секунд после возникновения ошибки показывать иконку красным цветом.

dict_naNdCompileCache = {}

def NaUpdateForReCompile(self, _context):
    dict_naNdCompileCache[self] = None
class NodeAssertor(ManagerNodeAlertness):
    nclass = 5 #42 #10 #40 #41
    bl_idname = 'MngNodeAssertor'
    bl_label = "Assert"
    bl_icon = 'STYLUS_PRESSURE' #STYLUS_PRESSURE  CAMERA_STEREO  MEMORY  HAND
    bl_width_max = 700
    bl_width_min = 140
    bl_width_default = 300
    mngCategory = "2Script", 1
    fit = "{'bpy':bpy, 'C':bpy.context, 'D':bpy.data, 'opa':opa, 'self':self}"
    txtEval: bpy.props.StringProperty(name="Text Eval", default="",            update=NaUpdateForReCompile, description=fit)
    tbPoi:   bpy.props.PointerProperty(name="Text Block", type=bpy.types.Text, update=NaUpdateForReCompile, description=fit)
    isTb:    bpy.props.BoolProperty(name="Use Text Block", default=False,      update=NaUpdateForReCompile)
    isCaching:      bpy.props.BoolProperty(name="Caching",        default=True)
    isLyReadOnly:   bpy.props.BoolProperty(name="Read only",      default=False)
    isAlertOnError: bpy.props.BoolProperty(name="Alert on error", default=False)
    decorText: bpy.props.StringProperty(name="Decor Text", default="")
    decorIcon: bpy.props.StringProperty(name="Icon", default='NONE', update=MngUpdateDecorIcon)
    decorHeight: bpy.props.FloatProperty(name="Decor Height", default=0.0, min=0.0, max=4.0)
    del fit
    def GetTextAssertEval(self):
        if self.isTb:
            if self.tbPoi:
                return self.tbPoi.as_string()
        else:
            return self.txtEval
        return ""
    def InitNode(self, _context):
        self.txtEval = "True"
        self.decorHeight = 0.17
        self.alertColor = (1.0, 1.0, 1.0, 1.0)
    def DrawLabel(self):
        try:
            if not( (self.isCaching)and(dict_naNdCompileCache.get(self, None)) ):
                txtAssert = self.GetTextAssertEval()
                dict_naNdCompileCache[self] = compile(txtAssert if txtAssert else "", "", 'eval')
            self.ProcAlertState(not eval(dict_naNdCompileCache[self], {'bpy':bpy, 'C':bpy.context, 'D':bpy.data, 'opa':opa, 'self':self}))
            dict_ndTxtError[self] = ""
        except Exception as ex:
            self.ProcAlertState(self.isAlertOnError)
            LogConsole(f"Error in {self.__mng_repr__()}: {ex}") #Когда сообщение об ошибке слишком длинное и не влезает в нод -- дополнительно отправить в консоль.
            dict_ndTxtError[self] = str(ex)
        return ( self.decorText if self.isLyReadOnly else ( (self.tbPoi.name if self.tbPoi else "" ) if self.isTb else self.txtEval ) ) if self.hide else ""
    def LyDrawExtNode(self, _context, colLy, _prefs):
        colList = colLy.column(align=True)
        colList.prop(self,'isTb')
        colList.prop(self,'isCaching')
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
                rowLabel.label(text=self.decorText if self.decorText else ((self.tbPoi.name if self.tbPoi else "" ) if self.isTb else self.txtEval ), icon=self.decorIcon)
            else:
                if self.isTb:
                    rowMain.prop(self,'tbPoi', text="", icon=self.decorIcon if self.decorIcon!='NONE' else 'TEXT')
                else:
                    rowMain.prop(self,'txtEval', text="", icon=self.decorIcon if self.decorIcon!='NONE' else 'SCRIPT')
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
        if txt:=dict_ndTxtError.get(self, ""):
            colLy.label(text=txt, icon='ERROR')

def Prefs():
    return bpy.context.preferences.addons[bl_info['name']].preferences

class AddonPrefs(AddonPrefs):
    isAllowNqleWorking: bpy.props.BoolProperty(name="Quick Layout Node is working", default=True)
    def draw(self, context):
        colLy = self.layout.column()
        colLy.prop(self,'isAllowNqleWorking')

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
list_catAdds = [(li[0][1:], li[1]) for li in sorted(dict_catAdds.items(), key=lambda a: a[0][0])]
del dict_catAdds
for li in list_catAdds:
    li[1].sort(key=lambda a: a.mngCategory[1])
#set_mngNodeBlids = set(si.bl_idname for si in set_mngNodeClasses)


uu_regutils.BringRegToFront(rud, globals(), 'AddonPrefs')

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
    uu_regutils.LazyRegAll(rud, globals())
    prefs = Prefs()
    ResetPrefsToDefault(prefs)
    PanelAddManagerNode.CreateUnfs(prefs)
    PanelAddManagerNode_SubPresetsAndEx.CreateUnfs(prefs)
def unregister():
    uu_regutils.UnregFromLazyRegAll(rud)

if __name__=="__main__":
    register()