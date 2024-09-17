import bpy, time, functools
from ... import opa

from ..Prefs import Prefs
from ...uu_ly import LyNiceColorProp
from .. import Utils

class ManagerNodeFiller:
    def InitNodePreChain(self,context):pass
    def InitNode(self,context):pass
    def DrawLabelPreChain(self):return ""
    def DrawLabel(self):return ""
    def LyDrawExtNodePreChain(self,context,colLy,prefs):pass
    def LyDrawExtNode(self,context,colLy,prefs):pass
    def LyDrawNodePreChain(self,context,colLy,prefs):pass
    def LyDrawNode(self,context,colLy,prefs):pass
    def LyDrawNodePostChain(self,context,colLy,prefs):pass
class ManagerNodeRoot(bpy.types.Node, ManagerNodeFiller):
    nclass = 0
    #isNotSetupNclass = True
    possibleDangerousGradation = 0 #0--безопасный  1--возможно опасный  2--имеет Exec или Eval
    @classmethod
    def poll(cls, tree):
        return True
    def init(self, context):
        prefs = Prefs()
        if (self.possibleDangerousGradation)and(prefs)and(not prefs.isDisclaimerAcceptance): #За компанию.
            return
        if context is None:
            context = bpy.context
        self.InitNodePreChain(context)
        self.InitNode(context)
    def draw_label(self): #Важно: Не вызывается, если nd.label!="" и нод свёрнут, но вызывается, если развёрнут.
        #if self.isNotSetupNclass:
        #    opa.BNode(self).typeinfo.nclass = self.nclass
        #    self.__class__.isNotSetupNclass = False
        prefs = Prefs()
        if (self.possibleDangerousGradation)and(prefs)and(not prefs.isDisclaimerAcceptance): #Тоже важно вместе с двумя другими ниже, ибо NodeAssertor.
            return ""
        return self.DrawLabelPreChain() or self.DrawLabel() #"or" без нужды, DrawLabelPreChain слишком редкий.
    def draw_buttons_ext(self, context, layout):
        colLy = layout.column()
        prefs = Prefs()
        if (self.possibleDangerousGradation)and(prefs)and(not prefs.isDisclaimerAcceptance): #Суета с дерегистрациями оказалось лажей -- всё крашится. Поэтому так; до лучших времён.
            return
        self.LyDrawExtNodePreChain(context, colLy, prefs)
        self.LyDrawExtNode(context, colLy, prefs)
    def draw_buttons(self, context, layout):
        #self.draw_label() #Для перерегистраций и других неизвестных "тонких" моментов.
        colLy = layout.column()
        prefs = Prefs()
        if (self.possibleDangerousGradation)and(prefs)and(not prefs.isDisclaimerAcceptance):
            return
        self.LyDrawNodePreChain(context, colLy, prefs)
        self.LyDrawNode(context, colLy, prefs)
        self.LyDrawNodePostChain(context, colLy, prefs)
    def register():
        from .. import Reg
        if not Reg.LegitMark.tgl:
            Reg.TimerWaitForBpyDataAndSetNclasses()
    #def unregister():
    #    from .. import Reg
    #    if not Reg.LegitMark.tgl:
    #        #Жаль здесь нет ссылки на себя
    #        from .. import Nodes
    #        for cls in Nodes.set_mngNodeClasses:
    #            cls.isNotSetupNclass = True


#Флаг ^15 -- nd.use_custom_color
#Флаг ^20 -- lastAlertState; см. в BNdToggleSetCol(col=None).
#Флаг ^21 -- isNowBlinkingAlert; А также активация при запуске .blend.
#Флаг ^22 -- stateBlinkingAlert; Экономить перерисовки.
flagsUccLas = 32768 | 1048576 #1<<15 | 1<<20
def BNdToggleSetCol(bNd, col=None):
    if col is None:
        if bNd.flag&1048576: #1<<20 #Нужно, чтобы при неактивном алерте можно было изменить цвет самого нода при постоянном вызове ProcAlertState. Бесполезно, ибо при активации алерта перезапишется, но всё ради эстетики.
            bNd.flag &= ~flagsUccLas
    else:
        bNd.flag |= flagsUccLas
        bNd.color = col #Выкуси, предупреждение "нельзя писать в рисовании", чтоб тебя.

dict_mngNdBlinkingAlertState = {}
dict_mngNdTimeStartBlinkingAlert = {}
dict_mngNdColInacDurBlk = {}

def MnaDoBlinkingAlert(tns, nd, bNd, *, colInacBlk=None, anyway=False):
    def Rainbow(x, ofs, mul2):
        return max(min(2.0-abs((x+ofs)%6.0-2.0),1.0),0.0)*(1.0 if mul2==2.0 else max(mul2,1.0)%1.0)
    num = int(2_000_000_000-1_750_000_000*(1.0 if nd.alertColor[3]==2.0 else nd.alertColor[3]%1.0))
    col = nd.alertColor[:3]
    if max(col)>1.0:
        fac = (tns/num%3.0)*2.0
        BNdToggleSetCol(bNd, (Rainbow(fac, +2, col[0]), Rainbow(fac, 0, col[1]), Rainbow(fac, -2, col[2])))
        if not anyway:
            nd.label = nd.label
    else:
        if (tns%num)<(num>>1): #Сравнение с первой половиной, чтобы показывать(менять) цвет сразу при активации.
            if (not bNd.flag&4194304)or(anyway): #1<<22
                bNd.flag |= 4194304 #1<<22
                BNdToggleSetCol(bNd, col)
                if not anyway: #Топокостыль, anyway==True использует только рисование.
                    nd.label = nd.label #Изменение заголовка почему-то заставляет перерисовываться все деревья во всех окнах.
        else:
            if (bNd.flag&4194304)or(anyway): #1<<22
                bNd.flag &= ~4194304 #1<<22
                BNdToggleSetCol(bNd, colInacBlk)
                if not anyway:
                    nd.label = nd.label
def MnaProcBlinkingAlert(nd, tns=None, reprNd=None, *, anyway=False): #Вынесено из-за возможности colInacBlk.
    if tns is None:
        tns = time.perf_counter_ns()
    if reprNd is None:
        reprNd = nd.__mng_repr__()
    bNd = opa.BNode(nd)
    if bNd.flag&2097152: #1<<21 #Явная проверка, чтобы не мигать вечно; но не важна, ибо см. else в DrawLabelPreChain, который выключает мигание.
        MnaDoBlinkingAlert(tns-dict_mngNdTimeStartBlinkingAlert[reprNd], nd, bNd, colInacBlk=dict_mngNdColInacDurBlk.get(reprNd), anyway=anyway)
def MnaTimerBlinkingAlert():
    tns = time.perf_counter_ns()
    for dk, nd in Utils.DgCollectEvalDoubleGetFromDict(dict_mngNdBlinkingAlertState):
        MnaProcBlinkingAlert(nd, tns, dk)
    return 0.05 if dict_mngNdBlinkingAlertState else None

def MnaUpdateAlertColor(self, _context):
    self['alertColor'] = self.alertColor[:3]+(0.0 if self.alertColor[3]<0.5 else max(1.0, min(self.alertColor[3], 2.0)),)
class ManagerNodeAlertness(ManagerNodeRoot):
    alertColor: bpy.props.FloatVectorProperty(name="Alert Color", size=4, min=0.0, max=2.0, subtype='COLOR_GAMMA', update=MnaUpdateAlertColor)
    def DelSelfFromDictBlinking(self):
        key = self.__mng_repr__()
        if key in dict_mngNdBlinkingAlertState:
            del dict_mngNdBlinkingAlertState[key]
    def free(self):
        #Так-то идеально, да, но: удалить нод с мигающим алертом; отменить; повторить -- и free() не вызывается. От чего эта процедура в целом бесполезна.
        self.DelSelfFromDictBlinking()
    def DrawLabelPreChain(self):
        ManagerNodeRoot.DrawLabelPreChain(self)
        #Плакала производительность... Ох уж эти CtrlZ'ы и "нельзя писать в рисовании". Но оно того стоило.
        bNd = opa.BNode(self)
        if bNd.flag&2097152: #1<<21
            if key:=Utils.DgProcAddSelfInDictSpec(self, dict_mngNdBlinkingAlertState):
                dict_mngNdTimeStartBlinkingAlert[key] = time.perf_counter_ns()
                if not bpy.app.timers.is_registered(MnaTimerBlinkingAlert):
                    bpy.app.timers.register(MnaTimerBlinkingAlert)
        else:
            self.DelSelfFromDictBlinking()
    def LyDrawExtNodePreChain(self, context, colLy, prefs):
        LyNiceColorProp(colLy, self,'alertColor')
    def ProcAlertState(self, ess, colToAlert=None):
        if colToAlert is None:
            colToAlert = self.alertColor
        bNd = opa.BNode(self)
        if (not self.mute)and(not not ess)and(colToAlert[3]): #У выключенных нод кастомный цвет всё равно не рисуется.
            if colToAlert[3]>1.0:
                if not(bNd.flag&2097152): #1<<21
                    bNd.flag |= 2097152 #1<<21
                    MnaDoBlinkingAlert(0, self, bNd, anyway=True) #Отправляется 0, а не time.perf_counter_ns(), потому что мигания "локальны", см. dict_mngNdTimeStartBlinkingAlert.
                    self.DrawLabelPreChain() #Иначе запуск произойдёт при следующем вызове ManagerNodeAlertness.DrawLabelPreChain(), а нужно сразу.
            else:
                if bNd.flag&2097152: #1<<21
                    bNd.flag &= ~2097152 #1<<21
                    self.DelSelfFromDictBlinking()
                if max(colToAlert[:3])>1.0:
                    colToAlert = RandomColor() #tuple(map(lambda z: z[0] if z[1]==2.0 else z[1]%1.0*z[0], zip(RandomColor(), colToAlert)))
                BNdToggleSetCol(bNd, colToAlert[:3])
        else:
            if bNd.flag&2097152: #1<<21
                bNd.flag &= ~2097152 #1<<21
                self.DelSelfFromDictBlinking()
            BNdToggleSetCol(bNd)


def MnpTimerSetProtectedPoseData(self, bNd):
    self.arrProtectedPoseSoldData[0] = bNd.locx
    self.arrProtectedPoseSoldData[1] = bNd.locy
    self.arrProtectedPoseSoldData[2] = bNd.width
def MnpUpdateIsProtectedPose(self, _context):
    if not self.isProtectedPose:
        self.arrProtectedPoseSoldData = (0.0, 0.0, 0.0)
class ManagerNodeProtected(ManagerNodeRoot):
    isProtectedDel: bpy.props.BoolProperty(name="Protect node from deletion", default=False)
    isProtectedDup: bpy.props.BoolProperty(name="Protect node from duplication", default=False)
    isProtectedPose: bpy.props.BoolProperty(name="Protect node location and size", default=False, update=MnpUpdateIsProtectedPose)
    arrProtectedPoseSoldData: bpy.props.FloatVectorProperty(size=3)
    def RestoreNewFromFree(self, ndNew):
        pass
    def free(self):
        if self.isProtectedDel:
            ndNew = self.id_data.nodes.new(self.bl_idname)
            #ndNew.isProtectedDel = self.isProtectedDel
            for pr in self.bl_rna.properties:
                if not pr.is_readonly:
                    setattr(ndNew, pr.identifier, getattr(self, pr.identifier))
            self.RestoreNewFromFree(ndNew)
            ndNew.select = not "Inf Cycle" #А так же не нулевая реакция на удаление для пользователя.
            self.name += "@"
            ndNew.name = self.name[:-1]
            if self.id_data.nodes.active==self:
                self.id_data.nodes.active = ndNew
    def copy(self, node):
        if self.isProtectedDup:
            node.isProtectedDel = False
            #Заметка: node.id_data==None.
            self.id_data.nodes.remove(node)
    def DrawLabelPreChain(self):
        if self.isProtectedPose:
            bNd = opa.BNode(self)
            if any(self.arrProtectedPoseSoldData):
                bNd.locx = self.arrProtectedPoseSoldData[0]
                bNd.locy = self.arrProtectedPoseSoldData[1]
                bNd.width = self.arrProtectedPoseSoldData[2]
            else:
                bpy.app.timers.register(functools.partial(MnpTimerSetProtectedPoseData, self, bNd))
    def LyDrawExtNodePreChain(self, context, colLy, prefs):
        col = colLy.column(align=True)
        #col.scale_y = 0.9
        col.prop(self,'isProtectedDel')
        col.prop(self,'isProtectedDup')
        col.prop(self,'isProtectedPose')