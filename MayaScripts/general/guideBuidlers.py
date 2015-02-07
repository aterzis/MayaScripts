from maya import cmds


class JointGuide(object):
    '''
        Base class for the guide builders
    '''
    def __init__(self, side="C", name="joint"):
        self.side = side
        self.name = name
        self.joint_data = dict()
        self.joint_order = list()
        self.joint_chain = list()
        self.mirrored_chain = list()


    def _name_joint(self, position, num):
        return '%s_%s_%s_%s'%(self.side, self.name, position, num)


    def create_chain(self):
        '''
        create the chain specified in joint data dictionary
        '''
        cmds.select(clear=True)
        for joint in self.joint_order:
            if joint in self.joint_data.keys():
                jnt = cmds.joint(n=joint, p=self.joint_data[joint])
                self.joint_chain.append(jnt)

        self.orient_chain()


    def setup_chain(self):
        '''
         method to be overriden by children, for specific body component
         by default set up a 3 joint chain
        '''
        for i in range(3):
            jnt_name = "%s_%s_%s" %(self.side, self.name, i)
            self.joint_order.append(jnt_name)
            self.joint_data[jnt_name] = [0,i,0]


    def orient_chain(self, orient="xyz", axis="yup"):
        '''
        orient = joint orient
        axis = secondary Axis orientation
        '''
        cmds.joint(self.joint_chain, e=True, oj=orient, sao=axis)


    def mirror_chain(self, current_side="L", new_side="R", plane='yz'):
        '''
        to mirror a joint chain
        current side, new_side are the strings to search replace in the mirror
        plane = yz, xy or xz
        '''
        xy = yz = xz = False

        if plane == "yz":
            yz=True
        elif plane == "xy":
            xy=True
        else:
            xz=True

        self.mirrored_chain = cmds.mirrorJoint(self.joint_chain[0], mxy=xy, mxz=xz, myz=yz, mb=True, sr=[current_side, new_side])


class ArmGuide(JointGuide):

    def __init__(self, side="L", name="gui"):
         JointGuide.__init__(self, side, name)
         self.setup_chain()

    def setup_chain(self):
        clavicle = self._name_joint('clavicle', 0)
        shoulder = self._name_joint('shoulder', 0)
        elbow    = self._name_joint('elbow', 0)
        wrist    = self._name_joint('wrist', 0)
        self.joint_order = [clavicle, shoulder, elbow, wrist]

        self.joint_data[clavicle] = [2,13,0]
        self.joint_data[shoulder] = [4,14,0]
        self.joint_data[elbow] = [8,14,-0.5]
        self.joint_data[wrist] = [11,14,0]

class LegGuide(JointGuide):

    def __init__(self, side="L", name="gui"):
         JointGuide.__init__(self, side, name)
         self.setup_chain()

    def setup_chain(self):
        hip     = self._name_joint('hip', 0)
        knee    = self._name_joint('knee', 0)
        ankle   = self._name_joint('ankle', 0)
        ball    = self._name_joint('ball', 0)
        toe     = self._name_joint('toe', 0)
        self.joint_order = [hip, knee, ankle, ball, toe]

        self.joint_data[hip] = [2,7,0]
        self.joint_data[knee] = [2,3,1]
        self.joint_data[ankle] = [2,0,0]
        self.joint_data[ball] = [2,0,1.5]
        self.joint_data[toe] = [2,0,2.5]


class SpineGuide(JointGuide):
    def __init__(self, side="C", name="gui"):
         JointGuide.__init__(self, side, name)
         self.setup_chain()

    def setup_chain(self):
        spine0     = self._name_joint('spine', 0)
        spine1     = self._name_joint('spine', 1)
        spine2     = self._name_joint('spine', 2)
        spine3     = self._name_joint('spine', 3)
        spine4     = self._name_joint('spine', 4)
        spine5     = self._name_joint('spine', 5)
        self.joint_order = [spine0, spine1, spine2, spine3, spine4, spine5]

        self.joint_data[spine0] = [0,7,0]
        self.joint_data[spine1] = [0,8.2,0]
        self.joint_data[spine2] = [0,9.4,0]
        self.joint_data[spine3] = [0,10.6,0]
        self.joint_data[spine4] = [0,11.8,0]
        self.joint_data[spine5] = [0,13,0]

class NeckGuide(JointGuide):
    def __init__(self, side="C", name="gui"):
         JointGuide.__init__(self, side, name)
         self.setup_chain()

    def setup_chain(self):
        neck0     = self._name_joint('neck', 0)
        neck1     = self._name_joint('neck', 1)
        neck2     = self._name_joint('neck', 2)
        neck3     = self._name_joint('neck', 3)
        head      = self._name_joint('head', 0)

        self.joint_order = [neck0, neck1, neck2, neck3, head]

        self.joint_data[neck0] = [0,14.2,0]
        self.joint_data[neck1] = [0,15.4,0]
        self.joint_data[neck2] = [0,16.6,0]
        self.joint_data[neck3] = [0,17.8,0]
        self.joint_data[head] = [0,20,0]

class HandGuide(JointGuide):
    pass


arm = ArmGuide()

#body = []
#body.append(ArmGuide())
#body.append(LegGuide())
#
#for body_part in body:
#    create = getattr(body_part, "create_chain")()
#    mirror = getattr(body_part, "mirror_chain")()


arm.create_chain()
arm.mirror_chain()

leg = LegGuide()
leg.create_chain()
leg.mirror_chain()

spine = SpineGuide()
spine.create_chain()
neck = NeckGuide()
neck.create_chain()
