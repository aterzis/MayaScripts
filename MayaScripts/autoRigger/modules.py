'''
(c) Arthur Terzis 2011

Base Module Class. The super class that all modules will inherit from
A handy place to store any generic code used in multiple modules

'''

from . import rigGuides
from maya import cmds


class BaseModule(object):
    '''
    Base Module class to store the generic methods required in my auto rig
    modules
    '''
    def __init__(self, guide=rigGuides.JointGuide()):
        self._guide = guide
        self._skin_jnts = list()
        self._side = self._guide.side
        
        if self._side == "L":
            self._colour = "red"
        elif self._side == "R":
            self._colour = "blue"
        else:
            self._colour = "yellow"
       
 
    def createJointsFromGuide(self, old="spine", new="spineIK", append=False):
        '''
        Takes the guide joints, and duplicates and renames in place 
        for the creation of the actual rig joints
        '''
        joints = cmds.duplicate(self._guide.jointOrder, rc=True)
        return_list = list()
        
        for gui, jnt in zip(self._guide.jointOrder, joints):
            new_name = gui.replace("gui", "jnt")
            new_name = new_name.replace(old, new)
            if append:
                tail = new_name[-2:]
                replace = append + tail
                new_name = new_name.replace(tail, replace)
            cmds.rename(jnt,new_name)
            return_list.append(new_name)
            
        return return_list
    
    def connectPorts(self, input, output):
        '''
        used to connect rig modules to each other
        '''
        if cmds.objExists(input) and cmds.objExists(output):
            cmds.parent(input, output)
    
    def skin(self):
        '''
        use the skin jnts variable to skin the rig to the selected mesh
        '''
        pass