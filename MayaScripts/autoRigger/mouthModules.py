from . import controllers
from . import rigGuides
from . import modules
from . import utils
from maya import cmds


class SimpleJawRig(modules.BaseModule):
    '''
         creates a simple jaw rig - with rotate and translate controls
    '''    
    
    
    def __init__(self, guide=rigGuides.JawGuide()):
        '''
        guide = rigGuide.JawGuide object
        '''
        modules.BaseModule.__init__(self, guide)
        self._jaw_jnts = list()


    def _create_joints(self):
        self._jaw_jnts = list()
        
        #use the skull joint created from the neck setup if it exists
        if cmds.objExists("C_jnt_skull_0"):
            gui_jnts = self._guide.joint_order[1:]
            self.parent=True
        else: # create a new joint
            gui_jnts = self._guide.joint_order
            self.parent=False
    
        cmds.select(clear=True)
        joints = cmds.duplicate(gui_jnts, rc=True)
        
        for gui, jnt in zip(gui_jnts, joints):
            new_name = gui.replace("gui", "jnt")
            jnt_name = cmds.rename(jnt,new_name)
            self._jaw_jnts.append(jnt_name)
         
        if self.parent:
            self._jaw_jnts.insert(0, "C_jnt_skull_0")
            cmds.parent(self._jaw_jnts[1], "C_jnt_skull_0")
              
        trans_joint = cmds.duplicate(self._jaw_jnts[1], po=True, n="C_jnt_jawTrans_0")[0]
        cmds.parent(self._jaw_jnts[1], trans_joint)
        self._jaw_jnts.insert(1, trans_joint)
        
        #label joints
        for joint in self._jaw_jnts:
            utils.label_joint(joint, self._side, typ="Other", label=joint.split("_")[2])
        
        
    def _create_attribute_node(self):
        '''
        the attribute node is where all the limits and settings are stored
        default values only - to be adjusted for each face rig
        '''
        self._attr_node = cmds.group(n="%s_jawSettings" %self._side, em=True)
        utils.lock_hide(self._attr_node)
        
        cmds.addAttr(self._attr_node, ln="rotDown", k=True, dv=-10)
        cmds.addAttr(self._attr_node, ln="rotUp", k=True, dv=10)
        cmds.addAttr(self._attr_node, ln="rotLeft", k=True, dv=8)
        cmds.addAttr(self._attr_node, ln="rotRight", k=True, dv=-8)
    
        cmds.addAttr(self._attr_node, ln="transDown", k=True, dv=-0.5)
        cmds.addAttr(self._attr_node, ln="transUp", k=True, dv=0.5)
        cmds.addAttr(self._attr_node, ln="transLeft", k=True, dv=0.3)
        cmds.addAttr(self._attr_node, ln="transRight", k=True, dv=-0.3)
        
        cmds.addAttr(self._attr_node, ln="jawFwd", k=True, dv=0.6)
        cmds.addAttr(self._attr_node, ln="jawBack", k=True, dv=-0.5)
    
    
    def _create_controllers(self):
        '''
        create the face jaw controls
        '''
        self._jawRot_control = controllers.SquareFaceControl("%s_ctl_jawRot" %self._side)
        self._jawRot_control.set_position(obj=self._guide.controller_guides["jawRot"])
        
        self._jawTrans_control = controllers.SquareFaceControl("%s_ctl_jawTrans" %self._side)
        self._jawTrans_control.set_position(obj=self._guide.controller_guides["jawTrans"])
        
        self._jawFwBk_control = controllers.HorizontalFaceControl("%s_ctl_jawFwBk" %self._side)
        self._jawFwBk_control.set_position(obj=self._guide.controller_guides["jawFwBk"])
        
        self.controls = [self._jawRot_control.name, self._jawTrans_control.name, self._jawFwBk_control.name]
        self.gui = [self._guide.controller_guides["jawFwBk"], self._guide.controller_guides["jawTrans"], self._guide.controller_guides["jawRot"]]
    
    
    def _setup_rotate(self):
        rotY_setRange = cmds.createNode("setRange", n="%s_jawRYSetRange" %self._side)
        rotZ_setRange = cmds.createNode("setRange", n="%s_jawRZSetRange" %self._side)
        rotY_pma = cmds.createNode("plusMinusAverage", n="%s_jawRYpma" %self._side)
        rotZ_pma = cmds.createNode("plusMinusAverage", n="%s_jawRZpma" %self._side)
        
        cmds.connectAttr("%s.tx" %self._jawRot_control.ctl, "%s.vx" %rotY_setRange)
        cmds.connectAttr("%s.tx" %self._jawRot_control.ctl, "%s.vy" %rotY_setRange)
        cmds.connectAttr("%s.rotLeft" %self._attr_node, "%s.mx" %rotY_setRange)
        cmds.connectAttr("%s.rotRight" %self._attr_node, "%s.ny" %rotY_setRange)
        cmds.setAttr("%s.omx" %rotY_setRange, 1)
        cmds.setAttr("%s.ony" %rotY_setRange, -1)
        cmds.connectAttr("%s.ox" %rotY_setRange, "%s.i1[0]" %rotY_pma)
        cmds.connectAttr("%s.oy" %rotY_setRange, "%s.i1[1]" %rotY_pma)
        cmds.connectAttr("%s.o1" %rotY_pma, "%s.ry" %self._jaw_jnts[2])
        
        cmds.connectAttr("%s.ty" %self._jawRot_control.ctl, "%s.vx" %rotZ_setRange)
        cmds.connectAttr("%s.ty" %self._jawRot_control.ctl, "%s.vy" %rotZ_setRange)
        cmds.connectAttr("%s.rotUp" %self._attr_node, "%s.mx" %rotZ_setRange)
        cmds.connectAttr("%s.rotDown" %self._attr_node, "%s.ny" %rotZ_setRange)
        cmds.setAttr("%s.omx" %rotZ_setRange, 1)
        cmds.setAttr("%s.ony" %rotZ_setRange, -1)
        cmds.connectAttr("%s.ox" %rotZ_setRange, "%s.i1[0]" %rotZ_pma)
        cmds.connectAttr("%s.oy" %rotZ_setRange, "%s.i1[1]" %rotZ_pma)
        cmds.connectAttr("%s.o1" %rotZ_pma, "%s.rz" %self._jaw_jnts[2])
        
    
    def _setup_translate(self):
        tranZ_setRange = cmds.createNode("setRange", n="%s_jawTXSetRange" %self._side)
        tranY_setRange = cmds.createNode("setRange", n="%s_jawTYSetRange" %self._side)
        tranZ_pma = cmds.createNode("plusMinusAverage", n="%s_jawTXpma" %self._side)
        tranY_pma = cmds.createNode("plusMinusAverage", n="%s_jawTYpma" %self._side)
    
        cmds.connectAttr("%s.tx" %self._jawTrans_control.ctl, "%s.vx" %tranZ_setRange)
        cmds.connectAttr("%s.tx" %self._jawTrans_control.ctl, "%s.vy" %tranZ_setRange)
        cmds.connectAttr("%s.transLeft" %self._attr_node, "%s.mx" %tranZ_setRange)
        cmds.connectAttr("%s.transRight" %self._attr_node, "%s.ny" %tranZ_setRange)
        cmds.setAttr("%s.omx" %tranZ_setRange, 1)
        cmds.setAttr("%s.ony" %tranZ_setRange, -1)
        cmds.connectAttr("%s.ox" %tranZ_setRange, "%s.i2[0].i2x" %tranZ_pma)
        cmds.connectAttr("%s.oy" %tranZ_setRange, "%s.i2[1].i2x" %tranZ_pma)
        tx = cmds.getAttr("%s.tx" %self._jaw_jnts[1])
        cmds.setAttr("%s.i2[2].i2x" %tranZ_pma, tx)
        cmds.connectAttr("%s.o2x" %tranZ_pma, "%s.tx" %self._jaw_jnts[1])

        cmds.connectAttr("%s.ty" %self._jawTrans_control.ctl, "%s.vx" %tranY_setRange)
        cmds.connectAttr("%s.ty" %self._jawTrans_control.ctl, "%s.vy" %tranY_setRange)
        cmds.connectAttr("%s.transUp" %self._attr_node, "%s.mx" %tranY_setRange)
        cmds.connectAttr("%s.transDown" %self._attr_node, "%s.ny" %tranY_setRange)
        cmds.setAttr("%s.omx" %tranY_setRange, 1)
        cmds.setAttr("%s.ony" %tranY_setRange, -1)
        cmds.connectAttr("%s.ox" %tranY_setRange, "%s.i2[0].i2x" %tranY_pma)
        cmds.connectAttr("%s.oy" %tranY_setRange, "%s.i2[1].i2x" %tranY_pma)
        ty = cmds.getAttr("%s.ty" %self._jaw_jnts[1])
        cmds.setAttr("%s.i2[2].i2x" %tranY_pma, ty)
        cmds.connectAttr("%s.o2x" %tranY_pma, "%s.ty" %self._jaw_jnts[1])
        

    def _setup_fwBk(self):
        tranX_setRange = cmds.createNode("setRange", n="%s_jawTXSetRange" %self._side)
        tranX_pma = cmds.createNode("plusMinusAverage", n="%s_jawTXpma" %self._side)

        cmds.connectAttr("%s.tx" %self._jawFwBk_control.ctl, "%s.vx" %tranX_setRange)
        cmds.connectAttr("%s.tx" %self._jawFwBk_control.ctl, "%s.vy" %tranX_setRange)
        cmds.connectAttr("%s.jawFwd" %self._attr_node, "%s.mx" %tranX_setRange)
        cmds.connectAttr("%s.jawBack" %self._attr_node, "%s.ny" %tranX_setRange)
        cmds.setAttr("%s.omx" %tranX_setRange, 1)
        cmds.setAttr("%s.ony" %tranX_setRange, -1)
        cmds.connectAttr("%s.ox" %tranX_setRange, "%s.i2[0].i2x" %tranX_pma)
        cmds.connectAttr("%s.oy" %tranX_setRange, "%s.i2[1].i2x" %tranX_pma)
        tz = cmds.getAttr("%s.tz" %self._jaw_jnts[1])
        cmds.setAttr("%s.i2[2].i2x" %tranX_pma, tz)
        cmds.connectAttr("%s.o2x" %tranX_pma, "%s.tz" %self._jaw_jnts[1])


    def _clean(self):
        '''
        general clean up of the rig
        '''
        gui_nodes = [self._guide.joint_order[0]] + self.gui
        self.gui_grp = cmds.group(gui_nodes, n="%s_jaw_gui" %self._side)
        cmds.setAttr("%s.v" %self.gui_grp, 0)
        utils.lock_hide(self.gui_grp, v=False)    
        
        self.ctls_grp = cmds.group(self.controls, n="%s_jaw_controls" %self._side)
        rig_nodes = [self._attr_node]
        if not self.parent:
            rig_nodes.append(self._jaw_jnts[0])
            
        self.rig_grp = self._attr_node
        
        self.input_nodes = self._jaw_jnts[0]
        self.output_jaw = self._jaw_jnts[2]
        self.output_skull = self._jaw_jnts[0]
        
    def create(self):
        self._create_joints()
        self._create_attribute_node()
        self._create_controllers()
        self._setup_rotate()
        self._setup_translate()
        self._setup_fwBk()
        self._clean()
        


class DualJawRig(SimpleJawRig):

    '''
    extends the simple jaw rig to include jaw ends, and beak/snout 
    '''    
    
    
    def __init__(self, guide=rigGuides.JawGuide(), upper='snout'):
        '''
        guide = rigGuide.JawGuide object
        '''
        SimpleJawRig.__init__(self, guide)
        self._snout_jnts = list()
        # to change this to beak or whatever if needed
        self._snout_name = upper
        
    def _create_joints(self):
        SimpleJawRig._create_joints(self)
        
        gui_jnts = self._guide.snout_order
        
        cmds.select(clear=True)
        joints = cmds.duplicate(gui_jnts, rc=True)
        
        
        for gui, jnt in zip(gui_jnts, joints):
            new_name = gui.replace("gui", "jnt")
            jnt_name = cmds.rename(jnt,new_name)
            self._snout_jnts.append(jnt_name)
            
        cmds.parent(self._snout_jnts[0], self._jaw_jnts[0])
              
        #label joints
        for joint in self._snout_jnts:
            utils.label_joint(joint, self._side, typ="Other", label=joint.split("_")[2])
        
        
    def _create_attribute_node(self):
        '''
        adding the snout attrs
        '''
        SimpleJawRig._create_attribute_node(self)
        
        cmds.addAttr(self._attr_node, ln="jawTipRotDown", k=True, dv=-25)
        cmds.addAttr(self._attr_node, ln="jawTipRotUp", k=True, dv=10)
        cmds.addAttr(self._attr_node, ln="jawTipRotLeft", k=True, dv=8)
        cmds.addAttr(self._attr_node, ln="jawTipRotRight", k=True, dv=-8)
        
        cmds.addAttr(self._attr_node, ln="%sRotDown" %self._snout_name, k=True, dv=-25)
        cmds.addAttr(self._attr_node, ln="%sRotUp" %self._snout_name, k=True, dv=10)
        cmds.addAttr(self._attr_node, ln="%sRotLeft" %self._snout_name, k=True, dv=8)
        cmds.addAttr(self._attr_node, ln="%sRotRight" %self._snout_name, k=True, dv=-8)
        
        cmds.addAttr(self._attr_node, ln="%sTipRotDown" %self._snout_name, k=True, dv=-25)
        cmds.addAttr(self._attr_node, ln="%sTipRotUp" %self._snout_name, k=True, dv=10)
        cmds.addAttr(self._attr_node, ln="%sTipRotLeft" %self._snout_name, k=True, dv=8)
        cmds.addAttr(self._attr_node, ln="%sTipRotRight" %self._snout_name, k=True, dv=-8)
    
    
    def _create_controllers(self):
        '''
        create the face jaw controls
        '''
        SimpleJawRig._create_controllers(self)
        
        self._snoutRot_control = controllers.SquareFaceControl("%s_ctl_%sRot" %(self._side, self._snout_name))
        self._snoutRot_control.set_position(obj=self._guide.controller_guides["snoutRot"])
        
        self._snoutTipRot_control = controllers.SquareFaceControl("%s_ctl_%sTipRot" %(self._side, self._snout_name))
        self._snoutTipRot_control.set_position(obj=self._guide.controller_guides["snoutTipRot"])
        
        self._jawTipRot_control = controllers.SquareFaceControl("%s_ctl_jawTipRot" %self._side)
        self._jawTipRot_control.set_position(obj=self._guide.controller_guides["jawTipRot"])
        
        self.controls.extend([self._snoutRot_control.name, self._snoutTipRot_control.name, self._jawTipRot_control.name])
        self.gui.extend([self._guide.controller_guides["snoutRot"], self._guide.controller_guides["snoutTipRot"], self._guide.controller_guides["jawTipRot"] ])
        
        
    def _setup_rotate(self):
        SimpleJawRig._setup_rotate(self)
        
        # Jaw Tip
        rotY_setRange = cmds.createNode("setRange", n="%s_jawTipRYSetRange" %self._side)
        rotZ_setRange = cmds.createNode("setRange", n="%s_jawTipRZSetRange" %self._side)
        rotY_pma = cmds.createNode("plusMinusAverage", n="%s_jawTipRYpma" %self._side)
        rotZ_pma = cmds.createNode("plusMinusAverage", n="%s_jawTipRZpma" %self._side)
        
        cmds.connectAttr("%s.tx" %self._jawTipRot_control.ctl, "%s.vx" %rotY_setRange)
        cmds.connectAttr("%s.tx" %self._jawTipRot_control.ctl, "%s.vy" %rotY_setRange)
        cmds.connectAttr("%s.jawTipRotLeft" %self._attr_node, "%s.mx" %rotY_setRange)
        cmds.connectAttr("%s.jawTipRotRight" %self._attr_node, "%s.ny" %rotY_setRange)
        cmds.setAttr("%s.omx" %rotY_setRange, 1)
        cmds.setAttr("%s.ony" %rotY_setRange, -1)
        cmds.connectAttr("%s.ox" %rotY_setRange, "%s.i1[0]" %rotY_pma)
        cmds.connectAttr("%s.oy" %rotY_setRange, "%s.i1[1]" %rotY_pma)
        cmds.connectAttr("%s.o1" %rotY_pma, "%s.ry" %self._jaw_jnts[3])
        
        cmds.connectAttr("%s.ty" %self._jawTipRot_control.ctl, "%s.vx" %rotZ_setRange)
        cmds.connectAttr("%s.ty" %self._jawTipRot_control.ctl, "%s.vy" %rotZ_setRange)
        cmds.connectAttr("%s.jawTipRotUp" %self._attr_node, "%s.mx" %rotZ_setRange)
        cmds.connectAttr("%s.jawTipRotDown" %self._attr_node, "%s.ny" %rotZ_setRange)
        cmds.setAttr("%s.omx" %rotZ_setRange, 1)
        cmds.setAttr("%s.ony" %rotZ_setRange, -1)
        cmds.connectAttr("%s.ox" %rotZ_setRange, "%s.i1[0]" %rotZ_pma)
        cmds.connectAttr("%s.oy" %rotZ_setRange, "%s.i1[1]" %rotZ_pma)
        cmds.connectAttr("%s.o1" %rotZ_pma, "%s.rz" %self._jaw_jnts[3])
        
        # snout 
        rotY_setRange = cmds.createNode("setRange", n="%s_%sRYSetRange" %(self._side, self._snout_name))
        rotZ_setRange = cmds.createNode("setRange", n="%s_%sRZSetRange"  %(self._side, self._snout_name))
        rotY_pma = cmds.createNode("plusMinusAverage", n="%s_%sRYpma"  %(self._side, self._snout_name))
        rotZ_pma = cmds.createNode("plusMinusAverage", n="%s_%sRZpma"  %(self._side, self._snout_name))
        
        cmds.connectAttr("%s.tx" %self._snoutRot_control.ctl, "%s.vx" %rotY_setRange)
        cmds.connectAttr("%s.tx" %self._snoutRot_control.ctl, "%s.vy" %rotY_setRange)
        cmds.connectAttr("%s.%sRotLeft" %(self._attr_node, self._snout_name), "%s.mx" %rotY_setRange)
        cmds.connectAttr("%s.%sRotRight" %(self._attr_node, self._snout_name), "%s.ny" %rotY_setRange)
        cmds.setAttr("%s.omx" %rotY_setRange, 1)
        cmds.setAttr("%s.ony" %rotY_setRange, -1)
        cmds.connectAttr("%s.ox" %rotY_setRange, "%s.i1[0]" %rotY_pma)
        cmds.connectAttr("%s.oy" %rotY_setRange, "%s.i1[1]" %rotY_pma)
        cmds.connectAttr("%s.o1" %rotY_pma, "%s.ry" %self._snout_jnts[1])
        
        cmds.connectAttr("%s.ty" %self._snoutRot_control.ctl, "%s.vx" %rotZ_setRange)
        cmds.connectAttr("%s.ty" %self._snoutRot_control.ctl, "%s.vy" %rotZ_setRange)
        cmds.connectAttr("%s.%sRotUp" %(self._attr_node, self._snout_name), "%s.mx" %rotZ_setRange)
        cmds.connectAttr("%s.%sRotDown" %(self._attr_node, self._snout_name), "%s.ny" %rotZ_setRange)
        cmds.setAttr("%s.omx" %rotZ_setRange, 1)
        cmds.setAttr("%s.ony" %rotZ_setRange, -1)
        cmds.connectAttr("%s.ox" %rotZ_setRange, "%s.i1[0]" %rotZ_pma)
        cmds.connectAttr("%s.oy" %rotZ_setRange, "%s.i1[1]" %rotZ_pma)
        cmds.connectAttr("%s.o1" %rotZ_pma, "%s.rz" %self._snout_jnts[1])
        
        # snout Tip
        rotY_setRange = cmds.createNode("setRange", n="%s_%sTipRYSetRange" %(self._side, self._snout_name))
        rotZ_setRange = cmds.createNode("setRange", n="%s_%sTipRZSetRange"  %(self._side, self._snout_name))
        rotY_pma = cmds.createNode("plusMinusAverage", n="%s_%sTipRYpma"  %(self._side, self._snout_name))
        rotZ_pma = cmds.createNode("plusMinusAverage", n="%s_%sTipRZpma"  %(self._side, self._snout_name))
        
        cmds.connectAttr("%s.tx" %self._snoutTipRot_control.ctl, "%s.vx" %rotY_setRange)
        cmds.connectAttr("%s.tx" %self._snoutTipRot_control.ctl, "%s.vy" %rotY_setRange)
        cmds.connectAttr("%s.%sTipRotLeft" %(self._attr_node, self._snout_name), "%s.mx" %rotY_setRange)
        cmds.connectAttr("%s.%sTipRotRight" %(self._attr_node, self._snout_name), "%s.ny" %rotY_setRange)
        cmds.setAttr("%s.omx" %rotY_setRange, 1)
        cmds.setAttr("%s.ony" %rotY_setRange, -1)
        cmds.connectAttr("%s.ox" %rotY_setRange, "%s.i1[0]" %rotY_pma)
        cmds.connectAttr("%s.oy" %rotY_setRange, "%s.i1[1]" %rotY_pma)
        cmds.connectAttr("%s.o1" %rotY_pma, "%s.ry" %self._snout_jnts[2])
        
        cmds.connectAttr("%s.ty" %self._snoutTipRot_control.ctl, "%s.vx" %rotZ_setRange)
        cmds.connectAttr("%s.ty" %self._snoutTipRot_control.ctl, "%s.vy" %rotZ_setRange)
        cmds.connectAttr("%s.%sTipRotUp" %(self._attr_node, self._snout_name), "%s.mx" %rotZ_setRange)
        cmds.connectAttr("%s.%sTipRotDown" %(self._attr_node, self._snout_name), "%s.ny" %rotZ_setRange)
        cmds.setAttr("%s.omx" %rotZ_setRange, 1)
        cmds.setAttr("%s.ony" %rotZ_setRange, -1)
        cmds.connectAttr("%s.ox" %rotZ_setRange, "%s.i1[0]" %rotZ_pma)
        cmds.connectAttr("%s.oy" %rotZ_setRange, "%s.i1[1]" %rotZ_pma)
        cmds.connectAttr("%s.o1" %rotZ_pma, "%s.rz" %self._snout_jnts[2])
    
    def _clean(self):
        '''
        add the snout guis to the gui group
        '''
        SimpleJawRig._clean(self)
        
        cmds.parent(self._guide.snout_order, self.gui_grp)
        
        self.output_snout = self._snout_jnts[1]

    
    
        
class ZipLipsRig(modules.BaseModule):
    '''
        creating a zip Lip rig component
    '''    
    
    
    def __init__(self, guide=rigGuides.LipGuide):
        '''
        guide = rigGuide.JawGuide object
        '''
        modules.BaseModule.__init__(self, guide)
        self._lower_jnts = list()
        self._upper_jnts = list()
        self._mid_jnts = list()
        
        self._lower_crv = None
        self._upper_crv = None
        self._mid_crv = None
        
        self._zipJoints = self._guide.zipJoints

        self._crv_degree = 1


    def create_joints_from_guide(self, old="spine", new="spineIK", append=False, joint_order=[]):
        '''
         overload to pass a list and not parent the joints
        '''
        joints = cmds.duplicate(joint_order, rc=True)
        return_list = list()
        
        for gui, jnt in zip(joint_order, joints):
            new_name = gui.replace("gui", "jnt")
            new_name = new_name.replace(old, new)
            if append:
                tail = new_name[-2:]
                replace = append + tail
                new_name = new_name.replace(tail, replace)
            jnt_name = cmds.rename(jnt,new_name)
            return_list.append(jnt_name)
            
        #label the joint for incase it is needed for skin weight mirror etc
        for joint in return_list:
            utils.label_joint(joint, self._side, typ="Other", label=joint.split("_")[2])
            
        return return_list


    def _create_joints(self):
        cmds.select(cl=True)
        self._lower_jnts = self.create_joints_from_guide(joint_order=self._guide.joint_order_lower)
        self._upper_jnts = self.create_joints_from_guide(joint_order=self._guide.joint_order_upper)

    def _create_curves(self):
        self._guide.refresh_joint_data()
        
        self.lower_crv, self.lower_crv_shape = self._build_curves(self._guide.joint_order_lower, "%s_lower_crv" %self._side)
        self.mid_crv, self.mid_crv_shape = self._build_curves(self._guide.joint_order_mid, "%s_mid_crv" %self._side)
        self.upper_crv, self.upper_crv_shape = self._build_curves(self._guide.joint_order_upper, "%s_upper_crv" %self._side)
        
        cmds.xform(self.lower_crv, cp=True)
        cmds.xform(self.upper_crv, cp=True)
        cmds.xform(self.mid_crv, cp=True)
        
        # maintain the target curve between the two
        # if a bias is needed, tweak the weight values
        #cmds.parentConstraint([self.upper_crv, self.lower_crv], self.mid_crv)
#         utils.lock_hide([self.upper_crv, self.lower_crv, self.mid_crv])
        
        self._crv_group = cmds.group([self.lower_crv, self.mid_crv, self.upper_crv], n="%s_lipCrvs" %self._side)
        utils.lock_hide(self._crv_group)
        
        cmds.addAttr(self._crv_group, ln="zipLips", k=True, dv=0, min=0, max=self._zipJoints)
        
        
    def _build_curves(self, joints, crvName):
        cvs = []
        for key in joints:
            cvs.append(self._guide.joint_data[key])
        
        name = cmds.curve(d=self._crv_degree, p=cvs, n=crvName)

        shape = cmds.listRelatives(name, s=True)[0]
        # curve command was not naming the shape node properly
        shape = cmds.rename(shape, name + "Shape")
        
        return name, shape
    
    def _create_zip(self):
        # create the blends and point on curves for lower and upper
        self._create_one_zip(self._lower_jnts, crvShape=self.lower_crv_shape)
        self._create_one_zip(self._upper_jnts, "upper", self.upper_crv_shape)
        
        
    def _create_one_zip(self, joints, side="lower", crvShape = None):
        for i, joint in enumerate(joints):
            num = `i`.zfill(2)
            crvInfo = cmds.createNode('pointOnCurveInfo', n="%s_%s_%s_crvInfo" %(self._side, side, num))
            cmds.connectAttr("%s.worldSpace[0]" %crvShape, "%s.inputCurve" %crvInfo, f=True)
            cmds.setAttr("%s.parameter" %crvInfo, i)
            
            # node will exist the second time this is run            
            crvInfo_mid = "%s_mid%s_crvInfo" %(self._side, num)
            if not cmds.objExists(crvInfo_mid):
                crvInfo_mid = cmds.createNode('pointOnCurveInfo', n="%s_mid%s_crvInfo" %(self._side, num))
            
                cmds.connectAttr("%s.worldSpace[0]" %self.mid_crv_shape, "%s.inputCurve" %crvInfo_mid, f=True)
                cmds.setAttr("%s.parameter" %crvInfo_mid, i)
            
            blend = cmds.createNode('blendColors', n="%s_%s_%s_blend" %(self._side, side, num))
            cmds.connectAttr("%s.position" %crvInfo, "%s.color1" %blend, f=True)
            cmds.connectAttr("%s.position" %crvInfo_mid, "%s.color2" %blend, f=True)
            
            cmds.connectAttr("%s.output" %blend, "%s.translate" %joint, f=True)
            
            remap = cmds.createNode("remapValue", n="%s_%s_%s_rmp" %(self._side, side, num))
            cmds.connectAttr("%s.zipLips" %self._crv_group, "%s.inputValue" %remap, f=True)

            # remaping value to zero for fist element            
            min = i - 0.3
            if i == 0:
                min = 0

            cmds.setAttr("%s.inputMax" %remap, i+1)
            cmds.setAttr("%s.inputMin" %remap, min)
            cmds.setAttr("%s.outputMax" %remap, 0)
            cmds.setAttr("%s.outputMin" %remap, 1)
            
            cmds.connectAttr("%s.outValue" %remap, "%s.blender" %blend)
            
    def _create_controllers(self):
        '''
        create the zip controls
        '''
        zip_control = controllers.VerticalFaceControl("%s_ctl_zip" %self._side, orient="bottom")
        zip_control.set_position(obj=self._guide.controller_guides["zip"])
        zip_control.set_position(rot=[180,0,0])
        
        self.controls = zip_control.name
        self.gui = [self._guide.controller_guides["zip"]]
    
        remap = cmds.createNode("remapValue", n="%s.zipLips" %self._side)
        
        cmds.setAttr("%s.inputMax" %remap, 1)
        cmds.setAttr("%s.inputMin" %remap, 0)
        cmds.setAttr("%s.outputMax" %remap, self._zipJoints)
        cmds.setAttr("%s.outputMin" %remap, 0)
        
        cmds.connectAttr("%s.ty" %zip_control.ctl, "%s.inputValue" %remap)
        cmds.connectAttr("%s.outValue" %remap, "%s.zipLips" %self._crv_group)
    
    
    def _clean(self):
        '''
        general clean up of the rig
        '''
        gui_nodes = self._guide.joint_order + [self._guide.controller_guides['zip']]
        self.gui_grp = cmds.group(gui_nodes, n="%s_lip_gui" %self._side)
        cmds.setAttr("%s.v" %self.gui_grp, 0)
        utils.lock_hide(self.gui_grp, v=False)    
        
        
        self.rig_grp = cmds.group(self._lower_jnts + self._upper_jnts, n="%s_lip_joints" %self._side)
        
        top_grp = cmds.group([self.rig_grp, self.gui_grp, self._crv_group], n="%s_lip_module_0" %self._side)
    
        # these are needed to be parented under the rig group, and skinned to the respective joints
        # in the actual builder 
        self.input_lower = self.lower_crv
        self.input_upper = self.upper_crv
#         if self.mid_crv:
#             self.input_mid = self.mid_crv

        
        self.rig_grp = top_grp
    
    def create(self):
        self._create_joints()
        self._create_curves()
        self._create_zip()
        self._create_controllers()
        self._clean()


class CurveLipsRig(ZipLipsRig):
    '''
        This does not global transform
        
        Need a aim constraint for the joint rotations...or something else
        
    '''    
    
    
    def __init__(self, guide=rigGuides.CurveLipGuide()):
        '''
        guide = rigGuide.JawGuide object
        '''
        self.control_number = guide.control_number

        ZipLipsRig.__init__(self, guide)
        
        self._crv_degree = 3
    
    def _create_curves(self):
        '''
        overide, no longer create the mid curve and switch from a linear
        '''
        
        self._guide.refresh_joint_data()
        
        self.lower_crv, self.lower_crv_shape = self._build_curves(self._guide.joint_order_lower, "%s_lower_crv" %self._side)
        self.upper_crv, self.upper_crv_shape = self._build_curves(self._guide.joint_order_upper, "%s_upper_crv" %self._side)
        
        cmds.xform(self.lower_crv, cp=True)
        cmds.xform(self.upper_crv, cp=True)
        
        
        self._crv_group = cmds.group([self.lower_crv, self.upper_crv], n="%s_lipCrvs" %self._side)
        utils.lock_hide(self._crv_group)
        
    
    
    def _attach_joints(self):
        # create the blends and point on curves for lower and upper
        self._attach_to_curve(self._lower_jnts, crvShape=self.lower_crv_shape)
        self._attach_to_curve(self._upper_jnts, "upper", self.upper_crv_shape)
        
        
    def _attach_to_curve(self, joints, side="lower", crvShape = None):
        
        #rebuild curve first
        cmds.rebuildCurve(crvShape, rpo=1, rt=0, end=1, kr=0, kcp=0, kep=1, kt=0, s=4, d=3, tol=0.01)
        
        for i, joint in enumerate(joints):
            num = `i`.zfill(2)
            crvInfo = cmds.createNode('pointOnCurveInfo', n="%s_%s_%s_crvInfo" %(self._side, side, num))
            cmds.connectAttr("%s.worldSpace[0]" %crvShape, "%s.inputCurve" %crvInfo, f=True)
            if i == 0:
                param = i
            else:
                param = i+1
            cmds.setAttr("%s.parameter" %crvInfo, i/(self._zipJoints-1))
            
            cmds.connectAttr("%s.position" %crvInfo, "%s.translate" %joint, f=True)
        
    def _create_controllers(self):
        self.upper_controls = []
        self.lower_controls = []
        
        self.upper_ctrl_jnts = []
        self.lower_ctrl_jnts = []
        self.lower_ctrl_objs = []
        
        if self._side == "L":
            colour = "magenta"
            switch = [0,0,0]
            corner = "purple"
        else:
            colour = "light_blue"
            switch = [0,0,180]
            corner = "green"
        
        for i in range(self.control_number):    
            num = `i`.zfill(2)
            upper = controllers.ToothControl("%s_upperLip%s_ctl" %(self._side,num), self._colour, joint=True)
            lower = controllers.ToothControl("%s_lowerLip%s_ctl" %(self._side,num), colour, joint=True) 
        
            upper.set_offset_position(obj=self._guide.controller_guides["%s_upperlip%s" %(self._side, num)])
            lower.set_offset_position(obj=self._guide.controller_guides["%s_lowerlip%s" %(self._side, num)])                                                                        
        
            upper_rot = cmds.xform(self._guide.controller_guides["%s_upperlip%s" %(self._side, num)], q=True, ro=True)
            lower_rot = cmds.xform(self._guide.controller_guides["%s_lowerlip%s" %(self._side, num)], q=True, ro=True)
            
            upper.set_offset_position(rot=upper_rot)
            lower.set_offset_position(rot=lower_rot)
            
            upper.hide_scale()
            lower.hide_scale()
            
            self.upper_controls.append(upper.group)
            self.lower_controls.append(lower.group)
        
            self.lower_ctrl_objs.append(lower)
        
            self.upper_ctrl_jnts.append(upper.skin_jnt)
            self.lower_ctrl_jnts.append(lower.skin_jnt)
        
        
        self._corner_ctl = controllers.ToothControl("%s_mouthCorner_ctl" %self._side, corner)
        self._corner_ctl.add_offset()
        self._corner_ctl.set_offset_position(obj=self._guide.corner_gui)
        rot = cmds.xform(self._guide.corner_gui, q=True, ro=True)
        self._corner_ctl.set_offset_position(rot=rot)
        
        self._corner_ctl.hide_scale()
        
        cmds.addAttr(self.lower_ctrl_objs[0].name, ln="corner_follow", k=True, dv=0, min=0, max=1)
        
        self.corner_pma = cmds.createNode("plusMinusAverage", n="%s_cornerFollow_pma" %self._side)
        
        #set up for connections
        cmds.setAttr("%s.input2D[0].input2Dx" %self.corner_pma,  1)
        cmds.connectAttr("%s.corner_follow" %self.lower_ctrl_objs[0].name, "%s.input2D[1].input2Dx" %self.corner_pma, f=True )
        cmds.setAttr("%s.operation" %self.corner_pma, 2)
        
        cmds.parent(self.upper_controls[0], self._corner_ctl.name)
        cmds.parent(self.lower_controls[0], self._corner_ctl.name)
        
        
    def bind_curves(self):
        '''
        This needs to be a post build function, else the curves get stuffed when re-parenting because they are locked
        '''
        cmds.skinCluster(self.upper_ctrl_jnts, self.upper_crv, tsb = True, bm = True)
        cmds.skinCluster(self.lower_ctrl_jnts, self.lower_crv, tsb = True, bm = True)
        
        # lock and hide these just in case
        utils.lock_hide(self.input_upper)
        utils.lock_hide(self.input_lower)
        
        utils.visibility(self.upper_crv)
        utils.visibility(self.lower_crv)
        
        
    def _clean(self):
        '''
        general clean up of the rig
        '''
        gui_nodes = self._guide.joint_order + self._guide.all_gui
        self.gui_grp = cmds.group(gui_nodes, n="%s_lip_gui" %self._side)
        cmds.setAttr("%s.v" %self.gui_grp, 0)
        utils.lock_hide(self.gui_grp, v=False)    
        
        upper = cmds.group(self.upper_controls[1:], n= "%s_upperLip_controls" %self._side)
        lower = cmds.group(self.lower_controls[1:], n= "%s_lowerLip_controls" %self._side)
    
        self.rig_grp = cmds.group(self._lower_jnts + self._upper_jnts, n="%s_lip_joints" %self._side)
        
        self.module= cmds.group([self.rig_grp, self.gui_grp, self._crv_group, upper, lower, self._corner_ctl.group], n="%s_lip_module_0" %self._side)
    
        self.input_lower = lower
        self.input_upper = upper
        self.input_corner = self._corner_ctl.group
        
        
    def create(self):
        '''
        overide to not create the zip functionality
        '''
        self._create_joints()
        self._create_curves()
        self._attach_joints()
        self._create_controllers()
        self._clean()



