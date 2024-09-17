import bpy, re
from .Bases import ManagerNodeRoot

from .. import Utils
from ...uu_ly import LyHighlightingText
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
        setattr(self, 'colGamm' if self.isGamma else 'col', Utils.RandomColor()[:3])
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
        setattr(self, self.GetCurColAtt(), Utils.RandomColor())
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
            LyHighlightingText(row0, *list_spl)
            row0.operator(Utils.OpSimpleExec.bl_idname, text="", icon='COPYDOWN').exc = f"bpy.context.window_manager.clipboard = {repr((txt, ' '.join(list_spl[1::2])))}[1-event.shift]"
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
                LyHighlightingText(row, *re.split("(?<= )|:", getattr(self, "soldTxt"+att)))


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
        self.col = Utils.RandomColor()
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

Wh.Lc(*globals().values())