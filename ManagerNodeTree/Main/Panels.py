import bpy, re
from .Prefs import Prefs

from . import Nodes
from .Utils import OpSimpleExec
from .Presets import PrstUtltExmp
from ..uu_ly import LyNiceColorProp

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
        for li in Nodes.list_catAdds:
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
            assert False, "CreateUnfs()"
            import functools
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
        for li in Nodes.list_catAdds:
            list_found = self.PreScan(patr, li[1], LKey=lambda a:a.bl_label)
            if suInda:
                list_found = [li for li in list_found if not li.possibleDangerousGradation] #ClsNodeIsRegistered(li)
            if (list_found)and(colListItems:=self.LyCatAddIndUnfAuto(colListCats, li[0], prefs, anyway=not not patr)):
                for cls in list_found:
                    rowOp = self.LyAddItem(colListItems, text=cls.bl_label, icon=getattr(cls,'bl_icon', 'NONE'))
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
class PamnUnfuril(bpy.types.PropertyGroup): #"discl" со своим "sure", "closure", и "dis", слишком не годились; пришлось заменить на модифицированный "Unfurl" (у которого "url" тоже так-себе).
    unf: bpy.props.BoolProperty(name="Unfurl", default=False) # Ещё был вариант с "reveal", но уже поздно; к тому же предыдущий ближе по смыслу.
Wh.AddonProps.pamnFilter = bpy.props.StringProperty(name="Filter", default="")
Wh.AddonProps.pamnUnfurils = bpy.props.CollectionProperty(type=PamnUnfuril)
Wh.txt_regApResetToDefault += " pamnFilter pamnUnfurils"

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
        for li in PrstUtltExmp.list_catPue:
            prefs.pamnUnfurils.add().name = li[0]
    def draw(self, context):
        colLy = self.layout.column()
        prefs = Prefs()
        colLy.prop(prefs,'pspaeFilter', text="", icon='SORTBYEXT' if prefs.pspaeFilter else 'NONE')
        colListCats = colLy.column()
        patr = re.compile(prefs.pspaeFilter) if prefs.pspaeFilter else None
        for li in PrstUtltExmp.list_catPue:
            list_found = PanelAddManagerNode.PreScan(patr, li[1])
            if (list_found)and(colListItems:=PanelAddManagerNode.LyCatAddIndUnfAuto(colListCats, li[0], prefs, anyway=not not patr)):
                for li in list_found:
                    rowOp = PanelAddManagerNode.LyAddItem(colListItems, text=li)
                    fit = f"from .Utils import *; from .Presets import PrstUtltExmp; GenPlaceNodesToCursor(bpy.context, getattr(PrstUtltExmp, {repr(li)}), isActiveFromList=True)"
                    rowOp.operator(OpSimpleExec.bl_idname, text="", icon='FRAME_PREV').exc = fit #BACK  FRAME_PREV  REW  PLAY_REVERSE
Wh.AddonProps.pspaeFilter = bpy.props.StringProperty(name="Filter", default="")
#Вместо pspaeUnfurils используются pamnUnfurils.
Wh.txt_regApResetToDefault += " pspaeFilter"

class PanelManagerTreeActiveNode(bpy.types.Panel):
    bl_idname = 'MNG_PT_ManagerTreeActiveNode'
    bl_label = "Manager Active Node"
    bl_space_type = 'NODE_EDITOR'
    bl_region_type = 'UI'
    bl_category = "Mng"
    bl_order = 1
    @classmethod
    def poll(cls, context):
        tree = context.space_data.edit_tree
        return (tree)and(ndAc:=tree.nodes.active)and(ndAc.__class__ in Nodes.set_mngNodeClasses)
    def draw(self, context):
        colLy = self.layout.column()
        ndAc = context.space_data.edit_tree.nodes.active
        col = colLy.column(align=True)
        col.prop(ndAc,'name', text="", icon='NODE')
        row = col.row(align=True)
        row.prop(ndAc,'width', slider=True)
        row.active = False
        ndAc.draw_buttons_ext(context, colLy)

Wh.Lc(*globals().values())