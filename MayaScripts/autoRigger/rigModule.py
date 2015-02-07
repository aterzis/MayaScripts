'''
(c) Arthur Terzis 2013
 
Where everything comes together
 
This is the master rig builder
 
'''
from . import controllers
from . import spineModules
from . import legModules
from . import rigGuides
 
from maya import cmds
 
 
class RigBuilder(object):
    '''
       virtual Base class for all rig builders
    '''
    def __init__(self, mesh=""):
        self.mesh = mesh
        self.skinJoints = list()
        self.masterControl = None
     
     
    def buildGuide(self):
        '''
         build all the guide components required
        '''
        return
     
    def buildRig(self):
        '''
         run after guide is built
         will create the rig based on the guide
         
         Build the master control
         
        '''
        return
     
    def createSkinCluster(self, mesh=""):
        '''
        will do a default bind of the mesh based on the skin joints specified in each component
        '''
        return
     
     

class BiPed(RigBuilder):
    '''
    A simple bi-ped rig for two legged characters
    '''
    def __init__(self, mesh=""):
        RigBuilder.__init__(self, mesh)
         
        # guides
        self.spineGuide = rigGuides.Spine5Guide()
        self.legLGuide = rigGuides.LegGuide()
        self.legRGuide = rigGuides.LegGuide("R")
        self.armLGuide = rigGuides.ArmGuide()
        self.armRGuide = rigGuides.ArmGuide("R")
        self.handLGuide = rigGuides.HandGuide()
        self.handRGuide = rigGuides.HandGuide("R")
        self.neckGuide = rigGuides.NeckGuide()
         
        # component builders
        self.spineRig = spineModules.StretchySpine(self.spineGuide)
        self.legLRig = legModules.IkFkLeg(self.legLGuide)
        self.legRRig = legModules.IkFkLeg(self.legRGuide)
         
    def buildGuide(self):
        self.spineGuide.build()
        self.legLGuide.build()
        self.legRGuide.build()
        self.armRGuide.build()
        self.armLGuide.build()
        self.handLGuide.build()
        self.handRGuide.build()
        self.neckGuide.build()
         
         
        # conect the guides
        self.legLGuide.connectPorts(self.legLGuide.input, self.spineGuide.outputHips)
        self.legRGuide.connectPorts(self.legRGuide.input, self.spineGuide.outputHips)
         
        self.armLGuide.connectPorts(self.armLGuide.input, self.spineGuide.outputArms)
        self.armRGuide.connectPorts(self.armRGuide.input, self.spineGuide.outputArms)
         
        self.handLGuide.connectPorts(self.handLGuide.input, self.armLGuide.output)
        self.handRGuide.connectPorts(self.handRGuide.input, self.armRGuide.output)
         
        self.neckGuide.connectPorts(self.neckGuide.input, self.spineGuide.outputArms)
         
         
    def buildRig(self):
        self.spineRig.build()
        self.legLRig.build()
        self.legRRig.build()
     
        # connect the rig components
        self.legLRig.connectPorts(self.legLRig.inputFK, self.spineRig.outputHips)
        self.legLRig.connectPorts(self.legLRig.inputIK, self.spineRig.outputHips)
        self.legLRig.connectPorts(self.legLRig.inputSkn, self.spineRig.outputHips)
# 
        self.legRRig.connectPorts(self.legRRig.inputFK, self.spineRig.outputHips)
        self.legRRig.connectPorts(self.legRRig.inputIK, self.spineRig.outputHips)
        self.legRRig.connectPorts(self.legRRig.inputSkn, self.spineRig.outputHips)

# import autoRigger.rigGuides as guide
# reload(guide)
# import autoRigger.spineModules as spine
# reload(spine)
# import autoRigger.rigBuilder as rig
# reload (rig)
#  
# char = rig.BiPed()
# char.buildGuide()
# char.buildRig()     
#     
