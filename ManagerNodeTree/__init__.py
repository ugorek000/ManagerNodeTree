bl_info = {'name':"ManagerNodeTree", 'author':"ugorek",
           'version':(2,0,2), 'blender':(4,2,0), 'created':"2024.08.22",
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
def SmartAddToRegAndAddToKmiDefs(*args, **kwargs):
    return uu_regutils.SmartAddToRegAndAddToKmiDefs(rud, *args, **kwargs)

#import nodeitems_utils
import functools


class AddonPrefs(bpy.types.AddonPreferences):
    bl_idname = bl_info['name'] if __name__=="__main__" else __name__

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

#class OpSimpleFunc(bpy.types.Operator): #В основном для mind-разметки; и без exec()'а.
#    bl_idname = 'unu.simple_func'
#    bl_label = "OpSimpleFunc"
#    bl_options = {'UNDO'}
#    fn: bpy.props.StringProperty(name="FnName", default="")
#    def invoke(self, context, event):
#        #`globals()[self.fn](context)` #Если ниже будет ещё больше наворотов, то это уже будет не "SimpleFunc".
#        Func = globals()[self.fn]
#        match Func.__code__.co_argcount:
#            case 0: result = Func()
#            case 1: result = Func(context)
#            case 2: result = Func(context, event)
#            case _: raise
#        return result if result else {'FINISHED'}

set_allIcons = set(bpy.types.UILayout.bl_rna.functions['prop'].parameters['icon'].enum_items.keys())


class ConvNclassTagNameId:
    dict_сonvertTagName = {0:"INPUT",    1:"OUTPUT",   2:"none",     3:"OP_COLOR", 4:"OP_VECTOR",  5:"OP_FILTER", 6:"GROUP",     8:"CONVERTER",  9:"MATTE",
                           10:"DISTORT", 12:"PATTERN", 13:"TEXTURE", 32:"SCRIPT",  33:"INTERFACE", 40:"SHADER",   41:"GEOMETRY", 42:"ATTRIBUTE", 100:"LAYOUT"}
    dict_сonvertIdToTag = dict(( (cyc, dk) for cyc, dk in enumerate(dict_сonvertTagName.keys()) ))
    dict_сonvertTagToId = dict(( (dv, dk) for dk, dv in dict_сonvertIdToTag.items() ))
    tup_сonvertTagName = tuple(dict_сonvertTagName.items())
    for dk, dv in tuple(dict_сonvertTagName.items()):
        dict_сonvertTagName[dv] = dk
#    @staticmethod
#    def TagToName(tag):
#        return ConvNclassTagNameId.dict_сonvertTagName[tag if tag in ConvNclassTagNameId.dict_сonvertTagName else 2]
#    @staticmethod
#    def NameToTag(name):
#        return ConvNclassTagNameId.dict_сonvertTagName[name if name in ConvNclassTagNameId.dict_сonvertTagName else "none"]
    del dict_сonvertTagName


#def DcDoubleLyProps(cls): #Всё равно лажа.
#    set_names = {"BoolProperty", "BoolVectorProperty", "IntProperty", "IntVectorProperty", "FloatProperty", "FloatVectorProperty", "StringProperty", "EnumProperty"}
#    for dk, dv in tuple(cls.__annotations__.items()):
#        if str(dv).split(">, {")[0].split("function ")[-1] in set_names:
#            #====class DoubleLy(bpy.types.PropertyGroup): #Вариант c присоединением "в глубину" оказался так себе.
#            #        isIncludeToNode: bpy.props.BoolProperty(name="Show in node", default=False)
#            #        wrapped: dv
#            #    bpy.utils.register_class(DoubleLy)
#            #    #...Если писать с новым именем, то у оригинала в str() `'attr': ...` почему-то тоже перезаписывается.
#            #    cls.__annotations__[] = bpy.props.PointerProperty(type=DoubleLy)
#            cls.__annotations__["dlp_"+dk] = bpy.props.BoolProperty(name="Show in node", default=False)
#    return cls


#class CatAdds:
#    dict_cats = {}
#    def __setitem__(self, txt, cls):
#        self.dict_cats.setdefault(txt, []).append(cls)
#CatAdds = CatAdds()
dict_catAdds = {}

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
    def ExecuteNodePreChain(self):pass
    def ExecuteNode(self):pass
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
#    def Execute(self):
#        self.ExecuteNodePreChain()
#        self.ExecuteNode()

#class NodeWithErrorReport(ManagerNodeRoot):
#    txtErrorInExecute: bpy.props.StringProperty(name="Error", default="")
#    def DrawPostChain(self, context, colLy):
#        if self.txtErrorInExecute:
#            colLy.alert = True
#            colLy.prop(self,'txtErrorInExecute', text="", icon="ERROR")
#            colLy.alert = False
#    def Execute(self):
#        try:
#            self.ExecuteNodePreChain()
#            self.ExecuteNode()
#            self.txtErrorInExecute = ""
#        except Exception as ex:
#            self.txtErrorInExecute = str(ex)

class PanelManagerActiveNode(bpy.types.Panel):
    bl_idname = 'MNG_PT_ManagerActiveNode'
    bl_label = "Manager Active Node"
    bl_space_type = 'NODE_EDITOR'
    bl_region_type = 'UI'
    bl_category = "Mng"
    @classmethod
    def poll(cls, context):
        tree = context.space_data.edit_tree
        return (tree)and(tree.nodes.active)and(tree.nodes.active.bl_idname in set_mngNodeBlids)
    def draw(self, context):
        colLy = self.layout.column()
        ndAc = context.space_data.edit_tree.nodes.active
        colLy.prop(ndAc,'name', text="", icon='NODE')
        ndAc.draw_buttons_ext(context, colLy)

class PanelAddManagerNode(bpy.types.Panel):
    bl_idname = 'MNG_PT_AddManagerNode'
    bl_label = "Add Manager Node"
    bl_space_type = 'NODE_EDITOR'
    bl_region_type = 'UI'
    bl_category = "Mng"
    @classmethod
    def poll(cls, context):
        return not not context.space_data.edit_tree
    def draw(self, context):
        colLy = self.layout.column()
        prefs = Prefs()
        colCats = colLy.column()
        ndAc = context.space_data.edit_tree.nodes.active
        for dk, dv in dict_catAdds.items():
            rowCat = colCats.box().row(align=True)
            rowCat.scale_y = 0.75
            ciUnf = prefs.amnUnfurils.get(dk)
            rowName = rowCat.row(align=True)
            rowName.alignment = 'LEFT'
            rowName.prop(ciUnf,'unf', text=ciUnf.name, icon='DOWNARROW_HLT' if ciUnf.unf else 'RIGHTARROW', emboss=False)
            rowCat.prop(ciUnf,'unf', text=" ", emboss=False)#+True, icon='BLANK1')
            if ciUnf.unf:
                rowList = colCats.row(align=True)
                rowList.label(icon='BLANK1')
                colList = rowList.column(align=True)
                for cls in dv:
                    rowItem = colList.row(align=True)
                    rowAdd = rowItem.row(align=True)
                    fit = f"bpy.ops.node.add_node('INVOKE_DEFAULT', type=\"{cls.bl_idname}\", use_transform=True)"
                    rowAdd.operator(OpSimpleExec.bl_idname, text="", icon='TRIA_LEFT', depress=(ndAc.bl_idname==cls.bl_idname)and(ndAc.select)).exc = fit
                    rowAdd.scale_x = 1.75
                    rowLabel = rowItem#.row(align=True)
                    rowLabel.alignment = 'LEFT'
                    rowLabel.label(text=" "+cls.bl_label)
                    if False:
                        rowIcon = rowLabel.row(align=True)
                        rowIcon.alignment = 'LEFT'
                        rowIcon.label(icon=getattr(cls,'bl_icon', 'NONE'))

class AmnUnfuril(bpy.types.PropertyGroup):
    unf: bpy.props.BoolProperty(default=False)
class AddonPrefs(AddonPrefs):
    amnUnfurils: bpy.props.CollectionProperty(type=AmnUnfuril)

def GenAmnUnfs(prefs):
    for si in set_mngNodeClasses:
        if not prefs.amnUnfurils.get(si.mngCategory):
            prefs.amnUnfurils.add().name = si.mngCategory
    global GenAmnUnfs
    del GenAmnUnfs

class ManagerNodeNote(ManagerNodeRoot):
    nclass = 32
    bl_width_max = 2048
    bl_width_default = 256

class NodeSimpleNote(ManagerNodeNote):
    bl_idname = 'NodeNote'
    bl_label = "Simple Note"
    bl_width_min = 64
    mngCategory = 'Text'
    body: bpy.props.StringProperty(name="Note body", default="")
    def DrawLabel(self):
        return self.body if self.hide else self.bl_label
    def LyDrawExtNode(self, _context, colLy, _prefs):
        uu_ly.LyNiceColorProp(colLy, self,'body') #colLy.prop(self,'body')
    def LyDrawNode(self, _context, colLy, _prefs):
        colLy.prop(self,'body', text="")


def NnUpdateDecorIcon(ndSelf, _context):
    if not ndSelf.decorIcon:
        ndSelf['decorIcon'] = ndSelf.bl_rna.properties['decorIcon'].default
    ndSelf['decorIcon'] = ndSelf.decorIcon.replace(" ", "")
class NodeNote(ManagerNodeNote):
    bl_idname = 'MngNodeNote'
    bl_label = "Note"
    bl_width_min = 140
    mngCategory = 'Text'
    note: bpy.props.StringProperty(name="Note body", default="")
    isLyReadOnly: bpy.props.BoolProperty(name="Read only", default=False)
    isLyCenter: bpy.props.BoolProperty(name="Center", default=False)
    decorIcon: bpy.props.StringProperty(name="Icon", default="NONE", update=NnUpdateDecorIcon)
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
            row0 = colLy.row(align=True)
            row1 = row0.row(align=True)
            row1.label(text="", icon='ERROR')
            row1.alert = True
            row1.alignment = 'LEFT'
            row1.prop(self,'decorIcon', text="", placeholder="Icon")
            row0.alert = True
            row0.alignment = 'CENTER'
            row0.label(text="..."*100) #Если нод адски широкий и пользователь где-то по середине, то чтобы не было ощущения, что макет просто исчез.
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


def NnpUpdateCount(ndSelf, _context):
    len = length(ndSelf.lines)
    if ndSelf.isAutoCount:
        for cyc in reversed(range(len)):
            if not ndSelf.lines[cyc].body:
                ndSelf.lines.remove(cyc)
        if not ndSelf.isLyReadOnly:
            ndSelf.lines.add().name = str(length(ndSelf.lines))
    else:
        for cyc in range(len, ndSelf.count):
            ndSelf.lines.add().name = str(cyc)
        for cyc in reversed(range(ndSelf.count, len)):
            if not(ndSelf.isProtectErasion and ndSelf.lines[cyc].body):
                ndSelf.lines.remove(cyc)
    ndSelf['count'] = length(ndSelf.lines)
    if not ndSelf.count:
        ndSelf['count'] = 1
        ndSelf.lines.add().name = "0"
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
    mngCategory = 'Text'
    lines: bpy.props.CollectionProperty(type=NnpLine)
    txtBackupLines: bpy.props.StringProperty(default="") #Не используется. Идея была, что если нод сломается, то восстановить через просое свойство будет проще, чем через PropertyGroup.
    isAutoCount: bpy.props.BoolProperty(name="Auto notepad", default=True, update=NnpUpdateCount)
    count: bpy.props.IntProperty(name="Count of lines", default=1, min=0, max=32, soft_min=1, soft_max=12, update=NnpUpdateCount)
    isLyReadOnly: bpy.props.BoolProperty(name="Read only", default=False, update=NnpUpdateCount)
    isProtectErasion: bpy.props.BoolProperty(name="Protect erasion", default=True)
    decorLineAlignment: bpy.props.EnumProperty(name="Lines alignment", default='DOCK', items=( ('FLAT',"Flat",""), ('DOCK',"Docking",""), ('GAP',"Gap","") ))
    includeNumbering: bpy.props.IntProperty(name="Include numbering", default=2, min=0, max=2)
    decor: bpy.props.IntProperty(name="decor", default=4, min=0, max=15)
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
        colList.prop(self,'decor')
    def LyDrawNode(self, _context, colLy, _prefs):
        colLines = colLy.column(align=self.decorLineAlignment!='GAP')
        len = length(str(self.count)) #length(self.lines)
        numbering = self.includeNumbering
        txt = ":" if numbering==2 else ""
        decor = self.decor
        for cyc, ci in enumerate(self.lines):
            rowLine = ( colLines.row() if self.decorLineAlignment=='DOCK' else colLines ).row(align=True)
            if numbering:
                rowNum = rowLine.row(align=True)
                rowNum.alignment = 'LEFT'
                rowNum.active = decor%2
                rowNum.alert = decor//2%2
                rowNum.label(text=str(cyc+1).zfill(len)+txt)
            rowBody = rowLine.row(align=True)
            rowBody.active = decor//4%2
            rowBody.alert = decor//8%2
            if self.isLyReadOnly:
                rowBody.label(text=ci.body)
            else:
                rowBody.prop(ci,'body', text="")

from random import random as Rand
from mathutils import Color

def NscUpdateCol(ndSelf, _context):
    ndSelf.use_custom_color = not ndSelf.isClassicLy
    if ndSelf.isGamma:
        ndSelf.color = ndSelf.colGamm
        ndSelf['col'] = ndSelf.colGamm
    else:
        ndSelf.color = tuple(map(lambda x: x**(1/2.2), ndSelf.col))
        ndSelf['colGamm'] = ndSelf.col
class NodeSimpleColor(ManagerNodeRoot):
    nclass = 33#2
    bl_idname = 'MngNodeSimpleColor'
    bl_label = "Color"
    bl_width_max = 384
    bl_width_min = 64
    bl_width_default = 140
    mngCategory = 'Color'
    isGamma: bpy.props.BoolProperty(name="Gamma", default=True, update=NscUpdateCol)
    col: bpy.props.FloatVectorProperty(name="Color", size=3, soft_min=0, soft_max=1, subtype='COLOR', update=NscUpdateCol)
    colGamm: bpy.props.FloatVectorProperty(name="ColorGamm", size=3, soft_min=0, soft_max=1, subtype='COLOR_GAMMA', update=NscUpdateCol)
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


def NcnUpdateColor(ndSelf, _context):
    ndSelf.use_custom_color = not ndSelf.isClassicLy
    if ndSelf.isReadOnly:
        ndSelf['col'] = ndSelf.col4SoldReadOnly[:3]
        ndSelf['colGamm'] = ndSelf.col4SoldReadOnly[:3]
        ndSelf['colA'] = ndSelf.col4SoldReadOnly
        ndSelf['colAGamm'] = ndSelf.col4SoldReadOnly
    else:
        if ndSelf.isAlpha:
            if ndSelf.isGamma:
                ndSelf.color = ndSelf.colAGamm[:3]
                ndSelf['colA'] = ndSelf.colAGamm
            else:
                ndSelf.color = tuple(map(lambda x: x**(1/2.2), ndSelf.colA[:3]))
                ndSelf['colAGamm'] = ndSelf.colA
        else:
            if ndSelf.isGamma:
                ndSelf.color = ndSelf.colGamm
                ndSelf['col'] = ndSelf.colGamm
            else:
                ndSelf.color = tuple(map(lambda x: x**(1/2.2), ndSelf.col))
                ndSelf['colGamm'] = ndSelf.col
    if ndSelf.isAlpha:
        tup_rgbaByte = tuple(map(lambda x: int(x*255), ndSelf.colA))
        ndSelf.soldTxtRgbByte = "R:{} G:{} B:{} A:{}".format(*tup_rgbaByte)
        txtPrec = str(ndSelf.precisionLyNums)
        ndSelf.soldTxtRgbFloat = "r:{:.&} g:{:.&} b:{:.&} a:{:.&}".replace("&", txtPrec).format(*ndSelf.colA).replace("0.", ".").replace("1.0", "1.")
        muv = 3*ndSelf.isReverseHex
        txtHex = hex(tup_rgbaByte[abs(muv-3)]+tup_rgbaByte[abs(muv-2)]*256+tup_rgbaByte[abs(muv-1)]*65536+tup_rgbaByte[abs(muv)]*16777216)[2:]
        ndSelf.soldTxtHex = f"Hex-{'abgr' if muv else 'rgba'}:"+ndSelf.txtHexPrefixReplace+(txtHex.upper() if ndSelf.isUpperHex else txtHex)
        tup_hsv = Color(ndSelf.colA[:3]).hsv
    else:
        tup_rgbByte = tuple(map(lambda x: int(x*255), ndSelf.col))
        ndSelf.soldTxtRgbByte = "R:{} G:{} B:{}".format(*tup_rgbByte)
        txtPrec = str(ndSelf.precisionLyNums)
        ndSelf.soldTxtRgbFloat = "r:{:.&} g:{:.&} b:{:.&}".replace("&", txtPrec).format(*ndSelf.col).replace("0.", ".").replace("1.0", "1.")
        muv = 2*ndSelf.isReverseHex
        txtHex = hex(tup_rgbByte[abs(muv-2)]+tup_rgbByte[abs(muv-1)]*256+tup_rgbByte[abs(muv)]*65536)[2:]
        ndSelf.soldTxtHex = f"Hex-{'bgr' if muv else 'rgb'}:"+ndSelf.txtHexPrefixReplace+(txtHex.upper() if ndSelf.isUpperHex else txtHex)
        tup_hsv = Color(ndSelf.col).hsv
    ndSelf.soldTxtHsvNum = "H:{:.&f}° S:{:.&f}% V:{:.&f}%".replace("&", str(int(txtPrec)-2)).format(tup_hsv[0]*360, tup_hsv[1]*100, tup_hsv[2]*100)
    ndSelf.soldTxtHsvFloat = "h:{:.&} s:{:.&} v:{:.&}".replace("&", txtPrec).format(*tup_hsv)
def NcnUpdateReadOnly(ndSelf, _context):
    assert tuple(ndSelf.col)==tuple(ndSelf.colGamm)
    assert tuple(ndSelf.colA)==tuple(ndSelf.colAGamm)
    ndSelf.col4SoldReadOnly = ndSelf.colA
def NcnUpdateAlpha(ndSelf, context):
    if ndSelf.isAlpha:
        for cyc in range(3):
            ndSelf.colA[cyc] = ndSelf.col[cyc]
            ndSelf.colAGamm[cyc] = ndSelf.colGamm[cyc]
    else:
        ndSelf.col = ndSelf.colA[:3]
        ndSelf.colGamm = ndSelf.colAGamm[:3]
    NcnUpdateColor(ndSelf, context)
class NodeColorNote(ManagerNodeRoot):
    nclass = 33#2
    bl_idname = 'MngNodeColorNote'
    bl_label = "Color Note"
    bl_width_max = 512
    bl_width_min = 140
    bl_width_default = 200
    mngCategory = 'Color'
    isAlpha: bpy.props.BoolProperty(name="Alpha", default=True, update=NcnUpdateAlpha)
    isGamma: bpy.props.BoolProperty(name="Gamma", default=True, update=NcnUpdateColor)
    col: bpy.props.FloatVectorProperty(name="Color", size=3, soft_min=0, soft_max=1, subtype='COLOR', update=NcnUpdateColor)
    colA: bpy.props.FloatVectorProperty(name="ColorAlpha", size=4, soft_min=0, soft_max=1, subtype='COLOR', update=NcnUpdateColor)
    colGamm: bpy.props.FloatVectorProperty(name="ColorGamm", size=3, soft_min=0, soft_max=1, subtype='COLOR_GAMMA', update=NcnUpdateColor)
    colAGamm: bpy.props.FloatVectorProperty(name="ColorAlphaGamm", size=4, soft_min=0, soft_max=1, subtype='COLOR_GAMMA', update=NcnUpdateColor)
    col4SoldReadOnly: bpy.props.FloatVectorProperty(size=4, soft_min=0, soft_max=1, subtype='COLOR', update=NcnUpdateColor)
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
        row.prop(self,self.GetCurColAtt(), text="")
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
            rowCol.prop(self,self.GetCurColAtt(), text="", emboss=self.isClassicLy) #emboss==False для color prop -- это потрясающе!!
            rowCol.scale_y = 0.5*self.decorHeight
        colList = colLy.column()
        for att in ("RgbByte", "RgbFloat", "HsvNum", "HsvFloat", "Hex"):
            if getattr(self,"isLy"+att):
                row = colList.row(align=True)
                row.alignment = 'CENTER'
                if self.isLySubstrate:
                    row = row.box().row()
                    row.scale_y = 0.5
                uu_ly.LyHighlightingText(row, *re.split("(?<= )|:", getattr(self, "soldTxt"+att)))


def NcqpUpdateGamma(ndSelf, _context):
    ndSelf['colP'] = tuple(map(lambda x: x**(1/ndSelf.gamma), ndSelf.col))
    ndSelf['colN'] = tuple(map(lambda x: x**ndSelf.gamma, ndSelf.col))
    ndSelf['colGP'] = ndSelf.colP
    ndSelf['colGN'] = ndSelf.colN
    ndSelf['colG'] = ndSelf.col
for chIsG in ("", "G"):
    for chSide in "PN":
        exec(f"def NcqpUpdateGamma{chIsG}{chSide}(ndSelf, _context): ndSelf.col = tuple(map(lambda x: x**({'1/'*(chSide=='N')}ndSelf.gamma), ndSelf.col{chIsG}{chSide}))")
def NcqpUpdateGammaG(ndSelf, _context):
    ndSelf.col = ndSelf.colG
class NodeColorQuickGamma(ManagerNodeRoot):
    nclass = 33
    bl_idname = 'MngNodeColorQuickGamma'
    bl_label = "Color Quick Gamma"
    bl_width_max = 400
    bl_width_min = 140
    bl_width_default = 140
    mngCategory = 'Color'
    gamma: bpy.props.FloatProperty(name="Gamma", default=2.2, min=1.0, soft_max=6.0, precision=3, subtype='FACTOR', update=NcqpUpdateGamma)
    decorHeight: bpy.props.IntProperty(name="Decor Height", default=2, min=2, max=12, soft_max=6)
    for chIsG in ("", "G"):
        for chSide in " PN":
            exec(f"col{chIsG}{chSide}: bpy.props.FloatVectorProperty(name=\"Color\", size=4, soft_min=0, soft_max=1, subtype='{'COLOR_GAMMA' if chIsG else 'COLOR'}', update=NcqpUpdateGamma{chIsG}{chSide})")
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

def NqleDoExec(exc, *, dict_vars={}):
    exec(exc, {'bpy':bpy, 'C':bpy.context, 'D':bpy.data}|dict_vars, None)
def NqleNdDoExecFromCache(nd, *, dict_vars={}):
    if cache:=dict_nqleNdCompileCache[nd]:
        NqleDoExec(cache, dict_vars=dict_vars)

class NqleOp(bpy.types.Operator):
    bl_idname = 'mng.op_nqle'
    bl_label = "NqleOp"
    bl_options = {'UNDO'}
    opt: bpy.props.StringProperty()
    repr: bpy.props.StringProperty()
    evl: bpy.props.StringProperty()
    def execute(self, _context):
        ndRepr = eval(self.repr)
        match self.opt:
            case 'LocExec':
                if self.evl:
                    NqleDoExec(eval(self.evl))
            case 'GlbExec':
                dict_nqleNdCompileCache[ndRepr] = NqleGetCacheCompiled(ndRepr)
                NqleNdDoExecFromCache(ndRepr)
        return {'FINISHED'}

def NqleUpdateReCompileRaw(self, _context):
    dict_nqleNdIsCached[dict_nqleSelfSelfToNode[self]] = False
class NqleLineItem(bpy.types.PropertyGroup):
    isActive:  bpy.props.BoolProperty(name="Active",     default=True,        update=NqleUpdateReCompileRaw)
    isTb:      bpy.props.BoolProperty(name="Toggle",     default=False,       update=NqleUpdateReCompileRaw)
    tbPoi:  bpy.props.PointerProperty(name="Text Block", type=bpy.types.Text, update=NqleUpdateReCompileRaw)
    txtExec: bpy.props.StringProperty(name="Text Exec",  default="",          update=NqleUpdateReCompileRaw)

dict_nqleNdCompileCache = {}
dict_nqleNdIsCached = {}
dict_nqleSelfSelfToNode = {}

def NqleGetCacheCompiled(nd):
    txtAcmExec = ""
    for ci in nd.lines:
        if ci.isActive:
            if ci.isTb:
                if ci.tbPoi:
                    txtAcmExec += ci.tbPoi.as_string()+"\n"
            else:
                txtAcmExec += ci.txtExec+"\n"
    return compile(txtAcmExec, "", 'exec')

def NqleUpdateCount(ndSelf, _context):
    len = length(ndSelf.lines)
    for cyc in range(len, ndSelf.count):
        ci = ndSelf.lines.add()
        ci.name = str(cyc)
        dict_nqleSelfSelfToNode[ci] = ndSelf #Для InitNode().
    for cyc in reversed(range(ndSelf.count, len)):
        if not(ndSelf.lines[cyc].txtExec and ndSelf.lines[cyc].tbPoi):
            ndSelf.lines.remove(cyc)
    ndSelf['count'] = length(ndSelf.lines) #nqleIsCountUpdating
    #Заметка: поскольку изменение количетсва добавляет и удаляет только пустые, в перекомплияции нет нужды.
def NqleUpdateMethod(ndSelf, _context):
    ndSelf.soldIsAsExc = ndSelf.method=='EXEC'
class NodeQuickLayoutExec(ManagerNodeRoot):
    nclass = 8
    bl_idname = 'MngNodeQuickLayoutExec'
    bl_label = "Quick Layout Exec"
    bl_width_max = 2048
    bl_width_min = 64
    bl_width_default = 750
    mngCategory = 'Script'
    lines: bpy.props.CollectionProperty(type=NqleLineItem)
    method: bpy.props.EnumProperty(name="Method", default='LAYOUT', items=( ('LAYOUT',"As Layout",""), ('EXEC',"As Exec","") ), update=NqleUpdateMethod)
    soldIsAsExc: bpy.props.BoolProperty()
    count: bpy.props.IntProperty(name="Count of lines", default=1, min=0, max=32, soft_min=1, soft_max=6, update=NqleUpdateCount)
    isCaching: bpy.props.BoolProperty(name="Caching", default=True)
    isOnlyLy: bpy.props.BoolProperty(name="Layout display only", default=False)
    decorExec: bpy.props.StringProperty(name="Decor Exec button", default="Exec")
    visibleButtons: bpy.props.IntProperty(name="Visibility of buttons", default=7, min=0, max=7)
    def DrawLabel(self):
        return "Quick Exec" if self.soldIsAsExc else "Quick Layout"
    def InitNode(self, _context):
        self.method = self.bl_rna.properties['method'].default
        self.count = 3
        self.lines[0].txtExec = "txt = \"Hello_World\""
        self.lines[1].txtExec = "ly.label(text=str(txt))"
        self.lines[2].txtExec = "#bpy.ops.node.add_node('INVOKE_DEFAULT', type=C.node.lines[0].txtExec.replace(\"#\", \"\"), use_transform=True)"
    def LyDrawExtNode(self, _context, colLy, _prefs):
        colList = colLy.column(align=True)
        colList.row().prop(self,'method', expand=True)
        colList.prop(self,'count')
        if self.soldIsAsExc:
            uu_ly.LyNiceColorProp(colList, self,'decorExec', text="Decor Exec:", align=True)
        else:
            colList.prop(self,'isCaching')
        colList.prop(self,'isOnlyLy')
        row = colList.row(align=True)
        row.prop(self,'visibleButtons')
        row.active = not self.isOnlyLy
    def LyDrawNode(self, _context, colLy, _prefs):
        for ci in self.lines:
            dict_nqleSelfSelfToNode[ci] = self
        if not self.isOnlyLy:
            colLines = colLy.column(align=True)
            for ci in self.lines:
                rowLine = colLines.row().row(align=True)
                rowEnb = rowLine.row(align=True)
                if self.visibleButtons%2:
                    rowEnb.prop(ci,'isActive', text="")
                rowEnb.active = False
                rowTb = rowLine.row(align=True)
                tgl = (ci.isTb)and(not ci.txtExec)or not(ci.isTb or not ci.tbPoi)
                if self.visibleButtons//2%2:
                    rowTb.prop(ci,'isTb', text="", icon='WORDWRAP_OFF', emboss=True, invert_checkbox=tgl) #RIGHTARROW  GREASEPENCIL  WORDWRAP_OFF  ALIGN_JUSTIFY
                rowTb.active = False
                if (self.soldIsAsExc)and(self.visibleButtons//4%2):
                    row = rowLine.row(align=True)
                    fit = repr(ci.txtExec) if not ci.isTb else repr(ci.tbPoi)+".as_string()" if ci.tbPoi else ""
                    row.operator_props(NqleOp.bl_idname, text="", icon='TRIA_RIGHT', opt='LocExec', repr=repr(self), evl=fit)
                    row.active = not(ci.isTb and not ci.tbPoi)
                if ci.isTb:
                    rowLine.prop(ci,'tbPoi', text="", icon='TEXT')
                else:
                    rowLine.prop(ci,'txtExec', text="", icon='SCRIPT')
                rowLine.active = ci.isActive
        if self.soldIsAsExc:
            if self.decorExec:
                colLy.operator_props(NqleOp.bl_idname, text=self.decorExec, opt='GlbExec', repr=repr(self))
        else:
            with uu_ly.TryAndErrInLy(colLy):
                if not( (self.isCaching)and(self in dict_nqleNdIsCached)and(dict_nqleNdIsCached[self]) ):
                    dict_nqleNdCompileCache[self] = NqleGetCacheCompiled(self)
                    dict_nqleNdIsCached[self] = True
                NqleNdDoExecFromCache(self, dict_vars={'ly': colLy})

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
    mngCategory = 'Hacking'
    idTag: bpy.props.IntProperty(name="Tag", default=0, min=0, max=17, update=NntUpdateTagId)
#    def InitNode(self, _context):
#        self.select = False
    def LyDrawNode(self, context, colLy, _prefs):
        ndAc = context.space_data.edit_tree.nodes.active
        uu_ly.LyBoxAsLabel(colLy, text=ndAc.bl_label if ndAc else "Active node is None", icon='NODE', active=not not ndAc, alignment='LEFT')
        if ndAc:
            tup_item = ConvNclassTagNameId.tup_сonvertTagName[self.idTag]
            nclass = opa.BNode(ndAc).typeinfo.contents.nclass
            if tup_item[0]!=nclass:
                bpy.app.timers.register(functools.partial(NntTimerSetTagId, self, nclass))
            colLy.prop(self,'idTag', text=f"{tup_item[0]}  —  {tup_item[1]}", slider=True) #-- – —

def Prefs():
    return bpy.context.preferences.addons[bl_info['name']].preferences

class AddonPrefs(AddonPrefs):
    def draw(self, context):
        colLy = self.layout.column()

def RecrGetHierSubclasses(cls):
    list_result = [cls]
    for li in cls.__subclasses__():
        list_result.extend(RecrGetHierSubclasses(li))
    return list_result

set_mngNodeClasses = set()
for li in RecrGetHierSubclasses(ManagerNodeRoot):
    if hasattr(li, 'bl_idname'):
        set_mngNodeClasses.add(li)
        assert hasattr(li, 'mngCategory')
        dict_catAdds.setdefault(li.mngCategory, []).append(li)
set_mngNodeBlids = set(si.bl_idname for si in set_mngNodeClasses)


uu_regutils.BringRegToFront(rud, globals(), 'AddonPrefs')

def register():
    uu_regutils.LazyRegAll(rud, globals())
    GenAmnUnfs(Prefs())
def unregister():
    uu_regutils.UnregFromLazyRegAll(rud)

if __name__=="__main__":
    register()