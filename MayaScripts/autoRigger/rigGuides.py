'''
(c) Arthur Terzis 2011

This is my implementation of a joint guide based system for my auto-rigger

Joint Guide is the base class, and all guide classes inherit from this. 
These create a default joint guide heirarchy, which can then be manipulated in Maya
by the user, and then passed into the corresponding module to create the rig component

'''



from maya import cmds


class JointGuide(object):
    '''
        Base class for the guide builders
    '''
    def __init__(self, side="C", name="joint", rebuild=False):
        self.side = side
        self.name = name
        self.joint_data = dict()
        self.joint_order = list()
        self.joint_chain = list()
        self.mirrored_chain = list()


    def _name_joint(self, position, num):
        return '%s_%s_%s_%s'%(self.side, self.name, position, num)


    def set_parent(self, parent):
        if cmds.objExists(parent):
            cmds.parent(self.joint_chain[0], parent)


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


    def rebuild(self):
        '''
        This function rebuilds the class with the guide data in the existing scene
        to rebuild a character who has an existing guide set up i.e. just sets up joint order
        A virtual function to be over written in the specific base classes
        '''
        pass


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
           
            
    def refresh_joint_data(self):
        '''
        refreshes the dictionary with the current guide positions - no rotations are stored
        '''
        for key, item in self.joint_data.items():
            trans = cmds.xform(key, q=True, t=True, ws=True)
            self.joint_data[key] = trans
            
        

class ArmGuide(JointGuide):

    def __init__(self, side="L", name="gui", rebuild=False):
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

    def __init__(self, side="L", name="gui", rebuild=False):
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


class Spine3Guide(JointGuide):
    def __init__(self, side="C", name="gui", rebuild=False):
        JointGuide.__init__(self, side, name)
        self.setup_chain()

    def setup_chain(self):
        spine0     = self._name_joint('spine', 0)
        spine1     = self._name_joint('spine', 1)
        spine2     = self._name_joint('spine', 2)
        spine3     = self._name_joint('spine', 3)
        self.joint_order = [spine0, spine1, spine2, spine3]

        self.joint_data[spine0] = [0,7,0]
        self.joint_data[spine1] = [0,8.2,0]
        self.joint_data[spine2] = [0,9.4,0]
        self.joint_data[spine3] = [0,10.6,0]



# making the guides more flexible
SPINEDEFAULTS = {}
SPINEDEFAULTS['spine0'] = [0,7,0]
SPINEDEFAULTS['spine1'] = [0,8.2,0]
SPINEDEFAULTS['spine2'] = [0,9.4,0]
SPINEDEFAULTS['spine3'] = [0,10.6,0]
SPINEDEFAULTS['spine4'] = [0,11.8,0]
SPINEDEFAULTS['spine5'] = [0,13,0]


class Spine5Guide(JointGuide):
    def __init__(self, side="C", name="gui", rebuild=False, rename="spine", defaults=SPINEDEFAULTS):
        JointGuide.__init__(self, side, name)
        self._rename = rename
        self.defaults = defaults
        self.setup_chain()

    def setup_chain(self):
        spine0 = self._name_joint(self._rename, 0)
        spine1 = self._name_joint(self._rename, 1)
        spine2 = self._name_joint(self._rename, 2)
        spine3 = self._name_joint(self._rename, 3)
        spine4 = self._name_joint(self._rename, 4)
        spine5 = self._name_joint(self._rename, 5)
        self.joint_order = [spine0, spine1, spine2, spine3, spine4, spine5]

        self.joint_data[spine0] = self.defaults['spine0']
        self.joint_data[spine1] = self.defaults['spine1']
        self.joint_data[spine2] = self.defaults['spine2']
        self.joint_data[spine3] = self.defaults['spine3']
        self.joint_data[spine4] = self.defaults['spine4']
        self.joint_data[spine5] = self.defaults['spine5']


class Spine7Guide(Spine5Guide):
    def __init__(self, side="C", name="gui", rebuild=False, rename="spine"):
        Spine5Guide.__init__(self, side, name)
        self._rename = rename
        self.setup_chain()
        self.add_to_chain()
         
    def add_to_chain(self):
        spine6 = self._name_joint(self._rename, 6)
        spine7 = self._name_joint(self._rename, 7)
        
        self.joint_order.extend([spine6, spine7])
        
        self.joint_data[spine6] = [0,14.2,0]
        self.joint_data[spine7] = [0,15.4,0]


class NeckGuide(JointGuide):
    def __init__(self, side="C", name="gui", rebuild=False):
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
    """
     Hand is slightly different, since it is not a single heirarchy chain, but
     different finger chains branching off. So most methods are overwritten
    """

    def __init__(self, side="L", name="gui", rebuild=False):
        JointGuide.__init__(self, side, name)

        self.pinky_order   = list()
        self.middle_order  = list()
        self.ring_order    = list()
        self.pinky_order   = list()
        self.finger_chains = list()
        self.palm_joint    = None

        self.setup_chain()


    def set_parent(self, parent):
        if cmds.objExists(parent):
            cmds.parent(self.root, parent)


    def setup_chain(self):
        palm     = self._name_joint('palm', 0)
        index0   = self._name_joint('index', 0)
        index1   = self._name_joint('index', 1)
        index2   = self._name_joint('index', 2)
        index3   = self._name_joint('index', 3)
        middle0 = self._name_joint('middle', 0)
        middle1 = self._name_joint('middle', 1)
        middle2 = self._name_joint('middle', 2)
        middle3 = self._name_joint('middle', 3)
        ring0   = self._name_joint('ring', 0)
        ring1   = self._name_joint('ring', 1)
        ring2   = self._name_joint('ring', 2)
        ring3   = self._name_joint('ring', 3)
        pinky0  = self._name_joint('pinky', 0)
        pinky1  = self._name_joint('pinky', 1)
        pinky2  = self._name_joint('pinky', 2)
        pinky3  = self._name_joint('pinky', 3)
        thumb0  = self._name_joint('thumb', 0)
        thumb1  = self._name_joint('thumb', 1)
        thumb2  = self._name_joint('thumb', 2)


        self.index_order = [index0, index1, index2, index3]
        self.middle_order= [middle0, middle1, middle2, middle3]
        self.ring_order  = [ring0, ring1, ring2, ring3]
        self.pinky_order = [pinky0, pinky1, pinky2, pinky3]
        self.thumb_order = [thumb0, thumb1, thumb2]
        self.palm_joint  = palm

        # Make sure the palm joint is the first one in the list
        self.finger_chains.extend([self.palm_joint, self.index_order, self.middle_order,
                                  self.ring_order, self.pinky_order, self.thumb_order])

        self.joint_data[index0] = [13,14,0.45]
        self.joint_data[index1] = [13.5,14,0.45]
        self.joint_data[index2] = [14,14,0.45]
        self.joint_data[index3] = [14.6,14,0.45]
        self.joint_data[middle0]= [13,14,0]
        self.joint_data[middle1]= [13.6,14,0]
        self.joint_data[middle2]= [14.1,14,0]
        self.joint_data[middle3]= [14.8,14,0]
        self.joint_data[ring0]  = [12.8,14,-0.4]
        self.joint_data[ring1]  = [13.4,14,-0.4]
        self.joint_data[ring2]  = [14,14,-0.4]
        self.joint_data[ring3]  = [14.6,14,-0.4]
        self.joint_data[pinky0] = [12.7,14,-0.75]
        self.joint_data[pinky1] = [13.2,14,-0.75]
        self.joint_data[pinky2] = [13.9,14,-0.75]
        self.joint_data[pinky3] = [14.4,14,-0.75]
        self.joint_data[thumb0] = [12.5,14,0.9]
        self.joint_data[thumb1] = [13.3,14,1.2]
        self.joint_data[thumb2] = [14,14,1.2]
        self.joint_data[palm]   = [11,14,0]


    def create_chain(self):
        '''
        need to create each finger joint chain, and then parent to the root
        '''
        cmds.select(clear=True)
        for chain in self.finger_chains:
            cmds.select(clear=True)
            if isinstance(chain, list):
                for joint in chain:
                    if joint in self.joint_data.keys():
                        jnt = cmds.joint(n=joint, p=self.joint_data[joint])
                        self.joint_chain.append(jnt)
                cmds.parent(chain[0], self.root)
            else:
                self.root = cmds.joint(n=chain, p=self.joint_data[chain])
                self.joint_chain.append(self.root)


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

        self.mirrored_chain = cmds.mirrorJoint(self.root, mxy=xy, mxz=xz, myz=yz, mb=True, sr=[current_side, new_side])


'''
Dodgy constant global variable
'''
eyeDefaults = {}
eyeDefaults['eye_jnt'] = [1.252, 10.944, 5.482]
eyeDefaults['eyeAim_jnt'] = [0.375, 0, 0]
eyeDefaults['uLid_jnt'] = [1.252, 10.944, 5.482]
eyeDefaults['uLidAim_jnt'] = [0.427, -0.196, 0]
eyeDefaults['lLid_jnt'] = [1.252, 10.944, 5.482]
eyeDefaults['lLidAim_jnt'] = [0.42, 0.154, 0]
eyeDefaults['eye_gui'] = [4.731, 18.893, 0]
eyeDefaults['ulid_gui'] = [7.031, 19.793, 0]
eyeDefaults['llid_gui'] = [7.031, 17.393, 0]
eyeDefaults['blink_gui'] = [8.231, 18.893, 0]


class EyeGuide(JointGuide):
    '''
    for use with eye rigs that use 1 joint for the upper and lower lids. 
    '''
    def __init__(self, side="L", name="gui", rebuild=False, defaults = eyeDefaults):
        JointGuide.__init__(self, side, name)
        self.defaults = {}
        self.set_default_positions(defaults)
        self.setup_chain()
        
        if rebuild:
            self.rebuild()
        else:
            self.controller_guides = dict()
            self._create_controller_guides()
        
    def set_default_positions(self, defaults):
        self.defaults['eye_jnt'] = defaults['eye_jnt'] 
        self.defaults['eyeAim_jnt'] = defaults['eyeAim_jnt']
        self.defaults['uLid_jnt'] = defaults['uLid_jnt']
        self.defaults['uLidAim_jnt'] = defaults['uLidAim_jnt']
        self.defaults['lLid_jnt'] = defaults['lLid_jnt']
        self.defaults['lLidAim_jnt'] = defaults['lLidAim_jnt']
        
        self.defaults['eye_gui'] = defaults['eye_gui']
        self.defaults['ulid_gui'] = defaults['ulid_gui']
        self.defaults['llid_gui'] = defaults['llid_gui']
        self.defaults['blink_gui'] = defaults['blink_gui']
        
        
    def setup_chain(self):
        eye = self._name_joint('eye', 0)
        eye_aim = self._name_joint('eyeAim', 0)
        upper_lid = self._name_joint('uLid', 0)
        upper_lid_aim = self._name_joint('uLidAim', 0)
        lower_lid = self._name_joint('lLid', 0)
        lower_lid_aim = self._name_joint('lLidAim', 0)
        
        self.joint_order = [eye, eye_aim, upper_lid, upper_lid_aim, lower_lid, lower_lid_aim]
        
        self.joint_data[eye] = self.defaults['eye_jnt'] 
        self.joint_data[eye_aim] = self.defaults['eyeAim_jnt'] 
        self.joint_data[upper_lid] = self.defaults['uLid_jnt'] 
        self.joint_data[upper_lid_aim] = self.defaults['uLidAim_jnt'] 
        self.joint_data[lower_lid] = self.defaults['lLid_jnt'] 
        self.joint_data[lower_lid_aim] = self.defaults['lLidAim_jnt'] 
        
    
    def rebuild(self):
        init = True
        for joint in self.joint_order:
            if cmds.objExists(joint):
                self.joint_chain.append(joint)
            else:
                init = False 
        
        eye = "%s_eye_gui" %self.side
        ulid = "%s_ulid_gui" %self.side
        llid = "%s_llid_gui" %self.side
        blink = "%s_blink_gui" %self.side

        if cmds.objExists(eye) and cmds.objExists(ulid) and cmds.objExists(llid) and cmds.objExists(blink): 
            self.controller_guides = {"eye":eye,
                                  "uLid":ulid,
                                  "lLid":llid,
                                  "blink":blink}
        
        else:
            init = False
            
        if init:
            print "### Successful initialization with %s Eye guide ###" %self.side
        else:
            print "### %s Eye Guide Rebuild failed - Do not attempt to rebuild the rig ###" %self.side
        
        
    def create_chain(self):
        '''
        joints are not created in a simple chain, method needs to be overriden
        '''
        cmds.select(clear=True)
        for i in range(len(self.joint_order)):
            if not i%2:
                cmds.select(clear=True)
            joint = self.joint_order[i]
            if joint in self.joint_data.keys():
                jnt = cmds.joint(n=joint, p=self.joint_data[joint])
                self.joint_chain.append(jnt)
                
        self.orient_chain()
        
        
    def _create_controller_guides(self):
        eye = cmds.spaceLocator(n="%s_eye_gui" %self.side)[0]
        cmds.xform(eye, ws=True, t=self.defaults['eye_gui'])
        ulid = cmds.spaceLocator(n="%s_ulid_gui" %self.side)[0]
        cmds.xform(ulid, ws=True, t=self.defaults['ulid_gui'] )
        llid = cmds.spaceLocator(n="%s_llid_gui" %self.side)[0]
        cmds.xform(llid, ws=True, t=self.defaults['llid_gui'] )
        blink = cmds.spaceLocator(n="%s_blink_gui" %self.side)[0]
        cmds.xform(blink, ws=True, t=self.defaults['blink_gui'])
        
        self.controller_guides = {"eye":eye,
                                  "uLid":ulid,
                                  "lLid":llid,
                                  "blink":blink}
        


class JawGuide(JointGuide):
    '''
    for use with simpleJaw setups - with a skull, jawRot and jawTrans joint 
    '''
    def __init__(self, side="C", name="gui", rebuild=False):
        JointGuide.__init__(self, side, name)
        self.setup_chain()
        
        if rebuild:
            self.rebuild()
        else:
            self.controller_guides = dict()
            self._create_controller_guides()


    def setup_chain(self):
        #naming it gui skull 1 to stop name clash with neck Module
        skull = self._name_joint('skull', 1)
        jaw_rot = self._name_joint('jawRot', 0)
        jaw_aim = self._name_joint('jawAim', 0)
        
        self.joint_order = [skull, jaw_rot, jaw_aim]
        
        self.joint_data[skull] = [0,0,0]
        self.joint_data[jaw_rot] = [0,-1,2]
        self.joint_data[jaw_aim] = [0,-2,6]
        
        
    def rebuild(self):
        init = True
        for joint in self.joint_order:
            if cmds.objExists(joint):
                self.joint_chain.append(joint)
            else:
                init = False 
        
        rot = "%s_jawRot_gui" %self.side
        trans = "%s_jawTrans_gui" %self.side   
        fb = "%s_jawFwBk_gui" %self.side
        
        if cmds.objExists(rot) and cmds.objExists(trans) and cmds.objExists(fb): 
            self.controller_guides = {"jawRot":rot,
                                      "jawTrans":trans,
                                      "jawFwBk":fb}
        else:
            init = False
            
        if init:
            print "### Successful initialization with Jaw guide ###"
        else:
            print "### Jaw guide Rebuild failed - Do not attempt to rebuild the rig ###"
        
                
    def _create_controller_guides(self):
        # to stop duplications, check if they exist
        if cmds.objExists("%s_jawRot_gui" %self.side):
            rot = "%s_jawRot_gui" %self.side
        else:
            rot = cmds.spaceLocator(n="%s_jawRot_gui" %self.side)[0]
            cmds.xform(rot, ws=True, t=[5,2,0])
  
        if cmds.objExists("%s_jawTrans_gui" %self.side):
            trans = "%s_jawTrans_gui" %self.side
        else:
            trans = cmds.spaceLocator(n="%s_jawTrans_gui" %self.side)[0]
            cmds.xform(trans, ws=True, t=[9,2,0])
        
        if cmds.objExists("%s_jawFwBk_gui" %self.side):
            fb = "%s_jawFwBk_gui" %self.side
        else:
            fb = cmds.spaceLocator(n="%s_jawFwBk_gui" %self.side)[0]
            cmds.xform(fb, ws=True, t=[7,0,0])
        
        self.controller_guides = {"jawRot":rot,
                                  "jawTrans":trans,
                                  "jawFwBk":fb}
        
    def create_chain(self):
        '''
        override base class to ensure the root joint i.e. skull is oriented to the world
        '''
        JointGuide.create_chain(self)
        cmds.joint(self.joint_chain[0], e=True, oj="none", zso=True)
        


class HyenaJawGuide(JawGuide):
    '''
    Hyena Jaw setup
    '''
    def __init__(self, side="C", name="gui", rebuild=False):
        JawGuide.__init__(self, side, name)
        self.setup_chain()
        
        if rebuild:
            self.rebuild()
        else:
            self.controller_guides = dict()
            self._create_controller_guides()


    def setup_chain(self):
        #naming it gui skull 1 to stop name clash with neck Module
        skull = self._name_joint('skull', 1)
        jaw_rot = self._name_joint('jawRot', 0)
        jaw_aim = self._name_joint('jawAim', 0)
        
        self.joint_order = [skull, jaw_rot, jaw_aim]
        
        self.joint_data[skull] = [0,9.514,2.271]
        self.joint_data[jaw_rot] = [0,9.623,4.799]
        self.joint_data[jaw_aim] = [0.0,7.646,7.809]
                
    def _create_controller_guides(self):
        # to stop duplications, check if they exist
        if cmds.objExists("%s_jawRot_gui" %self.side):
            rot = "%s_jawRot_gui" %self.side
        else:
            rot = cmds.spaceLocator(n="%s_jawRot_gui" %self.side)[0]
            cmds.xform(rot, ws=True, t=[-1.5,17.393,0])
  
        if cmds.objExists("%s_jawTrans_gui" %self.side):
            trans = "%s_jawTrans_gui" %self.side
        else:
            trans = cmds.spaceLocator(n="%s_jawTrans_gui" %self.side)[0]
            cmds.xform(trans, ws=True, t=[-1.5,15,0])
        
        if cmds.objExists("%s_jawFwBk_gui" %self.side):
            fb = "%s_jawFwBk_gui" %self.side
        else:
            fb = cmds.spaceLocator(n="%s_jawFwBk_gui" %self.side)[0]
            cmds.xform(fb, ws=True, t=[1.5,15,0])
        
        self.controller_guides = {"jawRot":rot,
                                  "jawTrans":trans,
                                  "jawFwBk":fb}
        
    def create_chain(self):
        '''
        override base class to ensure the root joint i.e. skull is oriented to the world
        '''
        JointGuide.create_chain(self)
        cmds.joint(self.joint_chain[0], e=True, oj="none", zso=True)


        
class DualJawGuide(HyenaJawGuide):
    '''
    adds an upper jaw/beak component
    Also adds jaw and beak tips 
    '''
    def __init__(self, side="C", name="gui", rebuild=False):
        HyenaJawGuide.__init__(self, side, name)
        self.setup_chain()
        
        if rebuild:
            self.rebuild()
        else:
            self.controller_guides = dict()
            self._create_controller_guides()


    def rebuild(self):
        HyenaJawGuide.rebuild(self)
        
        init = True
        for joint in self.joint_order:
            if cmds.objExists(joint):
                self.joint_chain.append(joint)
            else:
                init = False 
        
        rot = "%s_snoutRot_gui" %self.side
        snoutTip = "%s_snoutTipRot_gui" %self.side   
        jawTip = "%s_jawTipRot_gui" %self.side
        
        if cmds.objExists(rot) and cmds.objExists(snoutTip) and cmds.objExists(jawTip): 
            self.controller_guides['snoutRot'] = rot
            self.controller_guides['snoutTipRot'] = snoutTip
            self.controller_guides['jawTipRot'] = jawTip
        else:
            init = False
            
        if init:
            print "### Successful initialization with Dual Jaw guide ###"
        else:
            print "### Dual Jaw guide Rebuild failed - Do not attempt to rebuild the rig ###"


    def setup_chain(self):
        HyenaJawGuide.setup_chain(self)
        #naming it gui skull 1 to stop name clash with neck Module
        snout = self._name_joint('snout', 0)
        snout_rot = self._name_joint('snoutRot', 0)
        upperLip_rot = self._name_joint('upperLipRot', 0)
        snout_aim = self._name_joint('snoutAim', 0)
        
        self.snout_order = [snout, snout_rot, upperLip_rot, snout_aim]
        
        self.joint_data[snout] = [0,9.514,2.271]
        self.joint_data[snout_rot] = [0,9.746, 6.608]
        self.joint_data[upperLip_rot] = [0,9.032, 7.838]
        self.joint_data[snout_aim] = [0.0,8.307,8.271]
        
        #override some of the jaw guides
        jaw_aim = self._name_joint('jawAim', 0)
        self.joint_data[jaw_aim] = [0.0,7.661,7.823]
        
        lowerLip_rot = self._name_joint('lowerLipRot', 0)
        self.joint_data[lowerLip_rot] = [0.0,7.965,7.343]
        
        self.joint_order.insert(2, lowerLip_rot)
        
        
    def create_chain(self):
        '''
        create the chain specified in joint data dictionary
        '''
        HyenaJawGuide.create_chain(self)
        
        self.snout_chain = []
        
        cmds.select(clear=True)
        for joint in self.snout_order:
            if joint in self.joint_data.keys():
                jnt = cmds.joint(n=joint, p=self.joint_data[joint])
                self.snout_chain.append(jnt)

        cmds.joint(self.snout_chain, e=True, oj="xyz", sao="yup")


    def _create_controller_guides(self):
        # to stop duplications, check if they exist
        HyenaJawGuide._create_controller_guides(self)
        
        if cmds.objExists("%s_snoutRot_gui" %self.side):
            rot = "%s_snoutRot_gui" %self.side
        else:
            rot = cmds.spaceLocator(n="%s_snoutRot_gui" %self.side)[0]
            cmds.xform(rot, ws=True, t=[-1.5,19.7,0])            
        
        if cmds.objExists("%s_snoutTipRot_gui" %self.side):
            snoutTip = "%s_snoutTipRot_gui" %self.side
        else:
            snoutTip = cmds.spaceLocator(n="%s_snoutTipRot_gui" %self.side)[0]
            cmds.xform(snoutTip, ws=True, t=[1.5,19.7,0])
            
        if cmds.objExists("%s_jawTipRot_gui" %self.side):
            jawTip = "%s_jawTipRot_gui" %self.side
        else:
            jawTip = cmds.spaceLocator(n="%s_jawTipRot_gui" %self.side)[0]
            cmds.xform(jawTip, ws=True, t=[1.5,17.393,0])
        
        self.controller_guides['snoutRot'] = rot
        self.controller_guides['snoutTipRot'] = snoutTip
        self.controller_guides['jawTipRot'] = jawTip


class LipGuide(JointGuide):
    '''
    Zip Lip setup, with curves 
    '''
    def __init__(self, side="L", name="gui", rebuild=False, lipJoints = 6.0, defaults=None):
        JointGuide.__init__(self, side, name)
        self.zipJoints = lipJoints
        self.defaults = defaults

        self.joint_order_lower = list()
        self.joint_order_upper = list()
        self.joint_order_mid = list()

        
        self.setup_chain()
        
        self.controller_guides = dict()
        
        if rebuild:
            self.rebuild()
        else:
            self._create_controller_guides()


    def setup_chain(self):
        #naming it gui skull 1 to stop name clash with neck Module
        for i in range(int(self.zipJoints)):
            num = `i`.zfill(2)
            lower = self._name_joint('lower', num)
            upper = self._name_joint('upper', num)
            mid = self._name_joint('mid', num)
        
            if self.defaults:
                self.joint_data[lower] = self.defaults['lower'][i]
                self.joint_data[upper] = self.defaults['upper'][i]
                self.joint_data[mid] = self.defaults['mid'][i]
            else:
                if self.side == "L":
                    xval = 1.7
                else:
                    xval = -1.7
                
                self.joint_data[lower] = [xval, 8.872, i]
                self.joint_data[upper] = [xval, 9.041, i]
                self.joint_data[mid] = [xval,8.99, i]
            
            self.joint_order.extend([lower, mid, upper])
            self.joint_order_lower.append(lower)
            self.joint_order_upper.append(upper)
            self.joint_order_mid.append(mid)
        
        
    def rebuild(self):
        init = True
        for joint in self.joint_order:
            if cmds.objExists(joint):
                self.joint_chain.append(joint)
            else:
                init = False 
        
        zip = "%s_zip_gui" %self.side

         
        if cmds.objExists(zip):
            self.controller_guides = {"zip":zip}
        else:
            init = False
            
        if init:
            print "### Successful initialization with lip guide ###"
        else:
            print "### Zip Lip guide Rebuild failed - Do not attempt to rebuild the rig ###"
        
                
    def _create_controller_guides(self):
        zip = cmds.spaceLocator(n="%s_zip_gui" %self.side)[0]
        if self.side == "L":
            trans = [3, 15.393, 0]
        else:
            trans = [-3, 15.393, 0]
            
        cmds.xform(zip, ws=True, t=trans)

        self.controller_guides = {"zip":zip}
        
    def create_chain(self):
        '''
        override base class because joints do not need to be parented
        '''
        for key, item in self.joint_data.items():
            cmds.select(cl=True)
            jnt = cmds.joint(n=key, p=item)
            

class CurveLipGuide(LipGuide):
    
    def __init__(self, side="L", name="gui", rebuild=False, lipJoints = 6.0, defaults=None, control_number=3):
        self.control_number = control_number

        LipGuide.__init__(self, side=side, name=name, rebuild=rebuild, lipJoints = lipJoints, defaults=defaults)


    def rebuild(self):
        init = True
        for joint in self.joint_order:
            if cmds.objExists(joint):
                self.joint_chain.append(joint)
            else:
                init = False 
        
        self.all_gui = []
        
        for i in range(self.control_number):
            num = `i`.zfill(2)
            upper_gui = "%s_upperlip%s_gui" %(self.side, num)
            lower_gui = "%s_lowerlip%s_gui" %(self.side, num)

            if cmds.objExists(upper_gui) and cmds.objExists(lower_gui):
                self.controller_guides["%s_upperlip%s" %(self.side, num)] = upper_gui
                self.controller_guides["%s_lowerlip%s" %(self.side, num)] = lower_gui
                self.all_gui.extend([upper_gui, lower_gui])
            else:
                init = False
                print "### Missing Guide - Do not attempt to rebuild the rig ###"
        
        corner = "%s_mouthCorner_gui" %self.side
        if cmds.objExists(corner):
            self.corner_gui = corner
            self.all_gui.append(corner)
        else:
            init = False
            
        if init:
            print "### Successful initialization with lip guide ###"
        else:
            print "### Curve Lip guide Rebuild failed - Do not attempt to rebuild the rig ###"
        

    def setup_chain(self):
        # removing the mid joints - not needed 
        for i in range(int(self.zipJoints)):
            num = `i`.zfill(2)
            lower = self._name_joint('lower', num)
            upper = self._name_joint('upper', num)
        
            if self.defaults:
                self.joint_data[lower] = self.defaults['lower'][i]
                self.joint_data[upper] = self.defaults['upper'][i]
            else:
                if self.side == "L":
                    xval = 1.7
                else:
                    xval = -1.7
                
                self.joint_data[lower] = [xval, 8.872, i]
                self.joint_data[upper] = [xval, 9.041, i]
            
            self.joint_order.extend([lower, upper])
            self.joint_order_lower.append(lower)
            self.joint_order_upper.append(upper)
        
                
    def _create_controller_guides(self):
        self.all_gui = []
        
        for i in range(self.control_number):
            num = `i`.zfill(2)
            upper_gui = cmds.spaceLocator(n="%s_upperlip%s_gui" %(self.side, num))[0]
            lower_gui = cmds.spaceLocator(n="%s_lowerlip%s_gui" %(self.side, num))[0]
            
            if self.side == "L":
                trans_upper = [1.7, 9.041, i]
                trans_lower = [1.7, 8.872, i]
            else:
                trans_upper = [-1.7, 9.041, i]
                trans_lower = [-1.7, 8.872, i]
                
            cmds.xform(upper_gui, ws=True, t=trans_upper)
            cmds.xform(lower_gui, ws=True, t=trans_lower)
    
            self.controller_guides["%s_upperlip%s" %(self.side, num)] = upper_gui
            self.controller_guides["%s_lowerlip%s" %(self.side, num)] = lower_gui
            self.all_gui.extend([upper_gui, lower_gui])

        corner_gui = cmds.spaceLocator(n="%s_mouthCorner_gui" %self.side)[0]
        
        if self.side == "L":
            corner = [1.7, 9.041, -1]
                
        else:
            corner = [-1.7, 9.041, -1]
        
        cmds.xform(corner_gui, ws=True, t=corner)

        self.corner_gui = corner_gui
        
        self.all_gui.append(corner_gui)


class FaceBaseGuide(JointGuide):
    '''
    for use with simpleJaw setups - with a skull, jawRot and jawTrans joint 
    '''
    def __init__(self, side="C", name="gui", rebuild=False):
        JointGuide.__init__(self, side, name)
        self.setup_chain()

        if rebuild:
            self.rebuild()

    def setup_chain(self):
        skull = self._name_joint('skull', 0)
        root = self._name_joint('rigRoot', 0)
        front = self._name_joint('neckFront', 0)        
        back = self._name_joint('neckBack', 0)
        right = self._name_joint('neckRight', 0)
        left = self._name_joint('neckLeft', 0)
                
        self.joint_order = [root, skull, front, back, left, right]
        
        self.joint_data[root] = [0,0,0]
        self.joint_data[skull]= [0,5,0]
        self.joint_data[front] = [0,0,3]
        self.joint_data[back] = [0,0,-3]
        self.joint_data[right] = [-3,0,0]
        self.joint_data[left] = [3,0,0]


    def rebuild(self):
        init = True
        for joint in self.joint_order:
            if cmds.objExists(joint):
                self.joint_chain.append(joint)
            else:
                init = False 
            
        if init:
            print "### Successful initialization with Neck guide ###"
        else:
            print "### Neck Guide Rebuild failed - Do not attempt to rebuild the rig ###"

        
    def create_chain(self):
        '''
        override base class to create the specific heirarchy
        '''
    
        cmds.select(clear=True)
        joint_chain = self.joint_order[0:2]
        for joint in joint_chain:
            if joint in self.joint_data.keys():
                jnt = cmds.joint(n=joint, p=self.joint_data[joint])
                self.joint_chain.append(jnt)
                        
        rest = self.joint_order[2:]
        for joint in rest:
            cmds.select(self.joint_order[0])
            if joint in self.joint_data.keys():
                jnt = cmds.joint(n=joint, p=self.joint_data[joint])
                self.joint_chain.append(jnt)
                

class HyenaBaseGuide(JointGuide):
    '''
    for use with simpleJaw setups - with a skull, jawRot and jawTrans joint 
    '''
    def __init__(self, side="C", name="gui", rebuild=False):
        JointGuide.__init__(self, side, name)
        self.setup_chain()

        if rebuild:
            self.rebuild()

    def setup_chain(self):
        skull = self._name_joint('skull', 0)
        root = self._name_joint('rigRoot', 0)

        self.joint_order = [root, skull]
        
        self.joint_data[root] = [0,0,0]
        self.joint_data[skull]= [0,9.514,2.271]


    def rebuild(self):
        init = True
        for joint in self.joint_order:
            if cmds.objExists(joint):
                self.joint_chain.append(joint)
            else:
                init = False 
            
        if init:
            print "### Successful initialization with Neck guide ###"
        else:
            print "### Neck Guide Rebuild failed - Do not attempt to rebuild the rig ###"




#hand = HandGuide()
#hand.create_chain()
#hand.mirror_chain()
#
#arm = ArmGuide()
#
##body = []
##body.append(ArmGuide())
##body.append(LegGuide())
##
##for body_part in body:
##    create = getattr(body_part, "create_chain")()
##    mirror = getattr(body_part, "mirror_chain")()
#
#
#arm.create_chain()
#arm.mirror_chain()
##
#leg = LegGuide()
#leg.create_chain()
#leg.mirror_chain()
#
#spine = SpineGuide()
#spine.create_chain()
#neck = NeckGuide()
#neck.create_chain()

#PARENTING
#leg.set_parent(spine.joint_chain[0])
#leg.mirror_chain()
#arm.set_parent(spine.joint_chain[-1])
#arm.mirror_chain()
#neck.set_parent(spine.joint_chain[-1])