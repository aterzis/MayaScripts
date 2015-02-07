'''
(c) Arthur Terzis 2011

Spine Module implementation

Place to store different spine Module builders. All classes should take in a rigGuides
class to build the rig component from

All Modules inherit from modules.BaseModules which contains generic methods

'''

from . import controllers
from . import rigGuides
from . import modules
from . import utils
from maya import cmds


class StretchySpine(modules.BaseModule):
    '''
         creates a stretchy IK/FK spine setup 
         based on the passed in spine_guide which is of type
         rigGuide
    '''
    def __init__(self, guide=rigGuides.Spine5Guide()):
        '''
        spine_guide = rigGuide.SpineGuide object
        '''
        modules.BaseModule.__init__(self, guide)
        
        self._ikJnts = list()
        self._fkJnts = list()
 
        
    def build(self):
        self._createSplineIK()
        self._makeIKStretchy()
        self._createFK()
        self._clean()
        
        
    def _createSplineIK(self):
        '''
        create the default IKspline setup for the spine
        
        TODO: Remove the parent constraints, and instead just parent the nodes under each other
              needs an extra joint at the hips, for the legs to attach to
        
        '''
        # create the rig splineIK joints
        self._ikJnts = self.createJointsFromGuide("spine", "spineIK")
        self.outputHips = self._ikJnts[0]

        # create control joints and curves
        self.hip_jnt = cmds.duplicate(self._ikJnts[0], po=True, n="hip_C_jnt_0")[0]
        self.shoulder_jnt = cmds.duplicate(self._ikJnts[-1], n="shoulder_C_jnt_0")[0]
        cmds.parent(self.shoulder_jnt, world=True)
        
        self.hip_control = controllers.Arrow4Control("hip_C_ctl_0")
        self.hip_control.set_colour("yellow")
        self.hip_control.set_position(obj=self.hip_jnt)
        cmds.parent(self.hip_jnt, self.hip_control.name)
        cmds.setAttr('%s.rotateOrder' %self.hip_jnt, 2)
        self.hip_control.set_rotate_order("zxy")
        self.hip_control.hide_scale()
        self.hip_control.lock_hide("v")
        
        self.shoulder_control = controllers.SquareControl("shoulders_C_ctl_0")
        self.shoulder_control.set_position(obj=self.shoulder_jnt, sc=[4,4,4])
        self.shoulder_control.set_colour("yellow")
        cmds.parent(self.shoulder_jnt, self.shoulder_control.name)
        cmds.setAttr('%s.rotateOrder' %self.shoulder_jnt, 2)
        self.shoulder_control.set_rotate_order("zxy")
        self.shoulder_control.hide_scale()
        self.shoulder_control.lock_hide("v")
 
        # create splineIK setup
        ik_data = cmds.ikHandle(n="spineIKHandle", 
                                     startJoint=self._ikJnts[0],
                                     endEffector=self._ikJnts[-1], 
                                     solver="ikSplineSolver",
                                     createCurve=True)

        self._ik_handle = ik_data[0]
        self._ik_effector = cmds.rename(ik_data[1], "spine_effector")
        self._ik_curve = cmds.rename(ik_data[2], "spine_curve")
        cmds.setAttr("%s.v" %self._ik_curve, 0)
        cmds.setAttr("%s.v" %self._ik_handle, 0)
        
        cmds.skinCluster([self.hip_jnt, self.shoulder_jnt], self._ik_curve, tsb = True, bm = True)

        # set up the twist controls for the spline IK
        cmds.setAttr("%s.dTwistControlEnable" %self._ik_handle, 1)
        cmds.setAttr("%s.dWorldUpType" %self._ik_handle, 4)
        cmds.setAttr("%s.dWorldUpAxis" %self._ik_handle, 1)
        cmds.setAttr("%s.dWorldUpVectorY" %self._ik_handle, 0)
        cmds.setAttr("%s.dWorldUpVectorZ" %self._ik_handle, -1)
        cmds.setAttr("%s.dWorldUpVectorEndY" %self._ik_handle, 0)
        cmds.setAttr("%s.dWorldUpVectorEndZ" %self._ik_handle, -1)
        cmds.connectAttr('%s.worldMatrix[0]' %self.hip_control.name, "%s.dWorldUpMatrix" %self._ik_handle, f=True)
        cmds.connectAttr('%s.worldMatrix[0]' %self.shoulder_control.name, "%s.dWorldUpMatrixEnd" %self._ik_handle, f=True)


    def _makeIKStretchy(self):
        '''
        add squash and stretch to the ikSpline
        '''
        
        info = cmds.arclen(self._ik_curve, ch=True)
        info = cmds.rename(info, "spine_info")
        val = cmds.getAttr("%s.arcLength" %info)
        
        mdv_node = cmds.createNode("multiplyDivide", n="spine_stretch_multiplier")
        cmds.setAttr("%s.operation" %mdv_node, 2)
        cmds.connectAttr("%s.arcLength" %info, "%s.i1x" %mdv_node)
        cmds.setAttr("%s.i2x" %mdv_node, val)
        
        # adding an extra multiplier for the scaling of the rig 
        # to divide the scaling factor by
        mdv_scale = cmds.createNode("multiplyDivide", n="spine_scale_multiplier")
        cmds.setAttr("%s.i2x" %mdv_scale, 1)
        cmds.setAttr("%s.operation" %mdv_scale, 2)
        cmds.connectAttr("%s.ox" %mdv_node, "%s.i1x" %mdv_scale)
        self._mdv_scale = mdv_scale
        
        for joint in self._ikJnts:
            # make each joint stretchy using a scaling multiplier on tx
            mdl_name = joint.replace('jnt', 'mdl')
            mdl_node = cmds.createNode("multDoubleLinear", n=mdl_name)
            cmds.connectAttr("%s.ox" %mdv_scale, "%s.i1" %mdl_node)
            tx = cmds.getAttr("%s.tx" %joint)
            cmds.setAttr("%s.i2" %mdl_node, tx)
            cmds.connectAttr("%s.o" %mdl_node, "%s.tx" %joint)
        
        '''
        NEED TO ADD A SQUASH STRETCH METHOD FOR VOLUME PRESERVATION
        '''    
    
            
    def _createFK(self):
        '''
        create an FK spine set up and make the connections so that it
        drives the IK spine
        '''
        # create the FK joints
        self.start_jntFK = cmds.duplicate(self._ikJnts[0], po=True, n="spineFK_C_jnt_0")[0]
        self.end_jntFK = cmds.duplicate(self._ikJnts[-1], n="spineFKEnd_C_jnt_0")[0]    
        cmds.parent(self.end_jntFK, self.start_jntFK)
        
        #orient, set rotateOrder and split joints
        cmds.joint(self.start_jntFK, e=True, oj="yxz", sao="xup")
        cmds.setAttr('%s.rotateOrder' %self.start_jntFK, 2)
        fk_chain = utils.split_joint(self.start_jntFK, div=3, upAxis="ty")
    
        #create the main control
        self.main_control = controllers.SquareControl("C_ctl_main_0")
        self.main_control.set_position(obj=self.hip_jnt, sc=[11,11,11])
        self.main_control.set_colour('yellow')
        self.main_control.set_rotate_order("zxy")
        cmds.parent(self.start_jntFK, self.main_control.name)
        self.main_control.hide_scale()
        self.main_control.lock_hide("v")
    
        #Parent the IK controls under the FK joints
        hip_grp = cmds.group(self.hip_control.name, n="hip_grp")
        cmds.parent(hip_grp, self.start_jntFK)
        shoulder_grp = cmds.group(self.shoulder_control.name, n="shoulder_grp")
        cmds.parent(shoulder_grp, self.end_jntFK)
        
        utils.lock_hide([hip_grp, shoulder_grp])
        utils.lock_hide([self.start_jntFK, self.end_jntFK], other=['radius'])
        utils.lock_hide([fk_chain[1], fk_chain[2]], r=False, other=['radius'])
        
        fk_control1 = controllers.CircleControl("spineFK_C_ctl_0")
        fk_control1.set_colour('yellow')
        fk_control1.set_position(sc=[5,5,5])
        fk_control2 = controllers.CircleControl("spineFK_C_ctl_1")
        fk_control2.set_colour('yellow')
        fk_control2.set_position(sc=[5,5,5])
        
        cmds.parent(fk_control1.shape, fk_chain[1], add=True, shape=True)
        cmds.parent(fk_control2.shape, fk_chain[2], add=True, shape=True)
        
        cmds.delete([fk_control1.name,fk_control2.name])
        
    
    def _clean(self):
        '''
         general cleanup of the outliner and lock and hide any unwanted attributes 
        '''
        # grouping
        self.controlGroup = cmds.group(self.main_control.name, n="anim_controls_spine")
        #guides = cmds.group(self._guide.jointOrder[0], n="guides")
        other = [self._ikJnts[0], self._ik_curve, self._ik_handle]
        self.rigGroup = cmds.group(other, n="rig_group_spine")
        self.modGroup = cmds.group([self.controlGroup, self.rigGroup], n="spine_C_module_0")
        
#         cmds.setAttr("%s.v" %guides, 0)
        utils.lock_hide(self.rigGroup)
        utils.lock_hide(self.controlGroup)
#         utils.lock_hide(guides)
        
        cmds.setAttr("%s.inheritsTransform" %self._ik_curve, 0)
        cmds.connectAttr("%s.sy" %self.modGroup, "%s.i2x" %self._mdv_scale)
        
        #need to hide the joints
        
        