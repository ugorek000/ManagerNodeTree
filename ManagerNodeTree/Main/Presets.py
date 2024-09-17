from . import Nodes
from . import Utils

class PrstUtltExmp:
    def AddNodeByBlid(tree, meta_cat="3Dev"):
        list_addedNodes = []
        ndNqle = tree.nodes.new(Nodes.NodeQuickLayoutExec.bl_idname)
        list_addedNodes.append(ndNqle)
        ndNqle.width = 360
        ndNqle.name = "AddNodeByBlid"
        ndNqle.label = "Add node by bl_idname"
        ndNqle.method = 'EXEC'
        ndNqle.decorExec = "Add"
        ndNqle.visibleButtons = 7
        ndNqle.lines.clear()
        ndNqle.lines.add().txtExec = "NodeNote"
        ndNqle.lines[-1].isActive = False
        ndNqle.lines.add().txtExec = "bpy.ops.node.add_node('INVOKE_DEFAULT', type=C.node.lines[0].txtExec.replace(\"#\", \"\"), use_transform=True)"
        ndNqle.count = ndNqle.count
        return list_addedNodes
    def DoubleBigExec(tree, meta_cat="0Preset"):
        list_addedNodes = []
        ndNqle0 = tree.nodes.new(Nodes.NodeQuickLayoutExec.bl_idname)
        list_addedNodes.append(ndNqle0)
        ndNqle0.width = 415
        ndNqle0.name = "DoubleBigExec0"
        ndNqle0.label = "Speed up aiming for cursor work by large button size."
        ndNqle0.isShowOnlyLayout = True
        ndNqle0.visibleButtons = 1
        ndNqle1 = tree.nodes.new(Nodes.NodeQuickLayoutExec.bl_idname)
        list_addedNodes.append(ndNqle1)
        ndNqle1.location.y = -140
        ndNqle1.width = 820
        ndNqle1.name = "DoubleBigExec1"
        ndNqle1.label = "Big button's code below"
        ndNqle1.method = 'EXEC'
        ndNqle1.decorExec = ""
        ndNqle1.visibleButtons = 14
        ##
        ndNqle0.lines.clear()
        ndNqle0.lines.add().txtExec = f"ndTar = self.id_data.nodes.get(\"{ndNqle1.name}\")"
        ndNqle0.lines.add().txtExec = "row = ly.row(align=True)"
        ndNqle0.lines.add().txtExec = f"row.operator('{Utils.OpSimpleExec.bl_idname}', text=self.lines[-1].txtExec).exc = "+"f\"{repr(ndTar)}.ExecuteAll()\""
        ndNqle0.lines.add().txtExec = "row.scale_y = 5.0"
        ndNqle0.lines.add().txtExec = "Big button for anti-missclick"
        ndNqle0.lines[-1].isActive = False
        ndNqle0.count = ndNqle0.count
        ##
        ndNqle1.lines.clear()
        ndNqle1.lines.add().txtExec = "def PopupMessage(self, context):"
        ndNqle1.lines.add().txtExec = "  col = self.layout.column(align=True)"
        ndNqle1.lines.add().txtExec = "  col.label(text=\"The big button works successfully.\", icon='INFO')"
        ndNqle1.lines.add().txtExec = "  for cyc in range(1): col.label(text=\" \"*1)"
        ndNqle1.lines.add().txtExec = f"bpy.context.window_manager.popup_menu(PopupMessage, title=\"{ndNqle0.name}\", icon='NONE')"
        ndNqle1.lines.add().txtExec = f"import random; self.id_data.nodes[\"{ndNqle1.name}\"].label = \"Big button's code below: \"+str(random.random())"
        ndNqle1.lines.add().isTb = True
        ndNqle1.count = 7
        return list_addedNodes
    def ThemeRoundness(tree, meta_cat="2Example"):
        list_addedNodes = []
        ndNsf = tree.nodes.new(Nodes.NodeSolemnFactor.bl_idname)
        list_addedNodes.append(ndNsf)
        ndNsf.name = "ThemeRoundness0"
        ndNsf.isHlFromTheme = False
        ndNqle0 = tree.nodes.new(Nodes.NodeQuickLayoutExec.bl_idname)
        list_addedNodes.append(ndNqle0)
        ndNqle0.location.y = -60
        ndNqle0.width = 700
        ndNqle0.name = "ThemeRoundness1"
        ndNqle0.method = 'EXEC'
        ndNqle0.decorExec = ""
        ndNqle0.visibleButtons = 0
        ndNqle1 = tree.nodes.new(Nodes.NodeQuickLayoutExec.bl_idname)
        list_addedNodes.append(ndNqle1)
        ndNqle1.location = (-100, 20)
        ndNqle1.width = 440
        ndNqle1.name = "ThemeRoundness2"
        ndNqle1.method = 'EXEC'
        ndNqle1.isShowOnlyLayout = True
        ndNqle1.decorExec = "Press me to init"
        ndNqle1.visibleButtons = 0
        ndNqle2 = tree.nodes.new(Nodes.NodeQuickLayoutExec.bl_idname)
        list_addedNodes.append(ndNqle2)
        ndNqle2.location.y = -250
        ndNqle2.width = 230
        ndNqle2.name = "ThemeRoundness3"
        ndNqle2.label = "List"
        ndNqle2.hide = True
        ndNqle2.isShowOnlyLayout = True
        list_addedNodes[0], list_addedNodes[2] = list_addedNodes[2], list_addedNodes[0]
        ##
        ndNsf.txtExecOnUpdate = f"self.id_data.nodes[\"{ndNqle0.name}\"].ExecuteAll()"
        ##
        ndNqle0.lines.clear()
        ndNqle0.lines.add().txtExec = "theme = C.preferences.themes[0].user_interface"
        ndNqle0.lines.add().txtExec = "txtAtts = \"regular  tool  toolbar_item  radio  text  option  toggle  num  numslider  box  menu  pulldown  menu_back  pie_menu  tooltip  menu_item  scroll  progress  list_item  tab\""
        ndNqle0.lines.add().txtExec = f"if ndTar:=self.id_data.nodes.get(\"{ndNsf.name}\"):"
        ndNqle0.lines.add().txtExec = "  val = ndTar.value"
        ndNqle0.lines.add().txtExec = "  for li in txtAtts.split():"
        ndNqle0.lines.add().txtExec = "    setattr(getattr(C.preferences.themes[0].user_interface, \"wcol_\"+li),'roundness', val)"
        ndNqle0.lines.add().txtExec = "  C.preferences.themes[0].user_interface.panel_roundness = val"
        ndNqle0.count = ndNqle0.count
        ##
        ndNqle1.lines.clear()
        ndNqle1.lines.add().txtExec = ndNqle0.lines[0].txtExec
        ndNqle1.lines.add().txtExec = ndNqle0.lines[1].txtExec
        ndNqle1.lines.add().txtExec = ndNqle0.lines[2].txtExec
        ndNqle1.lines.add().txtExec = "  acc = 0.0"
        ndNqle1.lines.add().txtExec = ndNqle0.lines[4].txtExec
        ndNqle1.lines.add().txtExec = "    acc += getattr(getattr(C.preferences.themes[0].user_interface, \"wcol_\"+li),'roundness')"
        ndNqle1.lines.add().txtExec = "  ndTar[ndTar.txtPropSelfSolemn] = acc/len(txtAtts.split())"
        ndNqle1.lines.add().txtExec = "  ndTar.select = False"
        ndNqle1.lines.add().txtExec = "C.node.id_data.nodes.remove(C.node)"
        ndNqle1.lines.add().txtExec = f"self.id_data.nodes[\"{ndNqle0.name}\"].select = False"
        ndNqle1.lines.add().txtExec = f"self.id_data.nodes[\"{ndNqle2.name}\"].select = False"
        ndNqle1.count = ndNqle1.count
        ##
        ndNqle2.lines.clear()
        ndNqle2.lines.add().txtExec = ndNqle0.lines[0].txtExec
        ndNqle2.lines.add().txtExec = ndNqle0.lines[1].txtExec
        ndNqle2.lines.add().txtExec = "colList = ly.column(align=True)"
        fit = ["Regular", "Tool", "Toolbar Item", "Radio Buttons", "Text", "Option", "Toggle", "Number Field", "Value Slider", "Box", "Menu", "Pulldown", "Menu Background", "Pie Menu", "Tooltip", "Menu Item", "Scroll Bar", "Progress Bar", "List Item", "Tab"]
        ndNqle2.lines.add().txtExec = "list_names = [\""+"\", \"".join(fit)+"\"]"
        ndNqle2.lines.add().txtExec = "for cyc, li in enumerate(txtAtts.split()):"
        ndNqle2.lines.add().txtExec = "  colList.prop(getattr(C.preferences.themes[0].user_interface, \"wcol_\"+li),'roundness', text=list_names[cyc])"
        ndNqle2.lines.add().txtExec = "colList.prop(C.preferences.themes[0].user_interface,'panel_roundness')"
        ndNqle2.count = ndNqle2.count
        return list_addedNodes
    def AssertFrameStep(tree, meta_cat="2Example"):
        list_addedNodes = []
        ndNa = tree.nodes.new(Nodes.NodeAssertor.bl_idname)
        list_addedNodes.append(ndNa)
        ndNa.width = 560
        ndNa.name = "AssertFrameStep"
        ndNa.method = 'EVAL'
        ndNa.txtAssert = "(C.scene.frame_step == 1) and (C.scene.render.resolution_y % 2 == 0)"
        ndNa.decorText = "Frame Step is 1  and  Even Resolution[1]"
        ndNa.alertColor = (0.85, 0.425, 0.0, 1.0)
        return list_addedNodes
    def StatOfTbLines(tree, meta_cat="1Utility"):
        list_addedNodes = []
        ndNqle = tree.nodes.new(Nodes.NodeQuickLayoutExec.bl_idname)
        list_addedNodes.append(ndNqle)
        ndNqle.width = 310
        ndNqle.name = "StatOfTbLines"
        ndNqle.label = "Statistic of textblock lines"
        ndNqle.isShowOnlyLayout = True
        ndNqle.lines.clear()
        ndNqle.lines.add().txtExec = "colList = ly.column(align=True)"
        ndNqle.lines.add().txtExec = "def LyAddItem(where, *, text):"
        ndNqle.lines.add().txtExec = "  rowItem = where.row(align=True); rowSize = rowItem.row(align=False)"
        ndNqle.lines.add().txtExec = "  box = rowSize.box(); box.scale_y = 0.5; rowNum = box.row()"
        ndNqle.lines.add().txtExec = "  rowNum.ui_units_x = 3.5; rowNum.alignment = 'RIGHT'"
        ndNqle.lines.add().txtExec = "  rowNum.label(text=text); rowNum.active = False"
        ndNqle.lines.add().txtExec = "  return rowItem"
        ndNqle.lines.add().txtExec = "set_ignoreNames = set(self.lines[-1].txtExec.split(\"§\")); list_sucessIgnoredTb = []"
        ndNqle.lines.add().txtExec = "sco = 0"
        ndNqle.lines.add().txtExec = "for tb in sorted(bpy.data.texts, key=lambda a: len(a.lines), reverse=True):"
        ndNqle.lines.add().txtExec = "  if tb.name not in set_ignoreNames:"
        ndNqle.lines.add().txtExec = "    LyAddItem(colList, text=f\" {len(tb.lines)} lines\").prop(tb,'name', text=\"\")#, icon='TEXT')"
        ndNqle.lines.add().txtExec = "    sco += len(tb.lines)"
        ndNqle.lines.add().txtExec = "  else: list_sucessIgnoredTb.append(tb)"
        ndNqle.lines.add().txtExec = "row = LyAddItem(colList, text=f\" {sco} total\")#.row(); row.label(icon='ASSET_MANAGER'); row.active = False"
        ndNqle.lines.add().txtExec = "LyAddItem(colList, text=\"Ignoring\").prop(self.lines[-1],'txtExec', text=\"\")"
        ndNqle.lines.add().txtExec = "for tb in sorted(list_sucessIgnoredTb, key=lambda a: len(a.lines), reverse=True):"
        ndNqle.lines.add().txtExec = "  rowItem = colList.row(align=True); rowLines = rowItem.row(align=False)"
        ndNqle.lines.add().txtExec = "  rowItem.active = False; rowLines.ui_units_x = 4; rowLines.alignment = 'RIGHT'"
        ndNqle.lines.add().txtExec = "  rowLines.label(text=f\" {len(tb.lines)} lines \"); rowItem.separator(); rowItem.label(text=tb.name)"
        ndNqle.lines.add().txtExec = "Log§Log.py§Log.txt§§§§§§§§§§§§§"
        ndNqle.lines[-1].isActive = False
        ndNqle.count = ndNqle.count
        return list_addedNodes
    def RedrawCheck(tree, meta_cat="1Utility"):
        list_addedNodes = []
        ndNqle = tree.nodes.new(Nodes.NodeQuickLayoutExec.bl_idname)
        list_addedNodes.append(ndNqle)
        ndNqle.width = 200
        ndNqle.name = "RedrawCheck"
        ndNqle.label = "Redraw Check"
        ndNqle.isShowOnlyLayout = True
        ndNqle.visibleButtons = 0
        ndNqle.lines.clear()
        ndNqle.lines.add().txtExec = "import random; ly.label(text=str(random.random()), icon=\"SEQUENCE_COLOR_0\"+str(random.randint(1, 9)))"
        return list_addedNodes
    def NodeFlagViewer(tree, meta_cat="1Utility"):
        list_addedNodes = []
        ndNqle = tree.nodes.new(Nodes.NodeQuickLayoutExec.bl_idname)
        list_addedNodes.append(ndNqle)
        ndNqle.width = 340
        ndNqle.name = "NodeFlagViewer"
        ndNqle.label = "Node flag viewer"
        ndNqle.isShowOnlyLayout = True
        ndNqle.lines.clear()
        ndNqle.lines.add().txtExec = "if (ndAc:=self.id_data.nodes.active)or(ndAc:=self):"
        ndNqle.lines.add().txtExec = "  def Recr(txt, depth=3):"
        ndNqle.lines.add().txtExec = "    return txt if not depth else Recr(txt[:len(txt)//2], depth-1)+\" \"*depth+Recr(txt[len(txt)//2:], depth-1)"
        ndNqle.lines.add().txtExec = "  def LyLabel(where, *, header, txt):"
        ndNqle.lines.add().txtExec = "    rowMain = where.row(align=True); rowMain.alignment = 'CENTER'; row = rowMain.row(); row.alignment = 'CENTER'"
        ndNqle.lines.add().txtExec = "    row.active = False; row.label(text=header); rowMain.label(text=txt)"
        ndNqle.lines.add().txtExec = "  ly.prop(ndAc,'name', text=\"\", icon='NODE')"
        ndNqle.lines.add().txtExec = "  suFlag = opa.BNode(ndAc).flag"
        ndNqle.lines.add().txtExec = "  LyLabel(ly, header=\"bin\", txt=Recr(bin(suFlag).replace(\"0b\", \"\").rjust(32, \"0\")))"
        ndNqle.lines.add().txtExec = "  LyLabel(ly, header=\"dec\", txt=str(suFlag))"
        ndNqle.count = ndNqle.count
        return list_addedNodes
    def UserAgreement(tree, meta_cat="2Example"):
        list_addedNodes = []
        ndSb = tree.nodes.new(Nodes.NodeSolemnBool.bl_idname)
        list_addedNodes.append(ndSb)
        ndSb.name = "UserAgreement"
        ndSb.label = "Agreement"
        ndSb.alertColor = (1.0, 0.0, 0.0, 1.75)
        ndSb.txtCeremonial = "Blender the best!"
        ndSb.txtExecOnUpdate = "if self.value==False: print№(\"Oh nooo...\")".replace("№", "")
        ndSb.alerting = False
        ndSb.isHlFromTheme = False
        return list_addedNodes
    def NqleAlerting(tree, meta_cat="2Example"):
        list_addedNodes = []
        ndNqle = tree.nodes.new(Nodes.NodeQuickLayoutExec.bl_idname)
        list_addedNodes.append(ndNqle)
        ndNqle.width = 650
        ndNqle.name = "NqleAlerting"
        ndNqle.label = "Nqle Alerting Example"
        ndNqle.alertColor = (2.0, 2.0, 2.0, 1.5)
        ndNqle.lines.clear()
        ndNqle.lines.add().txtExec = "curLoc = C.space_data.cursor_location"
        ndNqle.lines.add().txtExec = "if C.region.view2d.view_to_region(curLoc.x, curLoc.y)!=(12000, 12000):"
        ndNqle.lines.add().txtExec = "  isX = (curLoc.x>self.location.x)and(curLoc.x<self.location.x+self.width)"
        ndNqle.lines.add().txtExec = "  scaleUi = C.preferences.system.dpi/72"
        ndNqle.lines.add().txtExec = "  isY = (curLoc.y<self.location.y)and(curLoc.y>self.location.y-self.dimensions.y/scaleUi)" #Огм, у меня без "s" свойство почему-то периодически существует.
        ndNqle.lines.add().txtExec = "  alert = (isX)and(isY)"
        ndNqle.lines.add().txtExec = "#ly.prop(C.preferences.view,'ui_scale')"
        ndNqle.count = ndNqle.count
        return list_addedNodes
    def RedrawAlways(tree, meta_cat="1Utility"):
        list_addedNodes = []
        ndNqle = tree.nodes.new(Nodes.NodeQuickLayoutExec.bl_idname)
        list_addedNodes.append(ndNqle)
        ndNqle.width = 160
        ndNqle.name = "RedrawAlways"
        ndNqle.label = "Always Redraw"
        ndNqle.isShowOnlyLayout = True
        ndNqle.lines.clear()
        ndNqle.lines.add().txtExec = "import functools"
        ndNqle.lines.add().txtExec = "def TimerRedrawAlways(reprNd):"
        ndNqle.lines.add().txtExec = "  nd = eval(reprNd); nd.label = nd.label"
        ndNqle.lines.add().txtExec = "bpy.app.timers.register(functools.partial(TimerRedrawAlways, self.__mng_repr__()))"
        ndNqle.lines.add().txtExec = "ly.label(text=\"Now all always redrawn\")"
        ndNqle.count = ndNqle.count
        return list_addedNodes
    def NyanCat(tree, meta_cat="2Example"):
        list_addedNodes = []
        ndNqle = tree.nodes.new(Nodes.NodeQuickLayoutExec.bl_idname)
        list_addedNodes.append(ndNqle)
        ndNqle.name = "NyanCat"
        ndNqle.label = "Gen Node NyanCat"
        ndNqle.method = 'EXEC'
        ndNqle.decorExec = "Add"
        ndNqle.lines.clear()
        ndNqle.lines.add().txtExec = "class NodeNyanCat(bpy.types.Node):"
        ndNqle.lines.add().txtExec = "  bl_idname = 'NodeNyanCat'; bl_label = \"Nyan Cat\""
        ndNqle.lines.add().txtExec = "  bl_width_default = 395; bl_width_max = bl_width_default; bl_width_min = bl_width_default"
        ndNqle.lines.add().txtExec = "  dataNc0 = \"ĈƸÑÐÙøÙÐáĐÉÒÉÈÉÒÉèÉÒÉÈÑÒÉĈũÚÉĀÉĒÉĔÙĀÉÒùÚÉýÜÉĀÉ×ÊÉÒÉÒÉÊ×ÊÉíÎÍÔÉĀÉ×Ċ×ÊÉÕÎíÌÑøÉÒÑÊÉÚÑÚÉąÌáèÉÒÉËêÉËÚÉõÎÍÌÉÒÑàÉĲÉÎýÌÑÒÑàÉĢÉíÎÝÌÙÒÑØÉâáâÉčÌÉÈÑÒÉØÉÚÉÌÝÉÚÉÕÎõÌÉÐáØÉÒÑÌåÉÒÉčÌÉĐÑÈÉÌÕÎÕÑĕÌÉĨÉÌĵÎÕÌÉĨÉÔíÎÕÎõÔÉĨÉÜĭÜÉİÉŌÉŀŉĈ\""
        ndNqle.lines.add().txtExec = "  dataNc1 = \"øƸÙÐÙøÙØÙĐÉÒÉÈÉÒÉðÉÒÉÈÉÒÉĈűÒÉĀÉĒÉĜÑĀÉÒùÚÉąÜÉøÉ×ÊÉÒÉÒÉÊ×ÊÉõÎÍÔÉøÉ×Ċ×ÊÉÝÎíÌÙèÉÒÑÊÉÚÑÚÉčÌÉÒÑØÉÒÉËêÉËÚÉýÎÍÌÉâÉÐÉĲÉÍÎýÌáÒÉÐÉĢÉõÎÝÌÉÐÉÒÉÐÉâáâÉĕÌÉØÑØÉÚÑÌÕÉÚÉÝÎõÌÉĀÉÒÉÈÉÌÝÉÒÉĕÌÉĈÑÐÉÌÕÎÍÑĝÌÉĨÉÌĵÎÕÌÉĨÉÔíÎÕÎõÔÉĨÉÜĭÜÉİÉŌÉŀŉĈ\""
        ndNqle.lines.add().txtExec = "  dataNc2 = \"ØÙÐÙøÙØÙĐÉÒÉÈÉÒÉðÉÒÉÈÉÒÉĐűÊÉĈÉĒÉĜÑĀÉÒùÚÉąÜÉøÉ×ÊÉÒÉÒÉÊ×ÊÉõÎÍÔÉÈáÐÉ×Ċ×ÊÉÝÎíÌÙÚÉÈÉÒÑÊÉÚÑÚÉčÌÉâÑÈÉÒÉËêÉËÚÉýÎÍÌéØÉĲÉÍÎýÌÑøÉĢÉõÎÝÌÉĀÉâáâÉĕÌÉĀÉÚÑÌÕÉÚÉÝÎõÌÉĀÉÒÉÈÉÌÝÉÒÉĕÌÉĈÑÐÉÌÕÎÍÑĝÌÉĨÉÌĵÎÕÌÉĨÉÔíÎÕÎõÔÉĨÉÜĭÜÉİÉŌÉŀŉĠƸ\""
        ndNqle.lines.add().txtExec = "  dataNc3 = \"àÙÐÙøÙØÙĐÉÒÉÈÉÒÉðÉÒÉÈÉÒÉĈűÒÉĀÉĒÉĜÑĀÉÒùÚÉąÜÉØÑÐÉ×ÊÉÒÉÒÉÊ×ÊÉõÎÍÔÉÐÉÒÉÈÉ×Ċ×ÊÉÝÎíÌáÒÉÈÉÒÑÊÉÚÑÚÉčÌÉâÉÐÉÒÉËêÉËÚÉýÎÍÌÉÒÑØÉĲÉÍÎýÌÙðÉĢÉõÎÝÌÉĀÉâáâÉĕÌÉĀÉÚÑÌÕÉÚÉÝÎõÌÉĀÉÒÉÈÉÌÝÉÒÉĕÌÉĈÑÐÉÌÕÎÍÑĝÌÉĨÉÌĵÎÕÌÉĨÉÔíÎÕÎõÔÉĨÉÜĭÜÉİÉŌÉŀŉĠƸ\""
        ndNqle.lines.add().txtExec = "  dataNc4 = \"ðÙÐÙøÙØÙĐÉÒÉÈÉÒÉðÉÒÉÈÉÒÉĀűÚÉøÉĒÉĔáøÉÒùÚÉýÜÑøÉ×ÊÉÒÉÒÉÊ×ÊÉíÎÍÔÉĀÉ×Ċ×ÊÉÕÎíÌÉĀÉÒÑÊÉÚÑÚÉąÌÙðÉÒÉËêÉËÚÉõÎÍÌÉÊáØÉĲÉÎýÌÑâÑÐÉĢÉíÎÝÌáÚÉÐÉâáâÉčÌÉÐáØÉÚÉÌÝÉÚÉÕÎõÌÉĈÉÒÑÌåÉÒÉčÌÉĐÑÈÉÌÕÎÕÑĕÌÉĨÉÌĵÎÕÌÉĨÉÔíÎÕÎõÔÉĨÉÜĭÜÉİÉŌÉŀŉĠƸ\""
        ndNqle.lines.add().txtExec = "  dataNc5 = \"ðÙØÙøÙÐÙĐÉÒÉÈÉÒÉðÉÒÉÈÉÒÉĐÉÊőÚÉĀđĜÑÊÉĀÉĒÉąÜÑĀÉÒùÚÉõÎÍÔÉĀÉ×ÊÉÒÉÒÉÊ×ÊÉÕÎíÌÉĀÉ×Ċ×ÊÉąÌÙðÉÒÑÊÉÚÑÚÉõÎÍÌÉÒÑàÉÒÉËêÉËÚÉÎýÌÉâÉØÉĲÉåÎÝÌáÒÉØÉĢÉčÌÉÐÉÒÉØÉâáâÉÕÎõÌÉØÑàÉÚÉÌÝÉÚÉčÌÉĈÉÒÑÌÕÎÍÉÒÉčÌÉĐÑÈÉÌíÑýÎÕÌÉĨÉÔíÎÕÎõÔÉĨÉÜĭÜÉİÉŌÉŀŉĠƸ\""
        ndNqle.lines.add().txtExec = "  def draw_label(self):"
        ndNqle.lines.add().txtExec = "    opa.BNode(self).typeinfo.nclass = 33"
        ndNqle.lines.add().txtExec = "    return \"\""
        ndNqle.lines.add().txtExec = "  def draw_buttons(self, context, layout):"
        ndNqle.lines.add().txtExec = "    self.draw_label()"
        ndNqle.lines.add().txtExec = "    colRows = layout.column(align=True); colRows.scale_y = 0.59"
        ndNqle.lines.add().txtExec = "    bNd = opa.BNode(self); inx = bNd.flag>>25; bNd.flag = (bNd.flag&2**25-1)+(((inx+1)%6)<<25)"
        ndNqle.lines.add().txtExec = "    txt = getattr(self, f'dataNc{inx}')"
        ndNqle.lines.add().txtExec = "    num = 0; sco = 0"
        ndNqle.lines.add().txtExec = "    for ch in (txt):"
        ndNqle.lines.add().txtExec = "      num <<= 8"
        ndNqle.lines.add().txtExec = "      num += ord(ch)-192"
        ndNqle.lines.add().txtExec = "    while num>0:"
        ndNqle.lines.add().txtExec = "      for cyc in range(num%256//8):"
        ndNqle.lines.add().txtExec = "        if (not sco%34)and(sco!=681):"
        ndNqle.lines.add().txtExec = "          rowColimns = colRows.row(align=True); rowColimns.scale_x = 0.79; rowColimns.alignment = 'CENTER'"
        ndNqle.lines.add().txtExec = "        rowColimns.label(icon=['BLANK1', 'SEQUENCE_COLOR_04', 'SEQUENCE_COLOR_09', 'SNAP_FACE', 'SEQUENCE_COLOR_03', 'SEQUENCE_COLOR_07', 'SEQUENCE_COLOR_06', 'SEQUENCE_COLOR_07'][num%8])"
        ndNqle.lines.add().txtExec = "        sco += 1"
        ndNqle.lines.add().txtExec = "      num >>= 8"
        ndNqle.lines.add().txtExec = "bpy.utils.register_class(NodeNyanCat)"
        ndNqle.lines.add().txtExec = "bpy.ops.node.add_node('INVOKE_DEFAULT', type=NodeNyanCat.bl_idname, use_transform=True)"
        ndNqle.count = ndNqle.count
        return list_addedNodes
    def AllPointersFromNsp(tree, meta_cat="2Example"):
        list_addedNodes = []
        ndNqle = tree.nodes.new(Nodes.NodeQuickLayoutExec.bl_idname)
        list_addedNodes.append(ndNqle)
        ndNqle.width = 340
        ndNqle.name = "ViewAllPointersFromNsp"
        ndNqle.isShowOnlyLayout = True
        ndNqle.lines.clear()
        ndNqle.lines.add().txtExec = "colInfo = ly.column(); colInfo.active = False"
        ndNqle.lines.add().txtExec = "if ndTar:=self.id_data.nodes.active:"
        ndNqle.lines.add().txtExec = "  colInfo.prop(ndTar,'name', text=\"\", icon='NODE')"
        ndNqle.lines.add().txtExec = "  if ndTar.bl_idname=='MngNodeSolemnPointer':"
        ndNqle.lines.add().txtExec = "    colInfo.active = True; colInfo.separator()"
        ndNqle.lines.add().txtExec = "    rowList = ly.row(align=False); colName = rowList.column(align=True)"
        ndNqle.lines.add().txtExec = "    colName.alignment = 'RIGHT'; colProp = rowList.column(align=True)  "
        ndNqle.lines.add().txtExec = "    colName.label(text=\"\"); colProp.prop(ndTar,'typePoi', text=\"\")"
        ndNqle.lines.add().txtExec = "    colName.separator(); colProp.separator()"
        ndNqle.lines.add().txtExec = "    for ti in ndTar.tup_itemsAvailableTypes:"
        ndNqle.lines.add().txtExec = "      colProp.prop(ndTar, 'pointer'+ti[0], text=\"\")"
        ndNqle.lines.add().txtExec = "      if ti[0]==ndTar.typePoi: colName.alert = True"
        ndNqle.lines.add().txtExec = "      colName.label(text=ti[1]); colName.alert = False"
        ndNqle.lines.add().txtExec = "  else: colInfo.label(text=\"Need a \\\"Solemn Pointer\\\" node.\")"
        ndNqle.lines.add().txtExec = "else: colInfo.label(text=\"Active node is None\")"
        ndNqle.count = ndNqle.count
        return list_addedNodes
    def ItsMyTreeOfGeoNodes(tree, meta_cat="2Example"):
        list_addedNodes = []
        ndNqle = tree.nodes.new(Nodes.NodeQuickLayoutExec.bl_idname)
        list_addedNodes.append(ndNqle)
        ndNqle.width = 330
        ndNqle.name = "ItsMyTreeOfGeoNodes"
        ndNqle.label = "Example of welcoming self-promotion"
        ndNqle.isShowOnlyLayout = True
        ndNqle.lines.clear()
        ndNqle.lines.add().txtExec = "ly.label(text=\"Hi! This is my geonodes tree under my authorship!\")"
        ndNqle.lines.add().txtExec = "row = ly.row(align=True)"
        ndNqle.lines.add().txtExec = "row.alignment = 'LEFT'"
        ndNqle.lines.add().txtExec = "row.label(text=\"Pls subscribe on my YouTube channel:\")"
        ndNqle.lines.add().txtExec = "row.operator('wm.url_open', text=\" Git  \", icon='URL').url = \"https://github.com/ugorek000/ManagerNodeTree\""
        ndNqle.count = ndNqle.count
        return list_addedNodes
    def InfoAboutObject(tree, meta_cat="2Example"):
        list_addedNodes = []
        ndNsp = tree.nodes.new(Nodes.NodeSolemnPointer.bl_idname)
        list_addedNodes.append(ndNsp)
        ndNsp.name = "InfoAboutObject0"
        ndNsp.label = "Example object custom info"
        ndNsp.decorTypeToNode = False
        ndNqle = tree.nodes.new(Nodes.NodeQuickLayoutExec.bl_idname)
        list_addedNodes.append(ndNqle)
        ndNqle.location.y = -60
        ndNqle.width = 330
        ndNqle.name = "InfoAboutObject1"
        ndNqle.label = "Custom viewer of object props"
        ndNqle.isShowOnlyLayout = True
        ndNqle.lines.clear()
        ndNqle.lines.add().txtExec = "data§parent§active_material§location§show_bounds§show_name§show_axis§show_texture_space§show_wire§show_all_edges§show_in_front§§§§§§§"
        ndNqle.lines[-1].isActive = False
        ndNqle.lines.add().txtExec = f"if obj:=self.id_data.nodes[\"{ndNsp.name}\"].pointerObject:"
        ndNqle.lines.add().txtExec = "  rowName = ly.row(align=True); rowName.prop(obj,'name', text=\"\", icon='OBJECT_DATA'); rowName.prop(obj,'use_fake_user', text=\"\")"
        ndNqle.lines.add().txtExec = "  for scn in D.scenes:"
        ndNqle.lines.add().txtExec = "    if obj.name in scn.objects:"
        ndNqle.lines.add().txtExec = "      row = ly.row(align=True); row.label(icon='BLANK1'); colScns = row.column(align=True)"
        ndNqle.lines.add().txtExec = "      row = colScns.row(align=True); row.prop(scn,'name', text=\"\", icon='SCENE_DATA'); row.prop(scn,'use_fake_user', text=\"\")"
        ndNqle.lines.add().txtExec = "      row = colScns.row(align=True); row.label(icon='BLANK1'); colLays = row.column(align=True)"
        ndNqle.lines.add().txtExec = "      for lay in scn.view_layers:"
        ndNqle.lines.add().txtExec = "        if obj.name in lay.objects:"
        ndNqle.lines.add().txtExec = "          colLays.prop(lay,'name', text=\"\", icon='RENDERLAYERS')"
        ndNqle.lines.add().txtExec = "  row = ly.row(align=True); row.prop(self.lines[0],'txtExec', text=\"\", placeholder=\"Props§\"); row.active = True"
        ndNqle.lines.add().txtExec = "  colProps = ly.column(align=True); colProps.use_property_split = True; colProps.use_property_decorate = False"
        ndNqle.lines.add().txtExec = "  for li in self.lines[0].txtExec.split(\"§\"):"
        ndNqle.lines.add().txtExec = "    if li:"
        ndNqle.lines.add().txtExec = "      if hasattr(obj, li): colProps.row().prop(obj, li)"
        ndNqle.lines.add().txtExec = "      else: colProps.label(text=f\"property not found: Object.{li}\", icon='ERROR')"
        ndNqle.lines.add().txtExec = "else:"
        ndNqle.lines.add().txtExec = "  row = ly.row(align=True); row.label(text=\"Object pointer is None\"); row.active = False"
        ndNqle.count = ndNqle.count
        return list_addedNodes
    def Detector001(tree, meta_cat="1Utility"):
        list_addedNodes = []
        ndNqle = tree.nodes.new(Nodes.NodeQuickLayoutExec.bl_idname)
        list_addedNodes.append(ndNqle)
        ndNqle.width = 280
        ndNqle.name = "Detector001"
        ndNqle.label = ".001 Detector"
        ndNqle.isShowOnlyLayout = True
        ndNqle.lines.clear()
        ndNqle.lines.add().txtExec = "import re"
        ndNqle.lines.add().txtExec = f"dict_typeIdToIcon = {repr(Utils.dict_typeIdToIcon)}"
        ndNqle.lines.add().txtExec = "isEmpty = True"
        ndNqle.lines.add().txtExec = "for att in dir(bpy.data):"
        ndNqle.lines.add().txtExec = "  ess = getattr(bpy.data, att)"
        ndNqle.lines.add().txtExec = "  if (ess.__class__.__name__==\"bpy_prop_collection\")and(list_founds:=[li for li in ess if re.search(r\"\.\d\d\d$\", li.name)]):"
        ndNqle.lines.add().txtExec = "    colHeader = ly.column(align=True); rowHeader = colHeader.row(); box = rowHeader.box(); box.scale_y = 0.5; rowData = box.row(align=True)"
        ndNqle.lines.add().txtExec = "    rowName = rowData.row(); rowName.alignment = 'LEFT'; rowName.alert = True; rowName.label(text=ess.bl_rna.name[5:])"
        ndNqle.lines.add().txtExec = "    rowCou = rowData.row(); rowCou.label(text=str(len(list_founds))); rowCou.active = False"
        ndNqle.lines.add().txtExec = "    rowNext = colHeader.row(align=True); rowNext.label(icon='BLANK1'); colList = rowNext.column(align=True)"
        ndNqle.lines.add().txtExec = "    for li in list_founds:"
        ndNqle.lines.add().txtExec = "      colList.prop(li,'name', text=\"\", icon=dict_typeIdToIcon[ess.bl_rna.identifier[9:]])"
        ndNqle.lines.add().txtExec = "    isEmpty = False"
        ndNqle.lines.add().txtExec = "if isEmpty:"
        ndNqle.lines.add().txtExec = "  ly.label(text=\"Clear!\")"
        ndNqle.count = ndNqle.count
        return list_addedNodes
    def Selector001(tree, meta_cat="2Example"):
        list_addedNodes = []
        ndNsp = tree.nodes.new(Nodes.NodeSolemnPointer.bl_idname)
        list_addedNodes.append(ndNsp)
        ndNsp.width = 280
        ndNsp.name = "Selector001"
        ndNsp.label = ".001 Selector"
        ndNsp.txtEvalPoll = "exec(\"import re\") or re.search(r\"\.\d\d\d$\", poi.name)"
        ndNsp.txtExecOnUpdate = ""
        ndNsp.decorTypeToNode = True
        return list_addedNodes
    def ToggleNodeRegistering(tree, meta_cat="3Dev"):
        list_addedNodes = []
        ndNqle = tree.nodes.new(Nodes.NodeQuickLayoutExec.bl_idname)
        list_addedNodes.append(ndNqle)
        ndNqle.width = 360
        ndNqle.name = "ToggleNodeRegistering"
        ndNqle.label = "ToggleNodeRegistering"
        ndNqle.method = 'EXEC'
        ndNqle.decorExec = "Toggle"
        ndNqle.visibleButtons = 7
        ndNqle.lines.clear()
        ndNqle.lines.add().txtExec = "NodeNclassTagViewer"
        ndNqle.lines[-1].isActive = False
        ndNqle.lines.add().txtExec = "def RecrFindCls(cls):"
        ndNqle.lines.add().txtExec = "  if cls.__name__==self.lines[0].txtExec:"
        ndNqle.lines.add().txtExec = "    return cls"
        ndNqle.lines.add().txtExec = "  for cls in cls.__subclasses__():"
        ndNqle.lines.add().txtExec = "    if result:=RecrFindCls(cls):"
        ndNqle.lines.add().txtExec = "      return result"
        ndNqle.lines.add().txtExec = "clsNode = RecrFindCls(bpy.types.Node)"
        ndNqle.lines.add().txtExec = "try: bpy.utils.register_class(clsNode)"
        ndNqle.lines.add().txtExec = "except: bpy.utils.unregister_class(clsNode)"
        ndNqle.count = ndNqle.count
        return list_addedNodes
    def ExecNearestNqle(tree, meta_cat="1Utility"):
        list_addedNodes = []
        ndNqle0 = tree.nodes.new(Nodes.NodeQuickLayoutExec.bl_idname)
        list_addedNodes.append(ndNqle0)
        ndNqle0.width = 205
        ndNqle0.name = "ExecNearestNqle0"
        ndNqle0.label = "Exec nearest Nqle (as exec)"
        ndNqle0.method = 'EXEC'
        ndNqle0.isShowOnlyLayout = True
        ndNqle0.lines.clear()
        ndNqle0.lines.add().txtExec = "#FriendlyFireInfRecursion"
        ndNqle0.lines.add().txtExec = "minLen = 16777216.0; ndNear = None"
        ndNqle0.lines.add().txtExec = "for nd in self.id_data.nodes:"
        ndNqle0.lines.add().txtExec = "  if (nd!=self)and(nd.bl_idname==self.bl_idname)and(len:=(nd.location-self.location).length)and(minLen>len):"
        ndNqle0.lines.add().txtExec = "    minLen = len; ndNear = nd"
        ndNqle0.lines.add().txtExec = "if (ndNear)and(ndNear.lines[0].txtExec!=self.lines[0].txtExec):"
        ndNqle0.lines.add().txtExec = "  self.decorExec = ndNear.decorExec; self.label = ndNear.label if ndNear.label else ndNear.name"
        ndNqle0.lines.add().txtExec = "  ndNear.ExecuteAll()"
        ndNqle0.count = ndNqle0.count
        ndNqle1 = tree.nodes.new(Nodes.NodeQuickLayoutExec.bl_idname)
        list_addedNodes.append(ndNqle1)
        ndNqle1.location.x = 245
        ndNqle1.width = 205
        ndNqle1.name = "ExecNearestNqle1"
        ndNqle1.label = "Exec nearest Nqle (as layout)"
        ndNqle1.isShowOnlyLayout = True
        ndNqle1.lines.clear()
        for cyc in range(6):
            ndNqle1.lines.add().txtExec = ndNqle0.lines[cyc].txtExec
        ndNqle1.lines.add().txtExec = "  ly.label(text=str(ndNear.name), icon='NODE')"
        ndNqle1.lines.add().txtExec = f"  ly.operator('{Utils.OpSimpleExec.bl_idname}', text=ndNear.decorExec).exc = "+"f\"{repr(ndNear)}.ExecuteAll()\""
        ndNqle1.lines.add().txtExec = "else:"
        ndNqle1.lines.add().txtExec = "  ly.label(text=\"Nearest Nqle not found\"); ly.active = False"
        ndNqle1.lines.add().txtExec = f"  ly.operator('{Utils.OpSimpleExec.bl_idname}', text=\"--\")"
        ndNqle1.count = ndNqle1.count
        return list_addedNodes
    def IconShop(tree, meta_cat="1Utility"):
        list_addedNodes = []
        ndNqle = tree.nodes.new(Nodes.NodeQuickLayoutExec.bl_idname)
        list_addedNodes.append(ndNqle)
        ndNqle.width = 222
        ndNqle.name = "IconShop"
        ndNqle.label = "Gen Icon Shop"
        ndNqle.method = 'EXEC'
        ndNqle.isShowOnlyLayout = True
        ndNqle.decorExec = "You are ready?  Press me!"
        ndNqle.lines.clear()
        fit  = "ŮĕƘĲËćƔƱľÞŘÁğĨĐÀÑóĤïĎƹœÁöĒÀÀŨƂĉƬþƪŘûãñēƎÀóŕĐÀáÊñäěĤƴœÒâĢĎƉűõäūĐřŝŔŎĸŖƑßåƬŌŐƓÈèīŪŪĲŧÐÀĹÓĺĮčũÈƜţòœÐàġÕĚÅŢđÍÚÀÀúÎƘĘüÇƀƴÏèòƣƉàĴáŰÀÚÒØŦÊÂŌƥðĴŞĵƉÛÈĸĨąƮĀĕčÀÁĿïńƼşēƢĶĎũšóŦĄƆŘŒĊãĄĈļƱ"
        fit += "ŝēŐįčéńðĦÄŰŔĂńĎŉƉøÙłưĜŊáĀËƠŚùŞŐĤƍŋŠĀƪĦŸčûáćÀËťĴîĵƊŹÕƩōñņìƅØœÐġƌñĸîƥƘźŗąÆŢĹäÕƉŪÀ×őƆĕĥàĤũõÞŒŖŚƙŃÀĨēŘŀÁƠòƫƵĮŦĔŜœđƪäýŧńƨÜƣŊıÎÁŸõĥÜĘÅŐŔưƘÍÈŃæĬĝÂÄƓŲÔİÀĩōĠāÆīŨëūšŞóŃƋĳĪûŢÄýĕŊŦĊÀÃĢì"
        fit += "ĆĀŮòĭćÐÀħƀĠÀƐæƄĐĊƑðĻçƀčĒŲ÷ăÁàĽŨÀÉùèÛŃĬƿşƥƲőÒéƲĞūĹæÝóÊĠŒñĨìƤĹĬÓâĀšÔÚĲýƁŐÆņðØöŀŋƃľôâÃöîĕÂĩƙÊøÀğŋƭĻůõİíƋęĪßâƬĎżøóŵàòÄƥÀÀĲŴƆŸƨòİħÐÁŧžƇÀÅİƯêĳĶĺƔĢƜêĥĈŊÏđŇÄƣċƈłņŊŧĚÀÂƄñƆƺƀÛƂŨŁőƖƲƞÁ"
        fit += "ƀ÷łĳŇĠāćŨĉàÀûŋńƪÂēçøıÀÆăƅúƐÀÍġŪõÆŘƒÚãāāƕŅéÁũĨøÀÕŢŬĕĊšāćƁÀĐţŤĲŎƘÛÂĠìÁĿţƴÞŁƏđƨûćĄƚśóĂĦČűÿâƄĔŉÉàƓĨƪƋĤŃæĬĝÂÇĂƀÀËÇÌåńƄĬōƑũƹÿćƭðåƶÒƁÆéÐÜƃŔÚńāĦíØóÅďĉƥàŤÄŴŖƒƢĝāèáÂàóƸĿČƹŞóŦİŎÑŲôĆĈƁ×"
        fit += "àĄÄŀÏƱƼÿćƠƻÜãŀóņĠĖÊŁĈèÄƠŘÒÂÐþÈàŝŁŞŐþÐùƠÀ×òżĕƪŐņÏáĴĤČŁŎéťðťƆûēūàŤƍĚřŠÀĖÜƃĨâČŝũƄÀüĎġÕĚÀÅâţŔęÏâäøņŐŲÔĂĈāÇàƄÔłéÅÚŢŇƀƷÞŃƌĸŏÁƞûŇĨƬÝģŪŁƚœƹÅæħũŵŴÀÃķĮƍƕź÷öƤƜěŃįĤķƠžāĉƁŰàČćŚƒõÀÁƧăÈĝÚâ"
        fit += "ƔĠŋőŊÙĂŧåËáƄöņŐŢÓĂĈąÈãäĞŌƐĨÿčæýÇċüĂƨàóĢƥĐúÖÀÃćĨƍÕŢôöńƐĚÃÿħƌƵơƤŀƉÅÌŚĚģÉůûÐÀÍŃƌïŀŸÒüĹƇŦÁóâĶÛńŐÀŖĒƂėĊƆďøƢÀËñĀıēĈÀÔƺŞÉÅÏøƚňÀÁĳîąƄŸÖưƮÆĀƀľÏšƠÿƁüƢŎàšŋÇŀÆƜƛěģīĭčťŴöĵŧŦËƤÔŜÛÂÅưĕĈĦŶÄ"
        fit += "ÀÌéĻïąŢİĆÐŶÖĂèĄÄƐŅÄƶÈƐÂŖŁŞæŴƄŢŜÀÙƣûħČƥŜóĶĬƍęţóĦČƅŘòƶĜƋęģëĥČťŔòķŇƄÃäÔĪňƳĄæàōôÀÅƢżÖźƯÊłżĴłðĬ×łƠâĝƂƼøŇĐƖÜÃƠŵĮļĆŎĀÀÓĚĪĊũđéťäŢŔÑĢÞöƦŸƔŚŃĈĨƌƁąÓĂĤČÉıìåĄŠœŌļąƚāœöîŁÃňĎĢÀÀđĩÚƐĴŨÆÊŢÈū"
        fit += "ĕěËŇŇƎĶŤÆĪŎÀÕŒűĖšŰƉƳŜāÄƌĖƀƠÀŞÓąŲŜĉŁáÔšýúçöƧƎēÄÆřœÚÀÆƌƙěãģĬčŅŰõƶżƗĚƣěīčĥŬõĶŬƕĚţēĮĽŀžāĊŚŁŜÛÂÀÅĚùƍƒŰÈƁÜÊŬÐźƈƼčðŀÀāňïÅŠŬÔłİĊÈƁÈßÃŠĬÌŁİêÄƀňÏÁŠìÄŀİÊÀƀÇƾƿşƫƼĿįƩƼſŇƮƽşūƴľįƉƸſÇƞƻşīƬĽ"
        fit += "įũƴžŇƎƹşëƤļįŉưžÇžƷŞƫƜĻįĩƬŽŇŮƵŞūƔĺįĉƨŽÇŞƳŞīƌĹįéƤżŇŎƱŞëƄĸįÉƠżÇľƯŝƫżķĮƩƜŻŇĮƭŝūŴĶĮƉƘŻÇĞƫŝīŬĵĮũƔźŇĎƩŝëŤĴĮŉƐźÇþƧŜƫŜĳĮĩƌŹŇîƥŜūŔĲĮĉƈŹÇÞƣŜīŌıĮéƄŸŇÎơŜëńİĮÉƀŸÆƾƟśƫļįĭƪðÀÅéÆŌƀƒůõƌÀÚœđĪÍ"
        fit += "ýŧôƖŘƒƚēĉĩÏÀÀ×ƈèħÊħÎŌƀÀƉřëäĤĬŉŐŲÆþƇŘƫÜģĬĩŌűņîƅŘūÔĢĬĉňűÆÞƃŘīÌĸÀÀòāăæŖŘƀÀÐÌŢŀÀÀÀÂÀÖŲŷÜĠüƈÀÞƀÄƌėřţÀÂŬËÏšƬĤÀÎàŁưĕĈĦŶÄÀÂŵėêÐĨÀĀØÂÍƋĀÀƔĈÀÁĀČƀáĚÊİŢ÷ćÒųåàŸÎÂƐÖÂŖÚƋĘċñÅàųƦĽÏŉưþƇżŨŕÂŞ"
        fit += "ēŕƲƍėƫøÃŀĠÊÁãÀÁĶŐÙűĲŨÜĂĳÐÀăŨŝøÖœŞĨńƸłÆÌŀÀŧĀÖøÀÀƚŸŗÂƟĕêšĉäŴŐŏÑƂëąĈťÆàäÂŀÏƁƩüŧĴƭŝŃŬĴŎĩƋøƧÈƟśƣĸĭōŁůõĆŜƍÙĂƌęĊƱĝëĥĤŬÕĲņċŉĩìåăŐĥŌšŌðÅĈŨÔłĸĎÈıÌáĄØŀÎŁƌ÷ņŠŦÔłİăÆĀƄÍŁŠÜÂāĦƠÀàĲÌřűĴÈÚƒƋ"
        ndNqle.lines.add().txtExec = f"txtMaliciousCodeExecAsm = \"{fit}\""
        ndNqle.lines.add().txtExec = "dict_valToIco = {dv.value:dv.identifier for _dk, dv in bpy.types.UILayout.bl_rna.functions['prop'].parameters['icon'].enum_items.items()}"
        ndNqle.lines.add().txtExec = "def Decode(tree):"
        ndNqle.lines.add().txtExec = "    list_addedNodes = []"
        ndNqle.lines.add().txtExec = "    numBits = 0"
        ndNqle.lines.add().txtExec = "    for ch in (txtMaliciousCodeExecAsm):"
        ndNqle.lines.add().txtExec = "        numBits <<= 8"
        ndNqle.lines.add().txtExec = "        numBits += ord(ch)-192"
        ndNqle.lines.add().txtExec = "    dict_node = {}"
        ndNqle.lines.add().txtExec = "    list_readData = [0, 5, 32, 0] #phase couBits couPow couRead"
        ndNqle.lines.add().txtExec = "    list_accData = []"
        ndNqle.lines.add().txtExec = "    while True:"
        ndNqle.lines.add().txtExec = "        data = numBits%list_readData[2]"
        ndNqle.lines.add().txtExec = "        numBits >>= list_readData[1]"
        ndNqle.lines.add().txtExec = "        list_readData[3] += 1"
        ndNqle.lines.add().txtExec = "        list_accData.append(data)"
        ndNqle.lines.add().txtExec = "        match list_readData[0]:"
        ndNqle.lines.add().txtExec = "            case 0:"
        ndNqle.lines.add().txtExec = "                if data==0:"
        ndNqle.lines.add().txtExec = "                    dict_node['nameCat'] = \"\".join((\" \" if li==1 else chr(63+li)) for li in list_accData[:-1]).title()"
        ndNqle.lines.add().txtExec = "                    list_readData = [1, 1, 2, 0]"
        ndNqle.lines.add().txtExec = "            case 1:"
        ndNqle.lines.add().txtExec = "                dict_node['isShowCount'] = not not data"
        ndNqle.lines.add().txtExec = "                list_readData = [2, 12, 4096, 0]"
        ndNqle.lines.add().txtExec = "                list_accData.clear()"
        ndNqle.lines.add().txtExec = "            case 2:"
        ndNqle.lines.add().txtExec = "                if list_readData[3]==2:"
        ndNqle.lines.add().txtExec = "                    LUtS = lambda n: n if n<2048 else n-4096"
        ndNqle.lines.add().txtExec = "                    dict_node['location'] = (LUtS(list_accData[0]), LUtS(list_accData[1]))"
        ndNqle.lines.add().txtExec = "                    list_readData = [3, 9, 512, 0]"
        ndNqle.lines.add().txtExec = "            case 3:"
        ndNqle.lines.add().txtExec = "                dict_node['width'] = data"
        ndNqle.lines.add().txtExec = "                list_readData = [4, 11, 2048, 0]"
        ndNqle.lines.add().txtExec = "                list_accData.clear()"
        ndNqle.lines.add().txtExec = "            case 4:"
        ndNqle.lines.add().txtExec = "                if data==0:"
        ndNqle.lines.add().txtExec = "                    def AddNode(tree, dict_node):"
        ndNqle.lines.add().txtExec = "                        ndNew = tree.nodes.new(NodeIconShop.bl_idname)"
        ndNqle.lines.add().txtExec = "                        list_addedNodes.append(ndNew)"
        ndNqle.lines.add().txtExec = "                        for dk in dict_node.keys():"
        ndNqle.lines.add().txtExec = "                            if dk.__class__ is str:"
        ndNqle.lines.add().txtExec = "                                setattr(ndNew, dk, dict_node[dk])"
        ndNqle.lines.add().txtExec = "                        for li in dict_node[list]:"
        ndNqle.lines.add().txtExec = "                            ndNew.collIcons.add().name = li"
        ndNqle.lines.add().txtExec = "                    dict_node[list] = [dict_valToIco[li] for li in list_accData[:-1]]"
        ndNqle.lines.add().txtExec = "                    AddNode(tree, dict_node)"
        ndNqle.lines.add().txtExec = "                    if not numBits:"
        ndNqle.lines.add().txtExec = "                        break"
        ndNqle.lines.add().txtExec = "                    dict_node = {}"
        ndNqle.lines.add().txtExec = "                    list_readData = [0, 5, 32, 0]"
        ndNqle.lines.add().txtExec = "                    list_accData.clear()"
        ndNqle.lines.add().txtExec = "    return list_addedNodes"
        ndNqle.lines.add().txtExec = "from ManagerNodeTree.Main import Utils"
        ndNqle.lines.add().txtExec = "class NodeIconShop(bpy.types.Node):"
        ndNqle.lines.add().txtExec = "    bl_idname = 'NodeIconShop'"
        ndNqle.lines.add().txtExec = "    bl_label = \"Icon Shop\""
        ndNqle.lines.add().txtExec = "    bl_width_min = 40"
        ndNqle.lines.add().txtExec = "    collIcons: bpy.props.CollectionProperty(type=bpy.types.PropertyGroup)"
        ndNqle.lines.add().txtExec = "    nameCat: bpy.props.StringProperty(name=\"Category Name\", default=\"\")"
        ndNqle.lines.add().txtExec = "    isShowCount: bpy.props.BoolProperty(name=\"Show Count In Cat\", default=True)"
        ndNqle.lines.add().txtExec = "    def draw_label(self):"
        ndNqle.lines.add().txtExec = "        opa.BNode(self).typeinfo.nclass = 4"
        ndNqle.lines.add().txtExec = "        return \" \""
        ndNqle.lines.add().txtExec = "    def draw_buttons(self, context, layout):"
        ndNqle.lines.add().txtExec = "        if self.nameCat:"
        ndNqle.lines.add().txtExec = "            rowCenter = layout.row(align=True)"
        ndNqle.lines.add().txtExec = "            rowCenter.alignment = 'CENTER'"
        ndNqle.lines.add().txtExec = "            rowCat = rowCenter.row(align=True)"
        ndNqle.lines.add().txtExec = "            rowCat.alignment = 'CENTER'"
        ndNqle.lines.add().txtExec = "            rowCat.label(text=self.nameCat)"
        ndNqle.lines.add().txtExec = "            if self.isShowCount:"
        ndNqle.lines.add().txtExec = "                rowCount = rowCenter.row(align=True)"
        ndNqle.lines.add().txtExec = "                rowCount.alignment = 'CENTER'"
        ndNqle.lines.add().txtExec = "                rowCount.label(text=f\"({str(length(self.collIcons))})\")"
        ndNqle.lines.add().txtExec = "                rowCount.active = False"
        ndNqle.lines.add().txtExec = "        colPool = layout.column(align=True)"
        ndNqle.lines.add().txtExec = "        suNumMaxIcosPerRow = self.width//20-1"
        ndNqle.lines.add().txtExec = "        for cyc, ci in enumerate(self.collIcons):"
        ndNqle.lines.add().txtExec = "            if not(cyc%suNumMaxIcosPerRow):"
        ndNqle.lines.add().txtExec = "                rowPool = colPool.row(align=True)"
        ndNqle.lines.add().txtExec = "            fit = f\"bpy.context.window_manager.clipboard = \\\"{ci.name}\\\"; \"+\"self.report({'INFO'}, bpy.context.window_manager.clipboard)\""
        ndNqle.lines.add().txtExec = "            rowPool.operator(Utils.OpSimpleExec.bl_idname, text=\"\", icon=ci.name).exc = fit"
        ndNqle.lines.add().txtExec = "bpy.utils.register_class(NodeIconShop)"
        ndNqle.lines.add().txtExec = "Utils.GenPlaceNodesToCursor(bpy.context, Decode, isActiveFromList=True)"
        ndNqle.lines.add().txtExec = "self.hide = True; self.location.y -= 30"
        ndNqle.count = ndNqle.count
        return list_addedNodes
    def ViewRegionToCanon(tree, meta_cat="3Dev"):
        list_addedNodes = []
        ndNlae = tree.nodes.new(Nodes.NodeLayoutAndExec.bl_idname)
        list_addedNodes.append(ndNlae)
        ndNlae.name = "ViewRegionToCanon"
        ndNlae.label = "v2d 1:1"
        ndNlae.txtCode = "def Layout(ly):"
        ndNlae.txtCode += "\n  ly.operator(bop, text=\"View region to canon and 1:1\")"
        ndNlae.txtCode += "\ndef Execute(op):"
        ndNlae.txtCode += "\n  reg = bpy.context.region\n  bV2d = opa.View2D(reg.view2d)"
        ndNlae.txtCode += "\n  bV2d.cur.xmin = -reg.width/2\n  bV2d.cur.ymin = -reg.height/2\n  bV2d.cur.xmax = reg.width/2\n  bV2d.cur.ymax = reg.height/2"
        return list_addedNodes
    def EditEditorZoomLimit(tree, meta_cat="3Dev"):
        from bpy import context
        from .. import opa
        list_addedNodes = []
        ndNsf0 = tree.nodes.new(Nodes.NodeSolemnFloat.bl_idname)
        list_addedNodes.append(ndNsf0)
        ndNsf0.width = 220
        ndNsf0.name = "EditEditorZoomLimit1"
        bV2d = opa.View2D(context.region.view2d)
        ndNsf0.float = bV2d.minzoom
        ndNsf1 = tree.nodes.new(Nodes.NodeSolemnFloat.bl_idname)
        list_addedNodes.append(ndNsf1)
        ndNsf1.width = 220
        ndNsf1.name = "EditEditorZoomLimit2"
        ndNsf1.float = bV2d.maxzoom
        ndNlae = tree.nodes.new(Nodes.NodeLayoutAndExec.bl_idname)
        list_addedNodes.append(ndNlae)
        ndNlae.width = 330
        ndNlae.name = "EditEditorZoomLimit0"
        ndNlae.label = "Edit zoom limit"
        ndNlae.txtCode = "def Layout(ly):"
        ndNlae.txtCode += "\n  reg = bpy.context.region"
        ndNlae.txtCode += "\n  bV2d = opa.View2D(reg.view2d)"
        ndNlae.txtCode += "\n  col = ly.column(align=True)"
        ndNlae.txtCode += "\n  col.label(text=f\"Current max zoom: {bV2d.maxzoom}\")"
        ndNlae.txtCode += "\n  col.label(text=f\"Current zoom: {reg.height/(bV2d.cur.ymax-bV2d.cur.ymin)}\")"
        ndNlae.txtCode += "\n  col.label(text=f\"Current min zoom: {bV2d.minzoom}\")"
        ndNlae.txtCode += "\n  col = ly.column(align=True)"
        ndNlae.txtCode += "\n  for ch in \"21\":"
        ndNlae.txtCode += f"\n    if ch==\"1\": nd = self.id_data.nodes.get(\"{ndNsf0.name}\")"
        ndNlae.txtCode += f"\n    else: nd = self.id_data.nodes.get(\"{ndNsf1.name}\")"
        ndNlae.txtCode += "\n    if not nd: return"
        ndNlae.txtCode += "\n    row = col.row(align=True)"
        ndNlae.txtCode += "\n    if (ch==\"2\")and(nd.float<1.0)or(ch==\"1\")and(nd.float>1.0):"
        ndNlae.txtCode += "\n      row.label(icon='ERROR')"
        ndNlae.txtCode += "\n    row.prop(nd,'float', text=f\"New {['min','max'][int(ch)-1]} limit:\")"
        ndNlae.txtCode += "\n  ly.operator(bop, text=\"Write new limits\")"
        ndNlae.txtCode += "\ndef Execute(op):"
        ndNlae.txtCode += "\n  bV2d = opa.View2D(bpy.context.region.view2d)"
        ndNlae.txtCode += "\n  nd2 = self.id_data.nodes['EditEditorZoomLimit2']"
        ndNlae.txtCode += "\n  nd1 = self.id_data.nodes['EditEditorZoomLimit1']"
        ndNlae.txtCode += "\n  if nd2.float>=nd1.float:"
        ndNlae.txtCode += "\n    bV2d.maxzoom = nd2.float"
        ndNlae.txtCode += "\n    bV2d.minzoom = nd1.float"
        ndNsf0.label = "Float node for "+ndNlae.label
        ndNsf1.label = ndNsf0.label
        list_addedNodes.insert(0, list_addedNodes[2])
        return list_addedNodes[:-1]
    def Dummy(tree, meta_cat1="9Dummy"):
        list_addedNodes = []
        ndAaa = tree.nodes.new(Nodes.NodeAaa.bl_idname)
        list_addedNodes.append(ndAaa)
        ndAaa.name = "Dummy"
        return list_addedNodes
    dict_catPae = {}
    for dk, dv in dict(locals()).items():
        if (callable(dv))and('meta_cat' in dv.__code__.co_varnames):
            dict_catPae.setdefault(dv.__defaults__[0], []).append(dk) #dv.__code__.co_name
    list_catPue = [(li[0][1:], li[1]) for li in sorted(dict_catPae.items(), key=lambda a: a[0][0])] #list(dict_catPae.items())
    del dict_catPae
