import bpy
from .. import uu_ly

class AddonPrefs(bpy.types.AddonPreferences):
    bl_idname = __name__.split(".")[0]


list_mngAlertClause = [False, False]
class MngOpAcceptDisclaimer(bpy.types.Operator):
    bl_idname = 'mng.mng_accept_disclaimer'
    bl_label = "Accept Disclaimer"
    bl_options = {'UNDO'}
    def execute(self, context):
        prefs = Prefs()
        list_mngAlertClause[0] = not prefs.isDisclaimerAcceptanceUserExec
        list_mngAlertClause[1] = not prefs.isDisclaimerAcceptancePossibleDangerous
        if (prefs.isDisclaimerAcceptanceUserExec)and(prefs.isDisclaimerAcceptancePossibleDangerous):
            prefs.isDisclaimerAcceptance = True
        return {'FINISHED'}
def MngUpdateDisclaimerAcceptance(self, _context):
    from . import Nodes
    from . import Reg
    Reg.LegitMark.tgl = True
    for cyc, si in enumerate(Nodes.set_mngUnsafeNodeCls):
        try:
            if self.isDisclaimerAcceptance:
                bpy.utils.register_class(si)
            #else: #А ещё здесь был ClsNodeIsRegistered()...
            #    bpy.utils.unregister_class(si) #План оказался лажа. Также см. проверку isDisclaimerAcceptance в ManagerNodeRoot.
        except:
            pass
    Reg.TimerWaitForBpyDataAndSetNclasses()
    Reg.LegitMark.tgl = False
def MngUpdateDisclaimerClauses(self, _context):
    list_mngAlertClause[0] = False if self.isDisclaimerAcceptanceUserExec else list_mngAlertClause[0]
    list_mngAlertClause[1] = False if self.isDisclaimerAcceptancePossibleDangerous else list_mngAlertClause[1]
class AddonPrefs(AddonPrefs):
    isDisclaimerAcceptance: bpy.props.BoolProperty(default=False, update=MngUpdateDisclaimerAcceptance)
    isDisclaimerAcceptanceUserExec: bpy.props.BoolProperty(name="Disclaimer Acceptance User Exec", default=False, update=MngUpdateDisclaimerClauses)
    isDisclaimerAcceptancePossibleDangerous: bpy.props.BoolProperty(name="Disclaimer Acceptance Possible Dangerous", default=False, update=MngUpdateDisclaimerClauses)
    def LyDrawDisclaimerAcceptance(self, where):
        def LyDisclaimerClause(where, prop, text, *, alert=False):
            row = where.row()
            col = row.column()
            col.alignment = 'CENTER'
            for cyc, txt in enumerate(text.split("\n")):
                col.alert = (alert)and(not cyc)
                col.prop(self, prop, text=txt, icon='BLANK1' if cyc else 'NONE', emboss=not cyc)
            row.alignment = 'CENTER'
        if self.isDisclaimerAcceptance:
            return
        colBox = where.box().column()
        colBox.label(text="To access all nodes, please agree to the disclaimer.")
        colDis = colBox.box().column()
        row = colDis.row()
        row.alignment = 'CENTER'
        row.alert = True
        row.label(text="Disclaimer".upper())
        fit = "The addon has a lot of `exec()` from user input.\nIf you write something wrong, you can make things worse for yourself."
        LyDisclaimerClause(colDis, 'isDisclaimerAcceptanceUserExec', text=fit, alert=list_mngAlertClause[0])
        fit = "The addon has an unknown non-zero risk of (non-zero) data corruption.\nBe careful and make backups."+" "*55
        LyDisclaimerClause(colDis, 'isDisclaimerAcceptancePossibleDangerous', text=fit, alert=list_mngAlertClause[1])
        row = colDis.row()
        row.operator(MngOpAcceptDisclaimer.bl_idname, text="Register unsafe nodes")
        row.active = (self.isDisclaimerAcceptanceUserExec)and(self.isDisclaimerAcceptancePossibleDangerous)


def Prefs():
    return (adn:=bpy.context.preferences.addons.get(__name__.split(".")[0]))and(adn.preferences)

def MngUpdateRegisterTreeType(self, _context):
    from . import Tree
    try: #Что-то я не знаю, как проверить зарегистрированность дерева.
        if self.isRegisterTreeType:
            bpy.utils.register_class(Tree.ManagerTree)
        else:
            bpy.utils.unregister_class(Tree.ManagerTree)
    except:
        pass
class AddonPrefs(AddonPrefs):
    isRegisterTreeType: bpy.props.BoolProperty(name="Register Tree type", default=True, update=MngUpdateRegisterTreeType)
    isAllowNqleWorking: bpy.props.BoolProperty(name="Quick Layout Node is working", default=True)
    isAllowNcWorking: bpy.props.BoolProperty(name="Console Node is working", default=True)
    def draw(self, _context):
        colLy = self.layout.column()
        self.LyDrawDisclaimerAcceptance(colLy)
        colMain = uu_ly.LyAddHeaderedBox(colLy, text="preferences", active=False)
        colMain.prop(self,'isRegisterTreeType')
        if self.isDisclaimerAcceptance:
            colMain.prop(self,'isAllowNqleWorking')
            colMain.prop(self,'isAllowNcWorking')

Wh.Lc(*globals().values())