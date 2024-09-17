import bpy
from . import Bases

from .. import Utils
from ...uu_ly import LyNiceColorProp

class ManagerNodeNote(Bases.ManagerNodeRoot):
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
        LyNiceColorProp(colLy, self,'body') #colLy.prop(self,'body')
    def LyDrawNode(self, _context, colLy, _prefs):
        colLy.prop(self,'body', text="")

class NodeNote(ManagerNodeNote, Bases.ManagerNodeProtected):
    bl_idname = 'MngNodeNote'
    bl_label = "Note"
    bl_width_min = 140
    mngCategory = "0Text", 1
    note: bpy.props.StringProperty(name="Note body", default="")
    isLyReadOnly: bpy.props.BoolProperty(name="Read only", default=False)
    isLyCenter: bpy.props.BoolProperty(name="Center", default=False)
    decorIcon: bpy.props.StringProperty(name="Icon", default='NONE', update=Utils.UpdateDecorIcon)
    decorIsActive: bpy.props.BoolProperty(name="Active", default=True)
    decorIsAlert: bpy.props.BoolProperty(name="Alert", default=False)
    decorPlaceholder: bpy.props.StringProperty(name="Placeholder", default="Note")
    def InitNode(self, _context):
        self.decorIcon = "OUTLINER_DATA_GP_LAYER"
    def DrawLabel(self):
        return self.note if self.hide else self.bl_label
    def LyDrawExtNode(self, _context, colLy, _prefs):
        LyNiceColorProp(colLy, self,'note', text="Text:", align=True) #colLy.prop(self,'note', text="")
        colLy.prop(self,'isLyReadOnly')
        row = colLy.row()
        row.prop(self,'isLyCenter')
        row.active = self.isLyReadOnly
        colLy.prop(self,'decorIsActive')
        colLy.prop(self,'decorIsAlert')
        LyNiceColorProp(colLy, self,'decorIcon')
        LyNiceColorProp(colLy, self,'decorPlaceholder')
    def LyDrawNode(self, _context, colLy, _prefs):
        if self.decorIcon not in Utils.set_allIcons:
            Utils.LyInvalidDecorIcon(colLy, self)
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
            colLy.prop(self,'note', text="", icon=self.decorIcon, placeholder=self.decorPlaceholder)

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
class NnpLine(Utils.PgNodeCollectionItemWithGetNdSelf):
    body: bpy.props.StringProperty(name="Body", default="", update=NnpUpdateLineBody)
class NodeNotepad(ManagerNodeNote, Bases.ManagerNodeProtected):
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
    decorHeightScale: bpy.props.FloatProperty(name="Height scale", default=1.0, min=0.5, max=1.5)
    decorVars: bpy.props.IntProperty(name="Decor", default=4, min=0, max=15)
    def RestoreNewFromFree(self, ndNew):
        ndNew.lines.clear()
        for ci in self.lines:
            ciNew = ndNew.lines.add()
            ciNew.name = ci.name
            ciNew['body'] = ci.body
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
        LyNiceColorProp(row, self,'decorLineAlignment')
        row.active = (self.count>1)and(not self.isLyReadOnly)
        colList.prop(self,'decorIncludeNumbering')
        colList.prop(self,'decorHeightScale')
        colList.prop(self,'decorVars')
    def LyDrawNode(self, _context, colLy, _prefs):
        colLines = colLy.column(align=self.decorLineAlignment!='GAP')
        colLines.scale_y = self.decorHeightScale
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

Wh.Lc(*globals().values())