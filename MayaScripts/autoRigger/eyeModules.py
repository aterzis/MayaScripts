'''
(c) Arthur Terzis 2011

Eye Module implementation

Place to store different Eye Module builders. All classes should take in a rigGuides
class to build the rig component from

All Modules inherit from modules.BaseModules which contains generic methods

'''

from ..utils import controllers
from . import rigGuides
from . import modules
from ..utils import utils
from maya import cmds


class SimpleEyeRig(modules.BaseModule):
    '''
         creates a simple eye rig - with lidstick follow and blink/lid controls
         No automatic collision on the eyes
    '''    
    
    
    def __init__(self, guide=rigGuides.EyeGuide()):
        '''
        guide = rigGuide.EyeGuide object
        '''
        modules.BaseModule.__init__(self, guide)
        
        self._eye_guide = guide.joint_order[0:2]
        self._uEye_guide = guide.joint_order[2:4]
        self._lEye_guide = guide.joint_order[4:]
        
        self._eye_jnts = list()
        self._upperLid_jnts = list()
        self._lowerLid_jnts = list()
    
    
    def _create_joints(self):
        '''
        override the BaseModule method to create the specialised eye heirarchy
        '''
        
        self._eye_jnts = cmds.duplicate(self._eye_guide[0], n=self._eye_guide[0].replace("gui", "jnt"), po=True)
        self._eye_jnts.extend(cmds.duplicate(self._eye_guide[1], n=self._eye_guide[1].replace("gui", "jnt"), po=True))
        cmds.parent(self._eye_jnts[1], self._eye_jnts[0])
        
        self._upperLid_jnts = cmds.duplicate(self._uEye_guide[0], n=self._uEye_guide[0].replace("gui","jnt"), po=True)
        self._upperLid_jnts.extend(cmds.duplicate(self._uEye_guide[1], n=self._uEye_guide[1].replace("gui","jnt"), po=True))
        cmds.parent(self._upperLid_jnts[1], self._upperLid_jnts[0])

        self._lowerLid_jnts = cmds.duplicate(self._lEye_guide[0], n=self._lEye_guide[0].replace("gui", "jnt"), po=True)
        self._lowerLid_jnts.extend(cmds.duplicate(self._lEye_guide[1], n=self._lEye_guide[1].replace("gui", "jnt"), po=True))
        cmds.parent(self._lowerLid_jnts[1], self._lowerLid_jnts[0])
        
        upper = self._upperLid_jnts[0].replace("_0", "Offset_0")
        upper_offset = cmds.duplicate(self._upperLid_jnts[0], po=True, n=upper)[0]
        cmds.parent(self._upperLid_jnts[0], upper_offset)
        self._upperLid_jnts.insert(0, upper_offset)
    
        lower = self._lowerLid_jnts[0].replace("_0", "Offset_0")
        lower_offset = cmds.duplicate(self._lowerLid_jnts[0], po=True, n=lower)[0]
        cmds.parent(self._lowerLid_jnts[0], lower_offset)
        self._lowerLid_jnts.insert(0, lower_offset)
        
        #label joints
        utils.label_joint(self._eye_jnts[0], self._side, typ="Other", label=self._eye_jnts[0].split("_")[2])
        utils.label_joint(self._eye_jnts[1], self._side, typ="Other", label=self._eye_jnts[1].split("_")[2])
        
        utils.label_joint(self._upperLid_jnts[0], self._side, typ="Other", label=self._upperLid_jnts[0].split("_")[2])
        utils.label_joint(self._upperLid_jnts[1], self._side, typ="Other", label=self._upperLid_jnts[1].split("_")[2])
        utils.label_joint(self._upperLid_jnts[2], self._side, typ="Other", label=self._upperLid_jnts[2].split("_")[2])
        
        utils.label_joint(self._lowerLid_jnts[0], self._side, typ="Other", label=self._lowerLid_jnts[0].split("_")[2])
        utils.label_joint(self._lowerLid_jnts[1], self._side, typ="Other", label=self._lowerLid_jnts[1].split("_")[2])
        utils.label_joint(self._lowerLid_jnts[2], self._side, typ="Other", label=self._lowerLid_jnts[2].split("_")[2])
        
        #create the look at joint for the look override controls
        self._lookAt_jnt = cmds.duplicate(self._eye_jnts[0], n="%s_jnt_eyeLookAt_0" %self._side, po=True)[0]
    
        self.skin_eye = self._eye_jnts[0]
        self.skin_lower_lid = self._lowerLid_jnts[0]
        self.skin_upper_lid = self._upperLid_jnts[0]
        
    def _create_attribute_node(self):
        '''
        the attribute node is where all the limits and settings are stored
        '''
        self._attr_node = cmds.group(n="%s_eyeSettings" %self._side, em=True)
        utils.lock_hide(self._attr_node)
        
        # note - default values only - to be adjusted for each face rig
        cmds.addAttr(self._attr_node, ln="eyeRangeUp", k=True, dv=35)
        cmds.addAttr(self._attr_node, ln="eyeRangeDown", k=True, dv=-40)
        cmds.addAttr(self._attr_node, ln="eyeRangeLeft", k=True, dv=40)
        cmds.addAttr(self._attr_node, ln="eyeRangeRight", k=True, dv=-32)
    
        cmds.addAttr(self._attr_node, ln="upperLidBlinkMax", k=True, dv=-45)
        cmds.addAttr(self._attr_node, ln="lowerLidBlinkMax", k=True, dv=10)
        
        cmds.addAttr(self._attr_node, ln="upperLidOpen", k=True, dv=20)
        cmds.addAttr(self._attr_node, ln="upperLidClosed", k=True, dv=-50)
        cmds.addAttr(self._attr_node, ln="lowerLidOpen", k=True, dv=-15)
        cmds.addAttr(self._attr_node, ln="lowerLidClosed", k=True, dv=15)
        
        cmds.addAttr(self._attr_node, ln="upperLidFollowMult", k=True, min=0, max=1, dv=0.3)
        cmds.addAttr(self._attr_node, ln="lowerLidFollowMult", k=True, min=0, max=1, dv=0.2)
        cmds.addAttr(self._attr_node, ln="hoizontalFollowMult", k=True, min=0, max=1, dv=0.3)
 

    def _create_eye_controls(self):
        '''
        create the face eye controls
        '''
        self._eye_control = controllers.SquareFaceControl("%s_ctl_eye" %self._side)
        self._eye_control.set_position(obj=self._guide.controller_guides["eye"])
        self._eye_control.set_colour(self._colour)
        self._uLid_control = controllers.VerticalFaceControl("%s_ctl_uLid" %self._side)
        self._uLid_control.set_position(obj=self._guide.controller_guides["uLid"])
        self._uLid_control.set_colour(self._colour)
        self._lLid_control = controllers.VerticalFaceControl("%s_ctl_lLid" %self._side)
        self._lLid_control.set_position(obj=self._guide.controller_guides["lLid"])
        self._lLid_control.set_colour(self._colour)
        self._blink_control = controllers.VerticalFaceControl("%s_ctl_blink" %self._side, orient="bottom")
        self._blink_control.set_position(obj=self._guide.controller_guides["blink"])
        self._blink_control.set_colour(self._colour)
        self._blink_control.set_position(rot=[180,0,0])
        self._look_control = controllers.CircleControl("%s_ctl_eyeLookAt" %self._side)
        self._look_control.set_colour(self._colour)
        self._look_control.set_position(rot=[90, 0, 0], obj=self._lookAt_jnt)
        #set position to look at joint, then translate it forward
        self._look_control.set_position(trans=[0,0,15], sc=[3,3,3])
        self._look_control.hide_rotation()
        self._look_control.hide_scale()

        self.controls = [self._eye_control.name, self._lLid_control.name, self._uLid_control.name, self._blink_control.name, self._look_control.name]
 

    def _setup_eye_controls(self):
        '''
        setup the dual eye controls
        '''        
        
        leftRight = cmds.createNode("setRange", n="%s_LREyeRange" %self._side)
        upDown = cmds.createNode("setRange", n="%s_UDEyeRange" %self._side)
        LR_pma = cmds.createNode("plusMinusAverage", n="%s_LRpma" %self._side)
        UD_pma = cmds.createNode("plusMinusAverage", n="%s_UDpma" %self._side)
        LR_clamp = cmds.createNode("clamp", n="%s_LR_clamp" %self._side)
        UD_clamp = cmds.createNode("clamp", n="%s_UD_clamp" %self._side)
        
        cmds.aimConstraint(self._look_control.name, self._lookAt_jnt, mo=True)
        
        cmds.connectAttr("%s.tx" %self._eye_control.ctl, "%s.vx" %leftRight)
        cmds.connectAttr("%s.tx" %self._eye_control.ctl, "%s.vy" %leftRight)
        cmds.connectAttr("%s.eyeRangeLeft" %self._attr_node, "%s.my" %leftRight)
        cmds.connectAttr("%s.eyeRangeRight" %self._attr_node, "%s.nx" %leftRight)
        cmds.setAttr("%s.onx" %leftRight, -1)
        cmds.setAttr("%s.omy" %leftRight, 1)
        cmds.connectAttr("%s.ox" %leftRight, "%s.i1[0]" %LR_pma)
        cmds.connectAttr("%s.oy" %leftRight, "%s.i1[1]" %LR_pma)
        cmds.connectAttr("%s.ry" %self._lookAt_jnt, "%s.i1[2]" %LR_pma)
        cmds.connectAttr("%s.o1" %LR_pma, "%s.ipr" %LR_clamp)
        cmds.connectAttr("%s.eyeRangeRight" %self._attr_node, "%s.mnr" %LR_clamp)
        cmds.connectAttr("%s.eyeRangeLeft" %self._attr_node, "%s.mxr" %LR_clamp)
        cmds.connectAttr("%s.opr" %LR_clamp, "%s.ry" %self._eye_jnts[0])
    
        cmds.connectAttr("%s.ty" %self._eye_control.ctl, "%s.vx" %upDown)
        cmds.connectAttr("%s.ty" %self._eye_control.ctl, "%s.vy" %upDown)
        cmds.connectAttr("%s.eyeRangeDown" %self._attr_node, "%s.ny" %upDown)
        cmds.connectAttr("%s.eyeRangeUp" %self._attr_node, "%s.mx" %upDown)
        cmds.setAttr("%s.ony" %upDown, -1)
        cmds.setAttr("%s.omx" %upDown, 1)
        cmds.connectAttr("%s.ox" %upDown, "%s.i1[0]" %UD_pma)
        cmds.connectAttr("%s.oy" %upDown, "%s.i1[1]" %UD_pma)
        cmds.connectAttr("%s.rz" %self._lookAt_jnt, "%s.i1[2]" %UD_pma)
        cmds.connectAttr("%s.o1" %UD_pma, "%s.ipr" %UD_clamp)
        cmds.connectAttr("%s.eyeRangeDown" %self._attr_node, "%s.mnr" %UD_clamp)
        cmds.connectAttr("%s.eyeRangeUp" %self._attr_node, "%s.mxr" %UD_clamp)
        cmds.connectAttr("%s.opr" %UD_clamp, "%s.rz" %self._eye_jnts[0])        
        
        
    def _setup_lidStick(self):
        '''
        setup the lidstick/follow of the lids using the offset joints
        '''
        #set up the lidstick using the offset joint
        upperMult = cmds.createNode("multiplyDivide", n="%s_upperLidMultiplier" %self._side)
        lowerMult = cmds.createNode("multiplyDivide", n="%s_lowerLidMultiplier" %self._side)
        
        cmds.connectAttr("%s.ry" %self._eye_jnts[0], "%s.i1y" %upperMult)
        cmds.connectAttr("%s.rz" %self._eye_jnts[0], "%s.i1z" %upperMult)
        cmds.connectAttr("%s.hoizontalFollowMult" %self._attr_node, "%s.i2y" %upperMult)
        cmds.connectAttr("%s.upperLidFollowMult" %self._attr_node, "%s.i2z" %upperMult)
        cmds.connectAttr("%s.oy" %upperMult, "%s.ry" %self._upperLid_jnts[0])
        cmds.connectAttr("%s.oz" %upperMult, "%s.rz" %self._upperLid_jnts[0])
        
        cmds.connectAttr("%s.ry" %self._eye_jnts[0], "%s.i1y" %lowerMult)
        cmds.connectAttr("%s.rz" %self._eye_jnts[0], "%s.i1z" %lowerMult)
        cmds.connectAttr("%s.hoizontalFollowMult" %self._attr_node, "%s.i2y" %lowerMult)
        cmds.connectAttr("%s.lowerLidFollowMult" %self._attr_node, "%s.i2z" %lowerMult)
        cmds.connectAttr("%s.oy" %lowerMult, "%s.ry" %self._lowerLid_jnts[0])
        cmds.connectAttr("%s.oz" %lowerMult, "%s.rz" %self._lowerLid_jnts[0])


    def _setup_blink(self):        
        '''
        create the individual lid rigs and the blink setup
        '''
        #create nodes for the lids / blink
        upper_range = cmds.createNode("setRange", n="%s_upperLidRange" %self._side)
        upper_range_pma = cmds.createNode("plusMinusAverage", n="%s_upperLidPMA" %self._side)
        upper_remap = cmds.createNode("remapValue", n="%s_upperLidRemap" %self._side)
        upper_remap_pma = cmds.createNode("plusMinusAverage", n="%s_upperLidRemapPMA" %self._side)
        upper_clamp = cmds.createNode("clamp", n="%s_upperLidClamp" %self._side)
        
        lower_range = cmds.createNode("setRange", n="%s_lowerLidRange" %self._side)
        lower_range_pma = cmds.createNode("plusMinusAverage", n="%s_lowerLidPMA" %self._side)
        lower_remap = cmds.createNode("remapValue", n="%s_lowerLidRemap" %self._side)
        lower_remap_pma = cmds.createNode("plusMinusAverage", n="%s_lowerLidRemapPMA" %self._side)
        lower_clamp = cmds.createNode("clamp", n="%s_lowerLidClamp" %self._side)
        
        #set up the lid controls
        cmds.connectAttr("%s.upperLidClosed" %self._attr_node, "%s.ny" %upper_range)
        cmds.connectAttr("%s.upperLidOpen" %self._attr_node, "%s.mx" %upper_range)
        cmds.connectAttr("%s.ty" %self._uLid_control.ctl, "%s.vx" %upper_range)
        cmds.connectAttr("%s.ty" %self._uLid_control.ctl, "%s.vy" %upper_range)
        cmds.setAttr("%s.ony" %upper_range, -1)
        cmds.setAttr("%s.omx" %upper_range, 1)
        cmds.connectAttr("%s.ox" %upper_range, "%s.i1[0]" %upper_range_pma)
        cmds.connectAttr("%s.oy" %upper_range, "%s.i1[1]" %upper_range_pma)
        cmds.connectAttr("%s.ty" %self._blink_control.ctl, "%s.i" %upper_remap)
        cmds.connectAttr("%s.upperLidBlinkMax" %self._attr_node, "%s.omx" %upper_remap)
        cmds.setAttr("%s.imn" %upper_remap, 0)
        cmds.setAttr("%s.imx" %upper_remap, 1)
        cmds.connectAttr("%s.o1" %upper_range_pma, "%s.i1[0]" %upper_remap_pma)
        cmds.connectAttr("%s.ov" %upper_remap, "%s.i1[1]" %upper_remap_pma)
        cmds.connectAttr("%s.o1" %upper_remap_pma, "%s.ipr" %upper_clamp)
        cmds.connectAttr("%s.upperLidClosed" %self._attr_node, "%s.mnr" %upper_clamp)
        cmds.connectAttr("%s.upperLidOpen" %self._attr_node, "%s.mxr" %upper_clamp)
        cmds.connectAttr("%s.opr" %upper_clamp, "%s.rz" %self._upperLid_jnts[1])
        
        cmds.connectAttr("%s.lowerLidClosed" %self._attr_node, "%s.mx" %lower_range)
        cmds.connectAttr("%s.lowerLidOpen" %self._attr_node, "%s.ny" %lower_range)
        cmds.connectAttr("%s.ty" %self._lLid_control.ctl, "%s.vx" %lower_range)
        cmds.connectAttr("%s.ty" %self._lLid_control.ctl, "%s.vy" %lower_range)
        cmds.setAttr("%s.ony" %lower_range, -1)
        cmds.setAttr("%s.omx" %lower_range, 1)
        cmds.connectAttr("%s.ox" %lower_range, "%s.i1[0]" %lower_range_pma)
        cmds.connectAttr("%s.oy" %lower_range, "%s.i1[1]" %lower_range_pma)
        cmds.connectAttr("%s.ty" %self._blink_control.ctl, "%s.i" %lower_remap)
        cmds.connectAttr("%s.lowerLidBlinkMax" %self._attr_node, "%s.omx" %lower_remap)
        cmds.setAttr("%s.imn" %lower_remap, 0)
        cmds.setAttr("%s.imx" %lower_remap, 1)
        cmds.connectAttr("%s.o1" %lower_range_pma, "%s.i1[0]" %lower_remap_pma)
        cmds.connectAttr("%s.ov" %lower_remap, "%s.i1[1]" %lower_remap_pma)
        cmds.connectAttr("%s.o1" %lower_remap_pma, "%s.ipr" %lower_clamp)
        cmds.connectAttr("%s.lowerLidClosed" %self._attr_node, "%s.mxr" %lower_clamp)
        cmds.connectAttr("%s.lowerLidOpen" %self._attr_node, "%s.mnr" %lower_clamp)
        cmds.connectAttr("%s.opr" %lower_clamp, "%s.rz" %self._lowerLid_jnts[1])


    def _clean(self):
        '''
        general clean up of the rig
        '''
        gui_nodes = [self._eye_guide[0], self._uEye_guide[0], self._lEye_guide[0]]
        gui_nodes +=  [self._guide.controller_guides["eye"], self._guide.controller_guides["lLid"], 
                      self._guide.controller_guides["uLid"], self._guide.controller_guides["blink"]]
        
        self.gui_grp = cmds.group(gui_nodes, n="%s_eye_guides" %self._side)
        cmds.setAttr("%s.v" %self.gui_grp, 0)    
        utils.lock_hide(self.gui_grp, v=False)
        
        self.ctls_grp = cmds.group(self.controls, n="%s_eye_controls" %self._side)
        rig_nodes = [self._attr_node, self._eye_jnts[0], self._lowerLid_jnts[0], self._upperLid_jnts[0], self._lookAt_jnt]
        self.rig_grp  = self._attr_node
        
        if cmds.objExists("C_jnt_skull_0"):
            cmds.parent(rig_nodes[1:], "C_jnt_skull_0") 
        
        self.joints_grp = cmds.group([self._upperLid_jnts[0], self._lowerLid_jnts[0], self._eye_jnts[0], self._lookAt_jnt], n="%s_eye_joints" %self._side)
                    
        mod = [self.joints_grp, self.gui_grp, self.rig_grp, self.ctls_grp, self._attr_node]
        self.module_grp = cmds.group(mod, n="%s_eye_module_0" %self._side)
        
        self.input_nodes = self.module_grp
        

    def create(self):
        '''
        to be run after initializing the class to create the eye rig
        '''
        self._create_joints()
        self._create_attribute_node()
        self._create_eye_controls()
        self._setup_eye_controls()
        self._setup_lidStick()
        self._setup_blink()
        self._clean()        
        
        
        