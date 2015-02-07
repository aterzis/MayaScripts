import sys
import maya.OpenMaya as OpenMaya
import maya.OpenMayaMPx as OpenMayaMPx


nodeTypeName = "UVinfo"
nodeTypeId = OpenMaya.MTypeId(0x00123)


class UVinfoNode(OpenMayaMPx.MPxNode):
    def __init__(self):
        OpenMayaMPx.MPxNode.__init__(self)

    def compute(self, plug, dataBlock):
        meshObj = dataBlock.inputValue(UVinfoNode.inMesh).asMesh()
        pointX = dataBlock.inputValue(UVinfoNode.pointX).asFloat()
        pointY = dataBlock.inputValue(UVinfoNode.pointY).asFloat()
        pointZ = dataBlock.inputValue(UVinfoNode.pointZ).asFloat()

        # check if there is no connection
        if meshObj.isNull():
            return False

        # calculate
        mesh = OpenMaya.MFnMesh(meshObj)
        mPoint = OpenMaya.MPoint(pointX, pointY, pointZ )

        # find and use the default UV set
        setList = list()
        mesh.getUVSetNames(setList)
        uvSet = setList[0]

        # define the float2
        pArray = [0, 0]
        floatPtr = OpenMaya.MScriptUtil()
        floatPtr.createFromList(pArray, 2)
        uvPoint = floatPtr.asFloat2Ptr()

        mesh.getUVAtPoint(mPoint, uvPoint, OpenMaya.MSpace.kObject , uvSet)
        u = OpenMaya.MScriptUtil.getFloat2ArrayItem(uvPoint, 0, 0)
        v = OpenMaya.MScriptUtil.getFloat2ArrayItem(uvPoint, 0, 1)

        #set the value
        uPlug = OpenMaya.MPlug(self.thisMObject(), UVinfoNode.Ucoord)
        vPlug = OpenMaya.MPlug(self.thisMObject(), UVinfoNode.Vcoord)

        uPlug.setFloat(u)
        vPlug.setFloat(v)

        dataBlock.setClean( plug )


def nodeCreator():
    return OpenMayaMPx.asMPxPtr(UVinfoNode())


def nodeInitializer():
    nAttr = OpenMaya.MFnNumericAttribute()
    gAttr = OpenMaya.MFnGenericAttribute()
    cAttr = OpenMaya.MFnCompoundAttribute()

    # define attributes
    UVinfoNode.inMesh = gAttr.create("inMesh", "im")
    gAttr.setConnectable(True)
    gAttr.setKeyable(True)
    gAttr.setStorable(True)
    gAttr.setReadable(True)
    gAttr.addDataAccept( OpenMaya.MFnData.kMesh)


    UVinfoNode.pointX = nAttr.create( "Px", "px", OpenMaya.MFnNumericData.kFloat )
    nAttr.setStorable(True)
    nAttr.setWritable(True)

    UVinfoNode.pointY = nAttr.create( "Py", "py", OpenMaya.MFnNumericData.kFloat )
    nAttr.setStorable(True)
    nAttr.setWritable(True)

    UVinfoNode.pointZ = nAttr.create( "Pz", "pz", OpenMaya.MFnNumericData.kFloat )
    nAttr.setStorable(True)
    nAttr.setWritable(True)

    UVinfoNode.point = cAttr.create("point", "pnt")
    cAttr.addChild(UVinfoNode.pointX)
    cAttr.addChild(UVinfoNode.pointY)
    cAttr.addChild(UVinfoNode.pointZ)


    UVinfoNode.Ucoord = nAttr.create( "U", "u", OpenMaya.MFnNumericData.kFloat )
    nAttr.setStorable(True)
    nAttr.setStorable(True)
    nAttr.setConnectable(True)

    UVinfoNode.Vcoord = nAttr.create( "V", "v", OpenMaya.MFnNumericData.kFloat )
    nAttr.setStorable(True)
    nAttr.setReadable(True)
    nAttr.setConnectable(True)

    UVinfoNode.UV = cAttr.create("UVCoordinates", "uv")
    cAttr.addChild(UVinfoNode.Ucoord)
    cAttr.addChild(UVinfoNode.Vcoord)

     #add attributes
    UVinfoNode.addAttribute(UVinfoNode.inMesh)
    UVinfoNode.addAttribute(UVinfoNode.point)
    UVinfoNode.addAttribute(UVinfoNode.UV)

    #attribute affects
    UVinfoNode.attributeAffects(UVinfoNode.inMesh, UVinfoNode.UV)
    UVinfoNode.attributeAffects(UVinfoNode.point, UVinfoNode.UV)

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
