import bpy

__all__ = ('GenPlaceNodesToCursor', 'GlobalsUtilsInUserExec')

class TryAndPass():
    def __enter__(self):
        pass
    def __exit__(self, *_):
        return True

class OpSimpleExec(bpy.types.Operator): #Бомбезно-гениально удобно!
    bl_idname = 'mng.simple_exec'
    bl_label = "OpSimpleExec"
    bl_options = {'UNDO'}
    exc: bpy.props.StringProperty(name="Exec", default="", options={'SKIP_SAVE'})
    def invoke(self, context, event):
        exec(self.exc, {'bpy':bpy, 'event':event, 'self':self, '__name__':__name__, '__package__':__package__}, {})
        return {'FINISHED'}

dict_mngNdErrorEss = {}

set_allIcons = set(bpy.types.UILayout.bl_rna.functions['prop'].parameters['icon'].enum_items.keys())

dict_typeIdToIcon = {"Actions":'ANIM_DATA', "Armatures":'ARMATURE_DATA', "Brushes":'BRUSH_DATA', "CacheFiles":'FILE_CACHE', "Cameras":'CAMERA_DATA',
                     "Collections":'OUTLINER_COLLECTION', "Curves":'CURVE_DATA', "Fonts":'FONT_DATA', "GreasePencils":'OUTLINER_DATA_GP_LAYER', "HairCurves":'CURVES_DATA',
                     "Images":'IMAGE_DATA', "Lattices":'LATTICE_DATA', "Libraries":'DECORATE_LIBRARY_OVERRIDE', "Probes":'OUTLINER_DATA_LIGHTPROBE', "Lights":'LIGHT_DATA',
                     "LineStyles":'LINE_DATA', "Masks":'IMAGE_ZDEPTH', "Materials":'MATERIAL_DATA', "Meshes":'MESH_DATA', "MetaBalls":'OUTLINER_DATA_META',
                     "MovieClips":'FILE_MOVIE', "NodeTrees":'NODETREE', "Objects":'OBJECT_DATA', "PaintCurves":'VPAINT_HLT', "Palettes":'COLOR', "Particles":'PARTICLE_DATA',
                     "PointClouds":'POINTCLOUD_DATA', "Scenes":'SCENE_DATA', "Screens":'RESTRICT_VIEW_ON', "Sounds":'SOUND', "Speakers":'OUTLINER_DATA_SPEAKER', "Texts":'TEXT',
                     "Textures":'TEXTURE_DATA', "Volumes":'VOLUME_DATA', "WindowManagers":'WINDOW', "WorkSpaces":'WORKSPACE', "Worlds":'WORLD_DATA'}


from random import random as Random
def RandomColor(alpha=1.0):
    return (Random(), Random(), Random(), alpha)

def ClsNodeIsRegistered(cls):
    #return cls.bl_rna.identifier==cls.bl_idname #https://projects.blender.org/blender/blender/issues/127165
    return True #Нужно придумать/найти, как проверить класс на зарегистрированность.

#def ReprStrWithDoubleQuote(txt):
#    return "\""+txt.replace("\\", "\\\\").replace("\"", "\\\"")+"\""


class ConvNclassTagNameId:
    dict_tagToName = {0:"INPUT",    1:"OUTPUT",   2:"none",     3:"OP_COLOR", 4:"OP_VECTOR",  5:"OP_FILTER", 6:"GROUP",     8:"CONVERTER",  9:"MATTE",
                      10:"DISTORT", 12:"PATTERN", 13:"TEXTURE", 32:"SCRIPT",  33:"INTERFACE", 40:"SHADER",   41:"GEOMETRY", 42:"ATTRIBUTE", 100:"LAYOUT"}
    dict_сonvertIdToTag = dict(( (cyc, dk) for cyc, dk in enumerate(dict_tagToName.keys()) ))
    dict_сonvertTagToId = dict(( (dv, dk) for dk, dv in dict_сonvertIdToTag.items() ))
    tup_сonvertTagName = tuple(dict_tagToName.items())
    #for dk, dv in tuple(dict_tagToName.items()):
    #    dict_tagToName[dv] = dk
    del dict_tagToName

def DgConvertReprNdAsDoubleGet(reprNd):
    list_spl = reprNd.split("]")
    return (list_spl[0].replace("[", ".get(")+")", list_spl[0]+"]"+list_spl[1].replace("[", ".get(")+")")
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


def UpdateDecorIcon(self, _context):
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


def GenPlaceNodesToCursor(context, FuncAddNodes, *, isActiveFromList=None):
    def OffsetNodesLocToOrigin(list_nodes, origin):
        from .. import opa
        for nd in list_nodes:
            bNd = opa.BNode(nd)
            bNd.locx += origin[0]
            bNd.locy += origin[1]
    tree = context.space_data.edit_tree
    bpy.ops.node.select_all(action='DESELECT')
    list_addedNodes = FuncAddNodes(tree)
    bpy.ops.wm.redraw_timer(type='DRAW_WIN', iterations=0) #Нужно для cursor_location ниже.
    OffsetNodesLocToOrigin(list_addedNodes, context.space_data.cursor_location)
    bpy.ops.transform.translate('INVOKE_DEFAULT', view2d_edge_pan=True)
    if isActiveFromList is not None:
        tree.nodes.active = list_addedNodes[0] if isActiveFromList else None


from mathutils import Vector
class GlobalsUtilsInUserExec:
    def GetNearestNode(ndDest, *, isByCenter=True, poll=None):
        minLen = 4294967296.0
        ndResult = None
        if isByCenter:
            vecFac = Vector((1.0, -1.0))
        for nd in ndDest.id_data.nodes:
            if (nd!=ndDest)and((not poll)or(poll(nd))):
                if isByCenter:
                    len = ((nd.location+nd.dimensions*vecFac/2.0)-(ndDest.location+ndDest.dimensions*vecFac/2.0)).length
                else:
                    len = (nd.location-ndDest.location).length
                if minLen>len:
                    minLen = len
                    ndResult = nd
        return ndResult