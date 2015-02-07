import sys
import maya.OpenMaya as OpenMaya
import maya.OpenMayaMPx as OpenMayaMPx
import maya.OpenMayaRender as OpenMayaRender
import maya.OpenMayaUI as OpenMayaUI
from Functions.apiFunctions import DependNode

nodeTypeName = "cameraSwitcher"
nodeTypeId = OpenMaya.MTypeId(0x87079)


class cameraSwitchNode(OpenMayaMPx.MPxNode):
    def __init__(self):
        OpenMayaMPx.MPxNode.__init__(self)

    def compute(self, plug, dataBlock):
        incams = dataBlock.inputValue(cameraSwitchNode.inputCams)
        outcam = dataBlock.inputValue(cameraSwitchNode.outPutMsg)
        id = dataBlock.inputValue(cameraSwitchNode.cameraId).asInt()

        # Get the current user defined in-cam
        inPlug = OpenMaya.MPlug(self.thisMObject(), cameraSwitchNode.inputCams)
        if id < inPlug.numElements():
            userPlug = inPlug.elementByPhysicalIndex(id)
        else:
            return False

        mpArray = OpenMaya.MPlugArray()
        userPlug.connectedTo(mpArray, True, False)
        inCamObj  = mpArray[0].node()
        inCamera  = OpenMaya.MFnDependencyNode(inCamObj)

        #get the main cam
        outPlug = OpenMaya.MPlug(self.thisMObject(), cameraSwitchNode.outPutMsg)
        outMPArray = OpenMaya.MPlugArray()
        outPlug.connectedTo(outMPArray, False, True)
        if outMPArray.length() > 0:
            outCamObj = outMPArray[0].node()
            outCamera = OpenMaya.MFnDependencyNode(outCamObj)
        else:
            return False

        # if not already - connect everything from this node, into the main camera


#        dagPath = OpenMaya.MDagPath()
#        dagPath.getAPathTo(inCamera.object())
#        cam = OpenMaya.MFnCamera(dagPath)

        dgMod = OpenMaya.MDGModifier()

        if plug == cameraSwitchNode.outTrans:
            pass
        if plug == cameraSwitchNode.outRot:
            pass
        if plug == cameraSwitchNode.outScale:
            pass

        if plug == cameraSwitchNode.horFilmApp:
            self.__updatePlug(cameraSwitchNode.horFilmApp,
                              'horizontalFilmAperture',
                              inCamera,
                              inCamObj)
            print "1"

        if plug == cameraSwitchNode.verFilmApp:
            self.__updatePlug(cameraSwitchNode.verFilmApp,
                              'verticalFilmAperture',
                              inCamera,
                              inCamObj)
            print "2"
        if plug == cameraSwitchNode.focalLength:
            self.__updatePlug(cameraSwitchNode.focalLength,
                              'focalLength',
                              inCamera,
                              inCamObj)
            print "3"
        if plug == cameraSwitchNode.lens:
            self.__updatePlug(cameraSwitchNode.lens,
                              'lensSqueezeRatio',
                              inCamera,
                              inCamObj)
            print "4"
        if plug == cameraSwitchNode.fstop:
            self.__updatePlug(cameraSwitchNode.fstop,
                              'fStop',
                              inCamera,
                              inCamObj)
            print "5"

        if plug == cameraSwitchNode.focusDist:
            self.__updatePlug(cameraSwitchNode.focusDist,
                              'focusDist',
                              inCamera,
                              inCamObj)
            print "6"
        if plug == cameraSwitchNode.shutterAngle:
            self.__updatePlug(cameraSwitchNode.shutterAngle,
                              'ShutterAngle',
                              inCamera,
                              inCamObj)
            print "6a"
        if plug == cameraSwitchNode.centre:
            self.__updatePlug(cameraSwitchNode.centre,
                              'centreOfInterest',
                              inCamera,
                              inCamObj)
            print "7"
        dataBlock.setClean( plug )


    def __updatePlug(self, nodeAttr, inAttr, inCam, inCamObj):
        nodePlug = OpenMaya.MPlug(self.thisMObject(), nodeAttr)
        attrObj  = inCam.attribute(inAttr)
        inPlug = OpenMaya.MPlug(inCamObj, attrObj)
        newValue = inPlug.asFloat()
        nodePlug.setFloat(newValue)
#        nodePlug.setMObject(attrObj)


def nodeCreator():
    return OpenMayaMPx.asMPxPtr(cameraSwitchNode())


def nodeInitializer():
    nAttr = OpenMaya.MFnNumericAttribute()
    cAttr = OpenMaya.MFnCompoundAttribute()
    mAttr = OpenMaya.MFnMessageAttribute()
    tAttr = OpenMaya.MFnTypedAttribute()

    # define attributes
    cameraSwitchNode.cameraId = nAttr.create('cameraID', 'cid', OpenMaya.MFnNumericData.kInt )
    nAttr.setChannelBox(1)
    nAttr.setKeyable(1)
    nAttr.setWritable(1)
    nAttr.setReadable(1)

    cameraSwitchNode.inputCams = mAttr.create("cameraInputs", "cin")
    mAttr.setArray(1)
    mAttr.setConnectable(1)
    mAttr.setUsesArrayDataBuilder(1)


    cameraSwitchNode.outPutMsg = mAttr.create("mainCamera", 'mc')

    cameraSwitchNode.transX = nAttr.create( "translateX", "tx", OpenMaya.MFnNumericData.kFloat )
    nAttr.setStorable(1)
    nAttr.setWritable(1)

    cameraSwitchNode.transY = nAttr.create( "translateY", "ty", OpenMaya.MFnNumericData.kFloat )
    nAttr.setStorable(1)
    nAttr.setWritable(1)

    cameraSwitchNode.transZ = nAttr.create( "translateZ", "tz", OpenMaya.MFnNumericData.kFloat )
    nAttr.setStorable(1)
    nAttr.setWritable(1)

    cameraSwitchNode.outTrans = cAttr.create("translate", "t")
    cAttr.addChild(cameraSwitchNode.transX)
    cAttr.addChild(cameraSwitchNode.transY)
    cAttr.addChild(cameraSwitchNode.transZ)

    cameraSwitchNode.rotX = nAttr.create( "rotateX", "rx", OpenMaya.MFnNumericData.kFloat )
    nAttr.setStorable(1)
    nAttr.setWritable(1)

    cameraSwitchNode.rotY = nAttr.create( "rotateY", "ry", OpenMaya.MFnNumericData.kFloat )
    nAttr.setStorable(1)
    nAttr.setWritable(1)

    cameraSwitchNode.rotZ = nAttr.create( "rotateZ", "rz", OpenMaya.MFnNumericData.kFloat )
    nAttr.setStorable(1)
    nAttr.setWritable(1)

    cameraSwitchNode.outRot = cAttr.create("rotate", "r")
    cAttr.addChild(cameraSwitchNode.rotX)
    cAttr.addChild(cameraSwitchNode.rotY)
    cAttr.addChild(cameraSwitchNode.rotZ)

    cameraSwitchNode.scaleX = nAttr.create( "scaleX", "sx", OpenMaya.MFnNumericData.kFloat )
    nAttr.setStorable(1)
    nAttr.setWritable(1)

    cameraSwitchNode.scaleY = nAttr.create( "scaleY", "sy", OpenMaya.MFnNumericData.kFloat )
    nAttr.setStorable(1)
    nAttr.setWritable(1)

    cameraSwitchNode.scaleZ = nAttr.create( "scaleZ", "sz", OpenMaya.MFnNumericData.kFloat )
    nAttr.setStorable(1)
    nAttr.setWritable(1)

    cameraSwitchNode.outScale = cAttr.create("scale", "s")
    cAttr.addChild(cameraSwitchNode.scaleX)
    cAttr.addChild(cameraSwitchNode.scaleY)
    cAttr.addChild(cameraSwitchNode.scaleZ)

    # default camera attributes and settings
    cameraSwitchNode.horFilmApp = nAttr.create("horizontalFilmApperture", 'hfa', OpenMaya.MFnNumericData.kFloat, 1.417)
    cameraSwitchNode.verFilmApp = nAttr.create("verticalFilmApperture", 'vfa', OpenMaya.MFnNumericData.kFloat, 0.945)
    cameraSwitchNode.focalLength = nAttr.create("focalLength", 'fl', OpenMaya.MFnNumericData.kFloat, 35.0)
    cameraSwitchNode.lens = nAttr.create("lensSqueezeRatio", 'lsr', OpenMaya.MFnNumericData.kFloat, 1.0)
    cameraSwitchNode.fstop = nAttr.create("fStop", 'fs', OpenMaya.MFnNumericData.kFloat, 5.6)
    cameraSwitchNode.focusDist = nAttr.create("focusDist", 'fd', OpenMaya.MFnNumericData.kFloat, 5)
    cameraSwitchNode.shutterAngle = nAttr.create("ShutterAngle", 'sa', OpenMaya.MFnNumericData.kFloat, 144)
    cameraSwitchNode.centre = nAttr.create("centreOfInterest", 'ci', OpenMaya.MFnNumericData.kFloat, 5)

    #add attributes
    cameraSwitchNode.addAttribute(cameraSwitchNode.cameraId)
    cameraSwitchNode.addAttribute(cameraSwitchNode.outTrans)
    cameraSwitchNode.addAttribute(cameraSwitchNode.outRot)
    cameraSwitchNode.addAttribute(cameraSwitchNode.outScale)
    cameraSwitchNode.addAttribute(cameraSwitchNode.inputCams)
    cameraSwitchNode.addAttribute(cameraSwitchNode.outPutMsg)
    cameraSwitchNode.addAttribute(cameraSwitchNode.horFilmApp)
    cameraSwitchNode.addAttribute(cameraSwitchNode.verFilmApp)
    cameraSwitchNode.addAttribute(cameraSwitchNode.focalLength)
    cameraSwitchNode.addAttribute(cameraSwitchNode.lens)
    cameraSwitchNode.addAttribute(cameraSwitchNode.fstop)
    cameraSwitchNode.addAttribute(cameraSwitchNode.focusDist)
    cameraSwitchNode.addAttribute(cameraSwitchNode.shutterAngle)
    cameraSwitchNode.addAttribute(cameraSwitchNode.centre)

    #attribute affects
    cameraSwitchNode.attributeAffects(cameraSwitchNode.cameraId, cameraSwitchNode.outTrans)
    cameraSwitchNode.attributeAffects(cameraSwitchNode.cameraId, cameraSwitchNode.outRot)
    cameraSwitchNode.attributeAffects(cameraSwitchNode.cameraId, cameraSwitchNode.outScale)
    cameraSwitchNode.attributeAffects(cameraSwitchNode.cameraId, cameraSwitchNode.horFilmApp)
    cameraSwitchNode.attributeAffects(cameraSwitchNode.cameraId, cameraSwitchNode.verFilmApp)
    cameraSwitchNode.attributeAffects(cameraSwitchNode.cameraId, cameraSwitchNode.focalLength)
    cameraSwitchNode.attributeAffects(cameraSwitchNode.cameraId, cameraSwitchNode.lens)
    cameraSwitchNode.attributeAffects(cameraSwitchNode.cameraId, cameraSwitchNode.fstop)
    cameraSwitchNode.attributeAffects(cameraSwitchNode.cameraId, cameraSwitchNode.focusDist)
    cameraSwitchNode.attributeAffects(cameraSwitchNode.cameraId, cameraSwitchNode.shutterAngle)
    cameraSwitchNode.attributeAffects(cameraSwitchNode.cameraId, cameraSwitchNode.centre)


    return OpenMaya.MStatus.kSuccess


def initializePlugin(obj):
    plugin = OpenMayaMPx.MFnPlugin(obj)
    try:
        plugin.registerNode(nodeTypeName, nodeTypeId, nodeCreator, nodeInitializer, OpenMayaMPx.MPxNode.kDependNode)
    except:
        sys.stderr.write( "Failed to register node: %s" % nodeTypeName)


def uninitializePlugin(obj):
    plugin = OpenMayaMPx.MFnPlugin(obj)
    try:
        plugin.deregisterNode(nodeTypeId)
    except:
        sys.stderr.write( "Failed to deregister node: %s" % nodeTypeName)


# plugin = "/drd/users/arthur.terzis/workspace/test/cameraSwitcher.py"
#cmds.unloadPlugin("cameraSwitcher")
# cmds.loadPlugin(plugin)
