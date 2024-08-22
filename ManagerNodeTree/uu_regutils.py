#24.03.25 by ugorek

class ModuleData():
    def __init__(self):
        self.list_kmiDefs = []
        self.dict_uniqueClsOfKmisBlid = {}
        ##
        self.kmAddon = None
        self.list_addonKmis = []
        ##
        self.list_lazyRegClasses = []

dict_convertNumKey = {"1":'ONE', "2":'TWO', "3":'THREE', "4":'FOUR', "5":'FIVE', "6":'SIX', "7":'SEVEN', "8":'EIGHT', "9":'NINE', "0":'ZERO',
                      'ONE':"1", 'TWO':"2", 'THREE':"3", 'FOUR':"4", 'FIVE':"5", 'SIX':"6", 'SEVEN':"7", 'EIGHT':"8", 'NINE':"9", 'ZERO':"0"}
def SmartAddToRegAndAddToKmiDefs(rud, cls, txt, active=True, **kwargs): #Eg. "###_ONE"
    rud.list_kmiDefs.append( (cls.bl_idname, dict_convertNumKey.get(txt[4:], txt[4:]), txt[0]=="S", txt[1]=="C", txt[2]=="A", txt[3]=="+", active, kwargs) )
    rud.dict_uniqueClsOfKmisBlid[cls] = cls.bl_idname

def RegKmiDefs(rud, kmAdn):
    assert not rud.kmAddon
    rud.kmAddon = kmAdn
    for blid, key, shift, ctrl, alt, repeat, active, dict_props in rud.list_kmiDefs:
        for kmi in rud.kmAddon.keymap_items:
            if (kmi.idname==blid)and(kmi.type==key)and(kmi.value=='PRESS')and(kmi.shift==shift)and(kmi.ctrl==ctrl)and(kmi.alt==alt)and(kmi.repeat==repeat):
                rud.kmAddon.keymap_items.remove(kmi)
                break
        kmiNew = rud.kmAddon.keymap_items.new(idname=blid, type=key, value='PRESS', shift=shift, ctrl=ctrl, alt=alt, repeat=repeat)
        kmiNew.active = active
        if dict_props:
            for dk, dv in dict_props.items():
                setattr(kmiNew.properties, dk, dv)
        rud.list_addonKmis.append(kmiNew)
def UnregKmiDefs(rud):
    for li in rud.list_addonKmis:
        rud.kmAddon.keymap_items.remove(li)
    rud.list_addonKmis.clear()
    rud.kmAddon = None


def BringRegToFront(rud, dict_globals, att):
    tmp = dict_globals[att]
    del dict_globals[att]
    dict_globals[att] = tmp

def LazyRegAll(rud, dict_globals):
    from bpy.utils import register_class
    if rud.list_lazyRegClasses:
        UnregFromLazyRegAll(rud)
    for dv in dict(dict_globals).values():
        if dv.__class__.__name__ in {"RNAMeta", "RNAMetaPropGroup"}:
            try:
                register_class(dv)
                rud.list_lazyRegClasses.append(dv)
            except:
                pass
def UnregFromLazyRegAll(rud):
    from bpy.utils import unregister_class
    for li in reversed(rud.list_lazyRegClasses):
        unregister_class(li)
    rud.list_lazyRegClasses.clear()


#for li in AddonPrefs.mro():
#    if hasattr(li,'bl_idname'):
#        AddonPrefs.bl_idname = li.bl_idname
#    if hasattr(li,'__annotations__'):
#        AddonPrefs.__annotations__ |= li.__annotations__