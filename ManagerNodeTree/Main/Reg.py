import bpy

dict_classes = {} #Без дубликатов как set(), но с сохранением порядка; ибо `Wh.Lc(globals())` захватывают так же и from import cls.
txt_regApResetToDefault = ""

class Wh:
    dict_classes = dict_classes
    def Lc(*args):
        assert args
        for ar in args:
            if ar.__class__.__name__ in {"RNAMeta", "RNAMetaPropGroup"}:
                Wh.dict_classes[ar] = True
    class AddonProps:
        def __setattr__(self, att, val):
            self.__annotations__[att] = val
    AddonProps.__annotations__ #Чёрная магия; без этой строчки не работает. Кажется, я где-то упускаю очевидные нюансы Пайтона.
    AddonProps = AddonProps()
    txt_regApResetToDefault = ""#txt_regApResetToDefault

__builtins__['Wh'] = Wh #Без паники; это на время "сборки" аддона.

from . import Tree
from . import Nodes
from . import Panels
from . import Presets
from . import Prefs

del __builtins__['Wh']

Prefs.AddonPrefs.__annotations__ |= Wh.AddonProps.__annotations__
txt_regApResetToDefault = Wh.txt_regApResetToDefault
del Wh

assert Prefs.AddonPrefs in dict_classes
del dict_classes[Prefs.AddonPrefs]
dict_classes[Prefs.AddonPrefs] = True

def Register():
    LegitMark.tgl = True
    def ResetPrefsToDefault(prefs):
        try: debug; return
        except: pass
        for li in txt_regApResetToDefault.split():
            if pr:=prefs.bl_rna.properties.get(li):
                if hasattr(pr,'default_flag'):
                    setattr(prefs, li, pr.default_flag)
                elif hasattr(pr,'default'):
                    setattr(prefs, li, pr.default)
                else:
                    getattr(prefs, li).clear()
    for dk in dict_classes:
        #if dk is Tree.ManagerTree: #Выключено для TimerWaitForBpyDataAndSetNclasses.
        #    continue
        if dk in Nodes.set_mngUnsafeNodeCls:
            continue
        try:
            bpy.utils.register_class(dk)
        except: #class to have an "bl_label" attribute
            pass
    prefs = Prefs.Prefs()
    prefs.isDisclaimerAcceptance = prefs.isDisclaimerAcceptance
    #prefs.isRegisterTreeType = prefs.isRegisterTreeType #Переехало в TimerWaitForBpyDataAndSetNclasses.
    ResetPrefsToDefault(prefs)
    Panels.PanelAddManagerNode.CreateUnfs(prefs)
    Panels.PanelAddManagerNode_SubPresetsAndEx.CreateUnfs(prefs)
    bpy.app.timers.register(TimerWaitForBpyDataAndSetNclasses, persistent=True) #Коли теперь устанавливается только через это, то здесь; а не при инициализации модуля.
    LegitMark.tgl = False
def Unregister():
    LegitMark.tgl = True
    for dk in reversed(dict_classes):
        try:
            bpy.utils.unregister_class(dk)
        except: #missing bl_rna attribute from 'RNAMetaPropGroup' instance (may not be registered)
            pass
    LegitMark.tgl = False

class LegitMark:
    tgl = False

def TimerWaitForBpyDataAndSetNclasses():
    from .. import opa
    def SetNodesNclass():
        tree = bpy.data.node_groups.new("MngTmp", Tree.ManagerTree.bl_idname)
        for si in Nodes.set_mngNodeClasses:
            try:
                nd = tree.nodes.new(si.bl_idname)
            except:
                continue
            opa.BNode(nd).typeinfo.nclass = nd.nclass #Все надежды на самый "надёжный" draw_label() провалились -- см. комментарий о draw_label в ManagerNodeRoot.
            tree.nodes.remove(nd)
        bpy.data.node_groups.remove(tree)
    if bpy.data.__class__.__name__=="BlendData":
        SetNodesNclass()
        prefs = Prefs.Prefs()
        prefs.isRegisterTreeType = prefs.isRegisterTreeType
        return None
    else:
        return 0.05