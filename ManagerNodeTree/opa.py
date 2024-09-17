#24.09.10 by ugorek

import bpy, ctypes, platform

class Structs(ctypes.Structure):
    list_subclasses = []
    def __init_subclass__(cls):
        cls.list_subclasses.append(cls)
    @staticmethod
    def InitStructs():
        typeFunc = type(lambda: None)
        for cls in Structs.list_subclasses:
            list_fields = []
            for dk, dv in cls.__annotations__.items():
                if isinstance(dv, typeFunc):
                    dv = dv()
                list_fields.append((dk, dv))
            if list_fields:
                cls._fields_ = list_fields
            cls.__annotations__.clear()
        Structs.list_subclasses.clear()
    ##
    def __getattribute__(self, att):
        result = object.__getattribute__(self, att)
        return result.contents if result.__class__.__name__.startswith("LP_") else result
    @classmethod
    def GetFields(cls, ess):
        return cls.from_address(ess.as_pointer())

from ctypes import (c_void_p as void_p,
                    c_uint32 as uint32,
                    c_short  as short,
                    c_int16  as int16,
                    c_int    as int,
                    c_float  as float,
                    c_char   as char)

#\source\blender\blenkernel\BKE_node_runtime.hh
class BNodeSocketRuntime(Structs):
    if platform.system()=='Windows':
        _pad0:        char*8
    declaration:  void_p
    changed_flag: uint32
    total_inputs: short
    _pad1:        char*2
    location:     float*2
    ...

#\source\blender\makesdna\DNA_node_types.h
class BNodeStack(Structs):
    vec:        float*4
    min:        float
    max:        float
    data:       void_p
    hasinput:   short
    hasoutput:  short
    datatype:   short
    sockettype: short
    is_copy:    short
    external:   short
    _pad:       char*4
class BNodeSocket(Structs):
    next:                   lambda: ctypes.POINTER(BNodeSocket)
    prev:                   lambda: ctypes.POINTER(BNodeSocket)
    prop:                   void_p
    identifier:             char*64
    name:                   char*64
    storage:                void_p
    type:                   short
    flag:                   short
    limit:                  short
    in_out:                 short
    typeinfo:               void_p
    idname:                 char*64
    default_value:          void_p
    _pad:                   char*4
    label:                  char*64
    description:            char*64
    if (bpy.app.version>=(4,0,0))and(bpy.app.version_string!="4.0.0 Alpha"):
        short_label:            char*64
    default_attribute_name: ctypes.POINTER(char)
    to_index:               int
    link:                   void_p
    ns:                     BNodeStack
    runtime:                ctypes.POINTER(BNodeSocketRuntime)

#\source\blender\blenkernel\BKE_node.hh
class BNodeType(Structs):
    idname:         char*64
    type:           int
    ui_name:        char*64
    ui_description: char*256
    ui_icon:        int
    if bpy.app.version>=(4,0,0):
        char:           void_p
    width:          float
    minwidth:       float
    maxwidth:       float
    height:         float
    minheight:      float
    maxheight:      float
    nclass:         int16
    ...

#\source\blender\makesdna\DNA_node_types.h
class BNode(Structs):
    next:       lambda: ctypes.POINTER(BNode)
    prev:       lambda: ctypes.POINTER(BNode)
    inputs:     void_p*2
    outputs:    void_p*2
    name:       char*64
    identifier: int
    flag:       int
    idname:     char*64
    typeinfo:   ctypes.POINTER(BNodeType)
    type:       int16
    ui_order:   int16
    custom1:    int16
    custom2:    int16
    custom3:    float
    custom4:    float
    id:         void_p
    storage:    void_p
    prop:       void_p
    parent:     void_p
    if bpy.app.version_string=="4.3.0 Alpha":
        pad:        void_p  #Выяснено опытным путём; в файле его не нашёл. Понятия не имею, что это может быть.
    locx:       float
    locy:       float
    width:      float
    height:     float
    offsetx:    float
    offsety:    float
    label:      char*64
    color:      float*3
    ...

#\source\blender\makesdna\DNA_vec_types.h
class Rctf(Structs):
    xmin: float
    xmax: float
    ymin: float
    ymax: float
class Rcti(Structs):
    xmin: int
    xmax: int
    ymin: int
    ymax: int

#\source\blender\makesdna\DNA_view2d_types.h
class View2D(Structs):
    tot:       Rctf
    cur:       Rctf
    vert:      Rcti
    hor:       Rcti
    mask:      Rcti
    min:       float*2
    max:       float*2
    minzoom:   float
    maxzoom:   float
    scroll:    short
    scroll_ui: short
    keeptot:   short
    keepzoom:  short
    ...

Structs.InitStructs()

for dk, dv in dict(globals()).items():
    if getattr(dv,'__module__', "")==__name__:
        if dk!="Structs":
            globals()[dk] = dv.GetFields

for li in dir(Structs):
    if not li.startswith("_"):
        delattr(Structs, li)
del Structs