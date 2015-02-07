'''
(c) Arthur Terzis 2011

Leg Module implementation

Place to store different Leg Module builders. All classes should take in a rigGuides
class to build the rig component from

All Modules inherit from modules.BaseModules which contains generic methods

'''

from . import controllers
from . import rigGuides
from . import modules
from . import utils
from maya import cmds


class IkFkLeg(modules.BaseModule):
    '''
         creates an IK/FK blend leg setup  - bare bones leg rig with reverse foot
         based on the passed in leg_guide which is of type
         rigGuide
    '''    
    
    def __init__(self, guide=rigGuides.LegGuide()):
        '''
        guide = rigGuide.LegGuide object
        '''
        modules.BaseModule.__init__(self, guide)
        
        self._ik_jnts = list()
        self._fk_jnts = list()
        
        
    def build(self):
        self._createIK()
        self._createFK()
        self._createBlend()
        self._clean()
        
        
    def _createIK(self):
        '''
         create the leg IK 
        '''
        self._ik_jnts = self.createJointsFromGuide(append="_ik")
        
        self._ik_ctl = controllers.BoxControl("%s_ctl_foot_0" %self._side)
        self._ik_ctl.set_position(sc=[1.5,1,4], obj=self._ik_jnts[3])
        self._ik_ctl.set_pivot(obj=self._ik_jnts[2])
        self._ik_ctl.set_colour(self._colour)
        self._ik_ctl.hide_scale()
        

        # create the IK solvers
        ik_data = cmds.ikHandle(n="%s_legIKHandle" %self._side, 
                                startJoint=self._ik_jnts[0],
                                endEffector=self._ik_jnts[2], 
                                solver="ikRPsolver",
                                sticky="sticky")
        
        self._ik_handle_foot = ik_data[0]
        self._ik_effector_foot = ik_data[1]
        
        ik_data = cmds.ikHandle(n="%s_ballIKHandle" %self._side, 
                                startJoint=self._ik_jnts[2],
                                endEffector=self._ik_jnts[3], 
                                solver="ikSCsolver")
      
        self._ik_handle_ball = ik_data[0]
        self._ik_effector_ball = ik_data[1]
        
        ik_data = cmds.ikHandle(n="%s_toeIKHandle" %self._side, 
                                startJoint=self._ik_jnts[3],
                                endEffector=self._ik_jnts[4], 
                                solver="ikSCsolver")
        
        self._ik_handle_toe = ik_data[0]
        self._ik_effector_toe = ik_data[1]
    
        # create the pole vector constraint
        self._knee_ctl = controllers.LocatorControl("%s_ctl_kneePV_0" %self._side)
        toe_pos = cmds.xform(self._ik_jnts[4], q=True, ws=True, t=True)
        knee_pos = cmds.xform(self._ik_jnts[1], q=True, ws=True, t=True)
        pos = [knee_pos[0], knee_pos[1], toe_pos[2]]
        self._knee_ctl.set_position(trans=pos)
        self._knee_ctl.set_colour(self._colour)
        self._knee_ctl.hide_scale()
        self._knee_ctl.hide_rotation()
        cmds.poleVectorConstraint(self._knee_ctl.name, self._ik_handle_foot)
        
        self.inputIK = self._ik_jnts[0]
        
        self._createReverseFoot()
    

    def _createReverseFoot(self):
        # add reverse foot attributes to controller
        cmds.addAttr(self._ik_ctl.name, ln="PeelHeel", min=0, max=10, dv=0, k=True)
        cmds.addAttr(self._ik_ctl.name, ln="StandTip", min=0, max=10, dv=0, k=True)
        cmds.addAttr(self._ik_ctl.name, ln="TwistHeel", min=-10, max=10, dv=0, k=True)
        cmds.addAttr(self._ik_ctl.name, ln="TwistToes", min=-10, max=10, dv=0, k=True)
        cmds.addAttr(self._ik_ctl.name, ln="ToeTap", min=-10, max=10, dv=0, k=True)
        cmds.addAttr(self._ik_ctl.name, ln="ikFkBlend", min=0, max=10, dv=0, k=True)
        
        
        ankle_pos = cmds.xform(self._ik_jnts[2], q=True, ws=True, t=True) 
        ball_pos = cmds.xform(self._ik_jnts[3], q=True, ws=True, t=True)
        toe_pos = cmds.xform(self._ik_jnts[4], q=True, ws=True, t=True)
        
        # in connect attr remove the unit conversion node
        peelHeelGrp = cmds.group(self._ik_handle_foot, n="peelHeelGrp_%s" %self._side)
        cmds.xform(peelHeelGrp, ws=True, rp=ball_pos, sp=ball_pos)
        heelRemap = cmds.createNode('setRange', n="PeelHeelRange_%s_srg" %self._side)
        cmds.connectAttr("%s.PeelHeel" %self._ik_ctl.name, "%s.vx" %heelRemap)
        cmds.setAttr("%s.mx "%heelRemap, 50)
        cmds.setAttr("%s.omx "%heelRemap, 10)
        cmds.connectAttr("%s.ox"%heelRemap, "%s.rx" %peelHeelGrp)
        
        toeTapGrp = cmds.group([self._ik_handle_ball, self._ik_handle_toe], n="toeTapGrp_%s" %self._side)
        cmds.xform(toeTapGrp, ws=True, rp=ball_pos, sp=ball_pos)
        toeRemap = cmds.createNode('setRange', n="ToeTapRange_%s_srg" %self._side)
        cmds.connectAttr("%s.ToeTap" %self._ik_ctl.name, "%s.vx" %toeRemap)
        cmds.setAttr("%s.mx "%toeRemap, 50)
        cmds.setAttr("%s.nx "%toeRemap, -50)
        cmds.setAttr("%s.omx "%toeRemap, 10)
        cmds.setAttr("%s.onx "%toeRemap, -10)
        cmds.connectAttr("%s.ox"%toeRemap, "%s.rx" %toeTapGrp)
        
        
        toePivotGrp = cmds.group([peelHeelGrp, toeTapGrp], n="toePivotGrp_%s" %self._side)
        cmds.xform(toePivotGrp, ws=True, rp=toe_pos, sp=toe_pos)
        toePivRemap = cmds.createNode('setRange', n="ToePivotRange_%s_srg" %self._side)
        cmds.connectAttr("%s.StandTip" %self._ik_ctl.name, "%s.vx" %toePivRemap)
        cmds.setAttr("%s.mx "%toePivRemap, 35)
        cmds.setAttr("%s.omx "%toePivRemap, 10)
        cmds.connectAttr("%s.ox"%toePivRemap, "%s.rx" %toePivotGrp)
        cmds.connectAttr("%s.TwistToes" %self._ik_ctl.name, "%s.vy" %toePivRemap)
        cmds.setAttr("%s.my "%toePivRemap, 40)
        cmds.setAttr("%s.omy "%toePivRemap, 10)
        cmds.setAttr("%s.ny "%toePivRemap, -40)
        cmds.setAttr("%s.ony "%toePivRemap, -10)
        cmds.connectAttr("%s.oy"%toePivRemap, "%s.ry" %toePivotGrp)
        
        
        heelPivotGrp = cmds.group(toePivotGrp, n='HeelPivotGrp_%s' %self._side)
        cmds.xform(heelPivotGrp, ws=True, rp=ankle_pos, sp=ankle_pos)
        heelPivRemap = cmds.createNode('setRange', n="HeelPivotRange_%s_srg" %self._side)
        cmds.connectAttr("%s.TwistHeel" %self._ik_ctl.name, "%s.vy" %heelPivRemap)
        cmds.setAttr("%s.my "%heelPivRemap, 40)
        cmds.setAttr("%s.ny "%heelPivRemap, -40)
        cmds.setAttr("%s.omy "%heelPivRemap, 10)
        cmds.setAttr("%s.ony "%heelPivRemap, -10)
        cmds.connectAttr("%s.oy"%heelPivRemap, "%s.ry" %heelPivotGrp)
        
        cmds.parent(heelPivotGrp, self._ik_ctl.name)
        
        utils.set_visibility(heelPivotGrp)
        utils.lock_hide([heelPivotGrp, toePivotGrp, toeTapGrp, peelHeelGrp])
        
        
    def _createFK(self):
        '''
         create the FK leg
        '''
        self._fk_jnts = self.createJointsFromGuide(append="_fk")
        
        fk_hip_ctl = controllers.CircleControl("%s_ctl_hipFK_0" %self._side)
        fk_hip_ctl.set_colour(self._colour)
        fk_hip_ctl.set_position(sc=[2,2,2])
        fk_knee_ctl = controllers.CircleControl("%s_ctl_kneeFK_0" %self._side)
        fk_knee_ctl.set_colour(self._colour)
        fk_knee_ctl.set_position(sc=[2,2,2])
        fk_ankle_ctl = controllers.CircleControl("%s_ctl_ankleFK_0" %self._side)
        fk_ankle_ctl.set_colour(self._colour)
        fk_ankle_ctl.set_position(sc=[2,2,2])
        fk_ball_ctl = controllers.CircleControl("%s_ctl_ballFK_0" %self._side)
        fk_ball_ctl.set_colour(self._colour)
        fk_ball_ctl.set_position(sc=[2,2,2])
        
        cmds.parent(fk_hip_ctl.shape, self._fk_jnts[0], add=True, shape=True)
        cmds.parent(fk_knee_ctl.shape, self._fk_jnts[1], add=True, shape=True)
        cmds.parent(fk_ankle_ctl.shape, self._fk_jnts[2], add=True, shape=True)
        cmds.parent(fk_ball_ctl.shape, self._fk_jnts[3], add=True, shape=True)
        
        cmds.delete([fk_hip_ctl.name,fk_knee_ctl.name, fk_ankle_ctl.name,fk_ball_ctl.name])
        
        self.inputFK = self._fk_jnts[0]
        
        #lock and hide translate and scale
        utils.lock_hide(self._fk_jnts, r=False)
        
        
    def _createBlend(self):
        '''
         setup the blend between the FK and IK
         
         need to set interp type to shortest
         setAttr "hip_L_jnt_skn_0_orientConstraint1.interpType" 2
        '''
        
        self._skin_jnts = self.createJointsFromGuide(append="_skn")
        
        # setup the blend switch
        remap = cmds.createNode('setRange', n="%s_rmp_legBlend" %self._side)
        cmds.connectAttr("%s.ikFkBlend" %self._ik_ctl.name, "%s.vx" %remap)
        cmds.setAttr("%s.mx "%remap, 1)
        cmds.setAttr("%s.nx "%remap, 0)
        cmds.setAttr("%s.omx "%remap, 10)
        cmds.setAttr("%s.onx "%remap, 0)
        reverse = cmds.createNode('reverse', n="%s_rev_legBlend" %self._side)
        cmds.connectAttr("%s.ox"%remap, "%s.ix" %reverse)
        
        #constrain and connect
        for i in range(len(self._skin_jnts)):
            cnst = cmds.orientConstraint(self._ik_jnts[i], self._skin_jnts[i])[0]  
            cmds.orientConstraint(self._fk_jnts[i], self._skin_jnts[i])
            cmds.connectAttr("%s.ox" %remap,"%s.%sW0" %(cnst, self._ik_jnts[i]))
            cmds.connectAttr("%s.ox" %reverse,"%s.%sW1" %(cnst, self._fk_jnts[i]))
            cmds.setAttr("%s.interpType" %cnst, 2)
            
        self.inputSkn = self._skin_jnts[0]
            
    def _clean(self):
        '''
         general cleanup of the outliner and lock and hide any unwanted attributes 
        '''
        # grouping
        self.controlGroup = cmds.group([self._ik_ctl.name, self._knee_ctl.name], n="anim_controls_%s_leg" %self._side)
        other = [self.inputFK, self.inputIK, self.inputSkn]
        self.rigGroup = cmds.group(other, n="rig_group_%s_leg" %self._side)
        self.modGroup = cmds.group([self.controlGroup, self.rigGroup], n="leg_%s_module_0" %self._side)
        
        utils.lock_hide(self.rigGroup)
        utils.lock_hide(self.controlGroup)



class IkFkLegNoFlip(IkFkLeg):
    '''
         creates an IK/FK blend leg setup  - with no pole vector constraint
         based on the passed in leg_guide which is of type
         rigGuide
    '''    
