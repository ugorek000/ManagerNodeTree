bl_info = {'name':"ManagerNodeTree", 'author':"ugorek",
           'version':(2,5,0), 'blender':(4,2,1), 'created':"2024.09.17",
           'description':"Nodes for special high level managenment", 'location':"NodeTreeEditor > N Panel > Mng",
           'category':"System", 'warning':"!",
           'tracker_url':"https://github.com/ugorek000/ManagerNodeTree/issues", 'wiki_url':"https://github.com/ugorek000/ManagerNodeTree/wiki"}

__builtins__['length'] = len #Спасибо богам Пайтона, за то что это оказалось возможным для простых смертных.

from . import Main

def register():
    Main.Register()
def unregister():
    Main.Unregister()