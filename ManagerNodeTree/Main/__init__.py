import bpy
from . import Reg

if True: #Для защиты от всяких `bpy.types.Node.__repr__ = lambda a: f"||{a.name}||"`, (которые я использовал в своём RANTO для дебага например)
    bpy.types.Node.__mng_repr__ = lambda nd: f"{nd.id_data.__repr__()}.nodes[\"{nd.name}\"]" #Но всё равно пришлось делать вручную, ибо повторные инициализации модуля.
    bpy.types.Node.__mng_repr__.__doc__ = "Backup from "+__name__.split(".")[0]+" addon."
else:
    bpy.types.Node.__mng_repr__ = bpy.types.Node.__repr__
    #В этом случае Node.__repr__ не имеет .__code__, так что не получится 'import types; types.FunctionType(bpy.types.Node.__repr__.__code__, ...)', чтобы изменить __doc__ у копии.

def Register():
    Reg.Register()
def Unregister():
    Reg.Unregister()