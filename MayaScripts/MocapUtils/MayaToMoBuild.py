# A set of utility scripts to prepare a character rig for 
# motionBuilder mocap as used in the UTS mocap pipeline
# Script by Arthur Terzis © 2010

from maya import cmds

##########################
# DATA CLASSES
##########################

# A simple Data class that will store the information for a joint
class JointData(object):
    def __init__(self, rigJoint, mocapJoint):
        self.rigJoint = rigJoint
        self.mocapJoint = mocapJoint
        self.jointWorldPos = [0, 0, 0]
        self.jointOrient = None

# A base class for the rig specific classes. Every rig using this system will need its own rig class that inherits from this base
# and populates the lists
class TemplateRig(object):
    def __init__(self):
        self.spine = []
        self.hip = []
        self.rightArm = []
        self.rightLeg = []
        
    def getWorldSpace(self, joint):
        point = cmds.xform(joint, q=True, ws=True, t=True)
        return point
    
    def getOrientation(self, joint):
        # Not too sure how this will work for the time being
        pass

# The Alfred Rig specific data class
class AlfredRig(TemplateRig):
    def __init__(self):
        #initialise lists
        self.spine = [
                      JointData(rigJoint="root",
                                mocapJoint="mocap_Hips"),
                      JointData(rigJoint="spineLower",
                                mocapJoint="mocap_Spine"),          
                      JointData(rigJoint="spineMid",
                                mocapJoint="mocap_Spine1"), 
                      JointData(rigJoint="spineHigher",
                                mocapJoint="mocap_Spine2"),             
                      JointData(rigJoint="chest",
                                mocapJoint="mocap_Chest"),
                      JointData(rigJoint="neck",
                                mocapJoint="mocap_Neck"),          
                      JointData(rigJoint="head",
                                mocapJoint="mocap_Head"), 
                      JointData(rigJoint="headMid",
                                mocapJoint="mocap_HeadMid"),             
                      JointData(rigJoint="headHigher",
                                mocapJoint="mocap_headHigher"),
                      ]
        
        self.hip = [JointData(rigJoint="hip", mocapJoint="mocap_Hip")]
        
        self.rightArm = [
                         JointData(rigJoint="Right_Shoulder",
                                   mocapJoint="mocap_RightShoulder"),
                         JointData(rigJoint="Right_ArmOriginal",
                                   mocapJoint="mocap_RightArm"),
                         JointData(rigJoint="Right_ElbowOriginal",
                                   mocapJoint="mocap_RightForeArm"),
                         JointData(rigJoint="Right_WristOriginal",
                                   mocapJoint="mocap_RightHand"),
                         ]
        
        self.rightLeg = [                         
                         JointData(rigJoint="Right_Leg",
                                   mocapJoint="mocap_RightUpLeg"),
                         JointData(rigJoint="Right_Knee",
                                   mocapJoint="mocap_RightLeg"),
                         JointData(rigJoint="Right_Ankle",
                                   mocapJoint="mocap_RightFoot"),
                         JointData(rigJoint="Right_Fingers",
                                   mocapJoint="mocap_RightToeBase"),] 
        
        for jnt in self.spine:
            jnt.jointWorldPos = self.getWorldSpace(jnt.rigJoint)
            jnt.jointOrient   = self.getOrientation(jnt.rigJoint)
    
        for jnt in self.hip:
            jnt.jointWorldPos = self.getWorldSpace(jnt.rigJoint)
            jnt.jointOrient   = self.getOrientation(jnt.rigJoint)
            
        for jnt in self.rightArm:
            jnt.jointWorldPos = self.getWorldSpace(jnt.rigJoint)
            jnt.jointOrient   = self.getOrientation(jnt.rigJoint)
            
        for jnt in self.rightLeg:
            jnt.jointWorldPos = self.getWorldSpace(jnt.rigJoint)
            jnt.jointOrient   = self.getOrientation(jnt.rigJoint)

##########################
# MAIN
##########################

def main():
    # Zero out all the controls in the rig
    zeroAlfred()
    # create the joints
    rig = AlfredRig()
    createJoints(rig.spine)
    createJoints(rig.hip)
    createJoints(rig.rightArm)
    createJoints(rig.rightLeg)
    # Mirror the skeleton
    mirrorJoints([rig.rightArm[0], rig.rightLeg[0]])
    # Parent the mocap rig into the correct heirarchy
    parentMocapJoints()

##########################
# UTILITY FUNCTIONS
##########################

# Create a mocap joint in the worldspace of the existing joint
def createJoints(joints):
    cmds.select(clear=True)
    for joint in joints:
        cmds.joint(name = joint.mocapJoint, p = joint.jointWorldPos)
        
# takes a list of the root of joint chains to be mirrored
def mirrorJoints(joints):
    for joint in joints:
        cmds.select(clear=True)
        cmds.mirrorJoint(joint.mocapJoint, mirrorYZ=True, searchReplace=["Right", "Left"])
        
def parentMocapJoints():
    cmds.parent("mocap_LeftShoulder", "mocap_Chest")
    cmds.parent("mocap_RightShoulder", "mocap_Chest") 
    cmds.parent("mocap_LeftUpLeg", "mocap_Hip")
    cmds.parent("mocap_RightUpLeg", "mocap_Hip")
    cmds.parent("mocap_Hip", "mocap_Hips")
#    cmds.parent("mocap_Hips", "Master_MOCAP_Node")
        
#Special case for Alfred Rig - zero out these controls
def zeroAlfred():
    zeroAttrs("Right_ArmFk_CTRL", ['rx', 'ry', 'rz'])
    zeroAttrs("Left_ArmFk_CTRL", ['rx', 'ry', 'rz'])
    zeroAttrs("right_Shoulder_CTR", ["armWorldOrient"])
    zeroAttrs("left_Shoulder_CTR", ["armWorldOrient"])
    zeroAttrs("lockHead_CTRL", ["lockHead"])    
    
# Utility Function to zero out controls
def zeroAttrs(obj, attrs):
    for attr in attrs:
        try:
            cmds.setAttr(obj + "." + attr, 0)
        except:
            #if attr is locked, continue
            pass
        

main()