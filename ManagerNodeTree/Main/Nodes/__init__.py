from . import Notes
from . import Colors
from . import QuickLayoutExec
from . import NclassToggler
from . import Solemns
from . import Assertor
from . import ConsoleViewers
from . import LayoutAndExec

def RecrGetListAllSubclasses(cls):
    list_result = [cls]
    for li in cls.__subclasses__():
        list_result.extend(RecrGetListAllSubclasses(li))
    return list_result

set_mngNodeClasses = set()
dict_catAdds = {}
for li in set(RecrGetListAllSubclasses(Bases.ManagerNodeRoot)): #Заметка: set для дубликатов из-за множественного наследования ('class NodeNote(ManagerNodeRoot, ManagerNodeProtected)').
    if hasattr(li, 'bl_idname'):
        set_mngNodeClasses.add(li)
        assert hasattr(li, 'mngCategory')
        dict_catAdds.setdefault(li.mngCategory[0], []).append(li)
        globals()[li.__name__] = li
list_catAdds = [(li[0][1:], li[1]) for li in sorted(dict_catAdds.items(), key=lambda a: a[0][0])] #Отсортировать порядок категорий и избавиться от их начальных цифр.
del dict_catAdds
for li in list_catAdds: #Отсортировать ноды в категориях.
    li[1].sort(key=lambda a: a.mngCategory[1])
set_mngUnsafeNodeCls = set()
for si in set_mngNodeClasses:
    if si.possibleDangerousGradation:
        set_mngUnsafeNodeCls.add(si)

del RecrGetListAllSubclasses