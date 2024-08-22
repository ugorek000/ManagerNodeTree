#24.06.02 by ugorek

from builtins import len as length

##

txtDoc = f'''Utility from "{__name__}.py" module'''

import bpy

def prop_inac(self, *args, **kw_args):
    self.prop(*args, **kw_args)
    self.active = False
bpy.types.UILayout.prop_inac = prop_inac #Гениально. Но юзабельно в основном с внешним ly.ly(stuff).prop_inac().
prop_inac.__doc__ = txtDoc

def operator_props(self, operator, text="", text_ctxt="", translate=True, icon='NONE', emboss=True, depress=False, icon_value=0, **kw_args):
    op = self.operator(operator, text=text, text_ctxt=text_ctxt, translate=translate, icon=icon, emboss=emboss, depress=depress, icon_value=icon_value)
    for dk, dv in kw_args.items():
        setattr(op, dk.lstrip("_"), dv)
    #return op
bpy.types.UILayout.operator_props = operator_props
operator_props.__doc__ = txtDoc

def prop_and_get(self, who, prop, **kw_args):
    self.prop(who, prop, **kw_args)
    return getattr(who, prop)
bpy.types.UILayout.prop_and_get = prop_and_get
prop_inac.__doc__ = txtDoc

##

import time

class UserConfirmAlert:
    secsLeft = property(lambda a: a.time+a.limit-time.perf_counter())
    isFinal = property(lambda a: a.secsLeft<0.0) #property(lambda a: time.perf_counter()>a.time+a.limit)
    count = property(lambda a: a.depth-1) #Или гениально, или кривая топология.
    def __init__(self, limit):
        self.depth = 0 #Количество нажатий.
        self.time = 0.0
        self.limit = limit
    def Done(self):
        self.depth = 0

dict_userConfirmAlert = {} #Заметка: Если в процессе алерта произойдёт импорт этого модуля где-то, то все алерты потеряются. Повезло, что ущерб от этого околонулевой.

def ProcConfirmAlert(essKey, limit=None):
    if limit is None:
        if uca:=dict_userConfirmAlert.get(essKey, None):
            if uca.isFinal:
                uca.depth = 0 #Заметка: Очевидное -- важно обнулять для последующих кликов.
                return False
            return uca.depth
        return False
    else:
        uca = dict_userConfirmAlert.setdefault(essKey, UserConfirmAlert(limit))
        if limit>0.0:
            uca.depth += 1
            uca.time = time.perf_counter()
            return uca.count
        else:
            uca.Done()
            return None

#Заметка: Если в названии есть Add -- функция возвращает макет.

def LyBoxAsLabel(where, *, text, icon, active=True, alignment='CENTER'):
    box = where.box()
    row = box.row(align=True)
    row.alignment = alignment
    row.label(text=text, icon=icon)
    row.active = active
    box.scale_y = 0.5
def LyAddHeaderedBox(where, *, text, icon, active=True):
    col = where.column(align=True)
    if txt:
        LyBoxAsLabel(col, text=text, icon=icon, active=active, alignment=alignment)
    return col.box()

import rna_keymap_ui
def LySimpleKeyMapList(context, where, kmU, set_opBlids):                 #todo элементы прилипают к заголовку, добавить промежуток
    #import rna_keymap_ui
    colMain = where.column(align=True)
    #colMain.separator()
    rowLabelRoot = colMain.row(align=True)
    rowLabelText = rowLabelRoot.row(align=True)
    rowLabelText.alignment = 'LEFT'
    rowLabelText.label(icon='DOT')
    rowLabelText.label(text=kmU.name)
    rowLabelPost = rowLabelRoot.row(align=True)
    rowLabelPost.active = False
    if kmU.is_user_modified:
        rowRestore = rowLabelRoot.row(align=True)
        rowRestore.context_pointer_set('keymap', kmU)
        rowRestore.operator('preferences.keymap_restore', text="Restore")
    colList = colMain.row().column(align=True)
    sco = 0
    for li in reversed(kmU.keymap_items):
        if li.idname in set_opBlids:
            colList.context_pointer_set('keymap', kmU)
            rna_keymap_ui.draw_kmi([], context.window_manager.keyconfigs.user, kmU, li, colList, 0)
            sco += 1
    rowLabelPost.label(text=f"({sco})")

import traceback
class TryAndErrInLy():
    def __init__(self, where):
        self.ly = where
    def __enter__(self):
        return self.ly
    def __exit__(self, type, value, tb):
        if type: #any((type, value, tb))
            row = self.ly.row(align=True)
            row.label(icon='ERROR')
            col = row.column(align=True)
            for li in traceback.format_exc().split("\n")[:-1]:
                col.label(text=li)

def LyNiceColorProp(where, ess, prop, *, align=False, text="", scale=0.0, decor=3):
    rowCol = where.row(align=align)
    rowLabel = rowCol.row()
    rowLabel.alignment = 'LEFT'
    rowLabel.label(text=text if text else ess.bl_rna.properties[prop].name+":")
    rowLabel.active = decor%2
    rowProp = rowCol.row()
    rowProp.alignment = 'LEFT' if scale else 'EXPAND'
    rowProp.scale_x = scale
    rowProp.prop(ess, prop, text="")
    rowProp.active = decor//2%2

def LyHighlightingText(where, *args_txt):
    rowRoot = where.row(align=True)
    for cyc, txt in enumerate(args_txt):
        if txt:
            row = rowRoot.row(align=True)
            row.alignment = 'LEFT'
            row.label(text=txt)
            row.active = cyc%2


def LyAddTemplateTotalRowHh(where, *tupleDataIcos, decor=21, aligns=0):
    box = (where.row() if aligns else where).box()
    box.scale_y = 0.5
    rowMain = box.row(align=True)
    rowTheme = rowMain.row(align=True)
    rowTheme.alignment = 'LEFT'
    rowLabel = rowTheme.row(align=True)
    rowLabel.alignment = 'LEFT'
    dec0 = decor//16%2
    dec1 = 1-decor//32%2
    if (dec1)or(dec0):
        rowLabel.label(text="Total"*dec1+":"*dec0, icon='ASSET_MANAGER' if dec0 else 'NONE')
    rowLabel.active = decor//8%2
    ##
    isAutoCanonTotal = (length(tupleDataIcos)==2)and(length(tupleDataIcos[0])==2)and(length(tupleDataIcos[0])==2)
    type_tuple = type(())
    for cyc, hh in enumerate(tupleDataIcos):
        isTuple = type(hh)==type_tuple
        isMultiTot = (isTuple)and(length(hh)>2)
        if type(hh)!=str:
            rowIco = rowTheme.row(align=True)
            rowIco.label(icon=hh[0] if isTuple else 'RADIOBUT_ON') #RADIOBUT_ON  SNAP_FACE
            rowIco.active = decor//2%2
            row = rowIco.row(align=True)
            row.separator()
            row.scale_y = 0.5
        rowData = rowTheme.row(align=True)
        rowData.alignment = 'LEFT'
        if isMultiTot:
            rowTxt = rowData.row(align=True)
            rowTxt.alignment = 'LEFT'
            rowTxt.label(text=str(hh[1]))
            rowDiv = rowTxt.row(align=True)
            rowDiv.alignment = 'LEFT'
            rowDiv.label(text="/")
            rowDiv.active = False
            rowTxt.label(text=str(hh[2]))
        else:
            rowData.label(text=str(hh[1] if isTuple else hh))
        rowData.active = decor%2
        if (isAutoCanonTotal)and(cyc==0)and(decor//4%2):
            rowDiv = rowTheme.row(align=True)
            rowDiv.alignment = 'LEFT'
            rowDiv.label(text="/")
            rowDiv.active = False
    if aligns==1:
        rowMain.label()
#LyAddTemplateTotalRowHh(ly, ('RADIOBUT_OFF', sco), length(data))


#def LyAddScaledBox(where, scaleY=0.5, scaleX=1.0):
#    box = where.box()
#    box.scale_y = scaleY
#    box.scale_x = scaleX
#    return box
#def LyAddLabelAsBox(where, text, *, icon='NONE', active=True, alignment='EXPAND', alert=False):
#    box = LyAddScaledBox(where)
#    row = box.row(align=True)
#    row.alignment = alignment
#    if icon!='NONE':
#        row.label(icon=icon)
#    row.alert = alert
#    row.label(text=text)
#    row.alert = False
#    row.active = active
#def LyAddLabeledBoxCol(where, label, *, icon='NONE', alert=False):
#    col = where.column(align=True)
#    LyAddLabelAsBox(col, label, icon=icon, alert=alert)
#    return col.box().column()