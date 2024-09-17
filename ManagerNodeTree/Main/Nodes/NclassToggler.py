import bpy, functools
from .Bases import ManagerNodeRoot

from ... import opa
from ..Utils import ConvNclassTagNameId

from ...uu_ly import LyBoxAsLabel

def NntUpdateTagId(self, context):
    opa.BNode(self.id_data.nodes.active).typeinfo.nclass = ConvNclassTagNameId.dict_сonvertIdToTag[self.idTag]
def NntTimerSetTagId(self, num):
    self['idTag'] = ConvNclassTagNameId.dict_сonvertTagToId[num]
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
        LyBoxAsLabel(colLy, text=ndAc.bl_label if ndAc else "Active node is None", icon='NODE', active=not not ndAc, alignment='LEFT')
        if ndAc:
            tup_item = ConvNclassTagNameId.tup_сonvertTagName[self.idTag]
            num = opa.BNode(ndAc).typeinfo.nclass
            if tup_item[0]!=num:
                bpy.app.timers.register(functools.partial(NntTimerSetTagId, self, num))
            colLy.prop(self,'idTag', text=f"{tup_item[0]}  —  {tup_item[1]}", slider=True) #-- – —

Wh.Lc(*globals().values())