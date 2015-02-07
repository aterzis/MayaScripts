# Author: Guillaume Barlier

import sys
from maya import cmds
from maya import OpenMaya, OpenMayaUI

from Functions import attributeFunctions
from Functions import checkFunctions
from Functions import controlFunctions
from Functions.decoratorFunctions import author
from Functions import handleFunctions
from Functions import shapeFunctions
from Functions import nameFunctions

from Functions import apiFunctions
dp = apiFunctions.Wrapper()

@author('g.barlier')
def follicleRivet(surface, baseName=None, U=0.5, V=0.5, attr=False, shape=True, p=None):
    '''
    Create follicle on surface as a rivet hook
    #    return rivet

    Options:
    -baseName (string): base name string used as prefix for all nodes
    -U (float): u placement
    -v (float): v placement
    -attr (bool): add U and V position option attributes to rivet
    -shape (bool): add locator shaped curve to rivet
    -p (node): rivet target parent node

    author: guillaume barlier
    '''
    #    sanity check
    surface, surfaceShp = shapeFunctions.filterShpAndTransform(surface)
    if not (surface and surfaceShp):
        return

    #    define baseName
    if not baseName:
        baseName    =   'rivet'

    #    create follicle
    follicleShp =   cmds.createNode('follicle')
    follicle    =   cmds.listRelatives(follicleShp, p=True)[0]
    cmds.setAttr('%s.inheritsTransform'%follicle, 0)

    cmds.connectAttr('%s.outRotate'%follicleShp, '%s.rotate'%follicle, f=True)
    cmds.connectAttr('%s.outTranslate'%follicleShp, '%s.translate'%follicle, f=True)

    #    set U V
    cmds.setAttr('%s.pu'%follicleShp, U)
    cmds.setAttr('%s.pv'%follicleShp, V)

    #    rename follicle (createNode create the shape)
    follicle    =   cmds.rename(follicle, baseName)
    follicleShp =   cmds.listRelatives(follicle, s=True)[0]

    #    connect surface to follicle
    cmds.connectAttr('%s.worldMatrix[0]'%surfaceShp, '%s.inputWorldMatrix'%follicleShp, f=True)
    if cmds.nodeType(surfaceShp) == 'nurbsSurface':
        cmds.connectAttr('%s.local'%surfaceShp, '%s.inputSurface'%follicleShp, f=True)
    elif cmds.nodeType(surfaceShp) == 'mesh':
        cmds.connectAttr('%s.worldMesh[0]'%surfaceShp, '%s.inputMesh'%follicleShp, f=True)

    #    add curve locator shape
    locatorShp  =   None
    if shape:
        #    rename.hide follicle shape
        follicleShp = cmds.rename(follicleShp, baseName+'FollicleShape')
        cmds.setAttr('%s.v'%follicleShp, 0)

        #    add curve locator shape
        locatorShp  =    handleFunctions.curveLocator(baseName+'CrvLoc', p=follicle, s=True)
        cmds.reorder(locatorShp, front=True )
        controlFunctions.colorShape([locatorShp], 4)

    #    add custom attribute
    if attr:
        attributeFunctions.createSeparator(follicle)
        cmds.addAttr(follicle, ln='parameterU', sn='pu', at='double')
        cmds.setAttr('%s.pu'%follicle, U, k=True)
        cmds.connectAttr('%s.pu'%follicle, '%s.pu'%follicleShp, f=True)

        cmds.addAttr(follicle, ln='parameterV', sn='pv', at='double')
        cmds.setAttr('%s.pv'%follicle, V, k=True)
        cmds.connectAttr('%s.pv'%follicle, '%s.pv'%follicleShp, f=True)

    #    parent rivet
    if p and cmds.objExists(p):
        cmds.parent(follicle, p)

    #    clean and lock
    attributeFunctions.lockAndHideTransforms(follicle)
    attributeFunctions.lockAll(follicleShp)
    cmds.select(cl=True)

    return follicle


@author('g.barlier')
def makeRivetFromList(objList, surfaceShp, baseName=None, attr=False):
    '''
    Create rivet with closest point on surface for objList

    Options:
    -baseName (string): base name string used as prefix for all nodes
    -attr (bool): add U and V position option attributes to rivet

    author: guillaume barlier
    '''
    #    sanity check
    if not objList:
        if vbzLvl> 0:
            sys.stderr.write('! %s.makeRivetFromList() -> wrong input, aborting\n' % __name__)
        return None

    #    check list type
    if not type(objList) is list:
        objList    =   [objList]

    #    check surface
    surface, surfaceShp = shapeFunctions.filterShpAndTransform(surfaceShp)
    if not surfaceShp:
        return None

    if not cmds.nodeType(surfaceShp) in ['mesh', 'nurbsSurface']:
        if vbzLvl> 0:
            sys.stderr.write('! %s.makeRivetFromList() -> wrong type for %s must be of type mesh or nurbsSurface, aborting\n' % (__name__, surfaceShp))
        return None

    #    define baseName
    if not baseName:
        baseName    =   'rivet'

    #    duplicate/freeze surface (closest point on surface doesn't take into account surface transformations)
    surfaceDup  =   cmds.duplicate(surface, n=surface+'_tmpRivetFreezedDup')[0]
    attributeFunctions.lockAndHideTransforms(surfaceDup, unlock=True)
    if cmds.listRelatives(surfaceDup, p=True):
        cmds.parent(surfaceDup, w=True)
    cmds.makeIdentity(surfaceDup, a=True)
    surfaceDupShp   =   cmds.listRelatives(surfaceDup, s=True, ni=True)[0]

    #    create tmp loc for objection position
    tmpLocShp   =   cmds.createNode('locator')
    tmpLoc      =   cmds.listRelatives(tmpLocShp, p=True)[0]

    tmpLoc      =   cmds.rename(tmpLoc, 'tmpRivetClosestPointLoc')
    tmpLocShp   =   cmds.listRelatives(tmpLoc, s=True)[0]#freaking non object cmds ... :/

    #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    #    position informations
    normalizeUV     =   False
    uRange          =   None
    vRange          =   None

    #    mesh case
    if cmds.nodeType(surfaceShp) == 'mesh':
        #    create/connect closest point on mesh info
        cpInfo  =   cmds.createNode('closestPointOnMesh', n='tmpRivetMeasure_CPOM')
        cmds.connectAttr('%s.outMesh'%surfaceDupShp, '%s.inMesh'%cpInfo)
        cmds.connectAttr('%s.worldPosition'%tmpLocShp, '%s.inPosition'%cpInfo)

    #    nurbsSurface case
    if cmds.nodeType(surfaceShp) == 'nurbsSurface':
        #    create/connect closest point on surface info
        cpInfo    =   cmds.createNode('closestPointOnSurface', n='tmpRivetMeasure_CPOS')
        cmds.connectAttr(surfaceShp+'.local', cpInfo+'.inputSurface', f=True)
        cmds.connectAttr(tmpLocShp+'.worldPosition', cpInfo+'.inPosition', f=True)

        normalizeUV =   True
        uRange      =   cmds.getAttr(surfaceShp+'.minMaxRangeU')[0]
        vRange      =   cmds.getAttr(surfaceShp+'.minMaxRangeV')[0]

    #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    #    create rivet for selected objects
    rivetList   =   []
    for i in range(len(objList)):
        obj = objList[i]

        #    place tmpLoc
        cmds.xform(tmpLoc, ws=True, t=cmds.xform(obj, q=True, ws=True, rp=True))

        #    define rivet name
        rivetName   =   baseName
        if len(objList)>1:
            rivetName   +=  unicode(i+1).zfill(len(unicode(len(objList))))
        if not baseName:
            rivetName   =   obj

        #    define UV coords
        uCoord  =   cmds.getAttr(cpInfo+'.u')
        vCoord  =   cmds.getAttr(cpInfo+'.v')

        if normalizeUV:
            #    follicles on nurbsSurfaces use normalized UV
            uCoord  =   abs((uCoord-uRange[0])/(uRange[1]-uRange[0]))
            vCoord  =   abs((vCoord-vRange[0])/(vRange[1]-vRange[0]))

        #    create follicle rivet
        rivetList.append(follicleRivet(surface, baseName=rivetName, U=uCoord, V=vCoord, attr=attr))

    #    clean tmp stuff
    cmds.delete([cpInfo, surfaceDup, tmpLoc])

    return rivetList

@author('g.barlier')
def getClosestUVValuesOnMesh(shape, coordinates, offset=False):
    ''''''
    #    filter inputs
    shape = dp.DependNode(shape).filterTransformAndShape()[1]
    coordinates = dp.vector(coordinates)
    pt = OpenMaya.MPoint(coordinates)

    #    offset point to prevent edge bug
    if offset:
        pt =   getOffsetedMPointOnMFnMesh(shape.asMFnMesh(), pt)

    #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    #    get uv values for closest point

    #    mesh case
    if shape.asMObject().hasFn(OpenMaya.MFn.kMesh):

        #    make float2 api array...
        pArray = [0,0]
        x1 = OpenMaya.MScriptUtil()
        x1.createFromList( pArray, 2 )
        uvPoint = x1.asFloat2Ptr()

        #    get values
        shape.asMFnMesh().getUVAtPoint(pt, uvPoint)

        #    get float values from float2 api array ...
        u = OpenMaya.MScriptUtil.getFloat2ArrayItem( uvPoint, 0, 0 )
        v = OpenMaya.MScriptUtil.getFloat2ArrayItem( uvPoint, 0, 1 )

        return u, v

#    #    nurbs case
#    elif shape.asMObject().hasFn(OpenMaya.MFn.kNurbsSurface):
#        #    get closest point on surface
#        closestPt = shape.asMFnNurbsSurface().closestPoint(pt)
#
#        u = 0.0 double type ....
#        v = 0.0
#        shape.asMFnNurbsSurface().getParamAtPoint(closestPt, u, v)
#
#        return u, v

    else:
        print 'input shape must but mesh (nurbsSurface to be implemented ...)'





@author('g.barlier')
def getOffsetedMPointOnMFnMesh(mfnMesh, mPoint, factor=0.001):
    '''
    return offested MPoint coordinate on face
    to prevent geoConstraint orient bug on edge of face
    '''
    #    get closest face
    polyInt = OpenMaya.MScriptUtil().asIntPtr()
    pt = OpenMaya.MPoint()
    mfnMesh.getClosestPoint( mPoint, pt, OpenMaya.MSpace.kObject, polyInt)
    if polyInt == -1:
        print 'unexpected poly int'
        return

    faceIndex = OpenMaya.MScriptUtil.getIntArrayItem(polyInt, 0)

    #    get face iterator
    polyIt = OpenMaya.MItMeshPolygon(mfnMesh.object())
    prevIndex = OpenMaya.MScriptUtil().asIntPtr()
    polyIt.setIndex(faceIndex, prevIndex)

    #    get face vertices
    vtxArray = OpenMaya.MIntArray()
    polyIt.getVertices(vtxArray)

    #    get closest vtx to point
    minDist = 10e32
    closestIndex = -1
    ptArray = list()
    for i in range(vtxArray.length()):
        vtxIndex = vtxArray[i]

        vtxPt = OpenMaya.MPoint()
        mfnMesh.getPoint(vtxIndex, vtxPt)
        ptArray.append(vtxPt)

        distance = vtxPt.distanceTo(mPoint)
        if distance < minDist:
            minDist = distance
            closestIndex = i

    #    define closest vtx edge vector
    if closestIndex+1 >= vtxArray.length():
        vec1 = ptArray[0]-ptArray[closestIndex]
    else:
        vec1 = ptArray[closestIndex+1]-ptArray[closestIndex]

    vec2 = ptArray[closestIndex-1]-ptArray[closestIndex]

    #    get offset vector
    offsetVector = vec1*vec1.length()*factor + vec2*vec2.length()*factor

    #    apply offset to input MPoint
    resultPt = mPoint + offsetVector

    return resultPt





#===============================================================================
# #Utility Functions  ---
#===============================================================================
@author('g.barlier')
def getUVvalues(objList, surfaceShp):
    '''
    returns a list of UV values in the form [[u1, v1], [u2, v2], ....etc]

    objList : a list of locators / guides that you want to find the uv value of on a mesh
    surfaceShp: the mesh shape you want to find the UV values on

    this code was extracted from the makeRivetFromList function, to be able to be used with other nodes than follicle
    e.g. arrayGeoConstraint
    '''

    #    check surface
    surface, surfaceShp = shapeFunctions.filterShpAndTransform(surfaceShp)
    if not surfaceShp:
        return None

    #    duplicate/freeze surface (closest point on surface doesn't take into account surface transformations)
    surfaceDup  =   cmds.duplicate(surface, n=surface+'_tmpRivetFreezedDup')[0]
    attributeFunctions.lockAndHideTransforms(surfaceDup, unlock=True)
    if cmds.listRelatives(surfaceDup, p=True):
        cmds.parent(surfaceDup, w=True)
    cmds.makeIdentity(surfaceDup, a=True)
    surfaceDupShp   =   cmds.listRelatives(surfaceDup, s=True, ni=True)[0]

    #    create tmp loc for objection position
    tmpLocShp   =   cmds.createNode('locator')
    tmpLoc      =   cmds.listRelatives(tmpLocShp, p=True)[0]

    tmpLoc      =   cmds.rename(tmpLoc, 'tmpRivetClosestPointLoc')
    tmpLocShp   =   cmds.listRelatives(tmpLoc, s=True)[0]#freaking non object cmds ... :/

    #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    #    position informations
    normalizeUV     =   False
    uRange          =   None
    vRange          =   None

    #    mesh case
    if cmds.nodeType(surfaceShp) == 'mesh':
        #    create/connect closest point on mesh info
        cpInfo  =   cmds.createNode('closestPointOnMesh', n='tmpRivetMeasure_CPOM')
        cmds.connectAttr('%s.outMesh'%surfaceDupShp, '%s.inMesh'%cpInfo)
        cmds.connectAttr('%s.worldPosition'%tmpLocShp, '%s.inPosition'%cpInfo)

    #    nurbsSurface case
    if cmds.nodeType(surfaceShp) == 'nurbsSurface':
        #    create/connect closest point on surface info
        cpInfo    =   cmds.createNode('closestPointOnSurface', n='tmpRivetMeasure_CPOS')
        cmds.connectAttr(surfaceShp+'.local', cpInfo+'.inputSurface', f=True)
        cmds.connectAttr(tmpLocShp+'.worldPosition', cpInfo+'.inPosition', f=True)

        normalizeUV =   True
        uRange      =   cmds.getAttr(surfaceShp+'.minMaxRangeU')[0]
        vRange      =   cmds.getAttr(surfaceShp+'.minMaxRangeV')[0]

    #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    #    create rivet for selected objects
    uvValues   =   []

    for i in range(len(objList)):
        obj = objList[i]

        #    place tmpLoc
        cmds.xform(tmpLoc, ws=True, t=cmds.xform(obj, q=True, ws=True, rp=True))

        #    define UV coords
        uCoord  =   cmds.getAttr(cpInfo+'.u')
        vCoord  =   cmds.getAttr(cpInfo+'.v')

        if normalizeUV:
            #    follicles on nurbsSurfaces use normalized UV
            uCoord  =   abs((uCoord-uRange[0])/(uRange[1]-uRange[0]))
            vCoord  =   abs((vCoord-vRange[0])/(vRange[1]-vRange[0]))

        uvValues.append([uCoord, vCoord])
    #    clean tmp stuff
    cmds.delete([cpInfo, surfaceDup, tmpLoc])

    return uvValues

@author('g.barlier')
def meshToJointArray(mesh, parent=None, compIndexList=None):
    '''Create joint for every vertex on mesh'''
    #    sanity check
    if not dp.objExists(mesh):
        sys.stderr.write('! meshToJointArray() -> input %s not found, aborting\n'%unicode(mesh))
        return
    mesh, shape = dp.DependNode(mesh).filterTransformAndShape()
    if not (shape and shape.asMObject().hasFn(OpenMaya.MFn.kMesh)):
        sys.stderr.write('! meshToJointArray() -> invalid shape, aborting\n')
        return

    if parent:
        if dp.objExists(parent):
            parent = dp.DependNode(parent)
        else:
            sys.stdout.write('#* meshToJointArray() -> parent %s not found, setting to None\n'%unicode(parent))
            parent = None

    #    load plugin
    checkFunctions.loadPlugin('rigSkinClusterDq')

    #    create arrayGeoConstraint
    arrayGeoCst = nameFunctions.changeType(mesh.name(), 'agc')
    if not dp.objExists(arrayGeoCst):
        arrayGeoCst = dp.createNode('arrayGeoConstraint', n=arrayGeoCst)
        shape.connect(arrayGeoCst, 'worldMesh', 'inMesh')
        arrayGeoCst.setAttr('constraintMode', 1)
        arrayGeoCst.setAttr('OutputMode', 1)
    else:
        arrayGeoCst = dp.DependNode(arrayGeoCst)

    #    parent case decompose matrix
    if parent:
        dmx = nameFunctions.changeType(mesh.name(), 'dmx').split(':')[-1]
        dmx = dp.createNode('decomposeMatrix', n=dmx)
        parent.connect(dmx, 'worldMatrix', 'inputMatrix')

    #    define array size
    vtxCount = shape.asMItGeometry().count()
    indexList = compIndexList
    if not compIndexList:
        indexList = range(vtxCount)
    else:
        vtxCount = len(indexList)

    #    init progress window
    pWin = OpenMayaUI.MProgressWindow()
    pWinState = pWin.reserve()
    if pWinState:
        pWin.startProgress()
        pWin.setTitle('Processing %s to joints'%shape.name())
        pWin.setProgressRange( 0, vtxCount )

    #    parse vtx
    baseJntName = nameFunctions.changeType(mesh.name(), 'jnt').split(':')[-1]
    jointList = dp.DependNodeArray()
    arrayIndex = arrayGeoCst.getAttr('uValue', size=True)
    for i in indexList:
        #    update feedback ui
        if pWinState:
            pWin.setProgressStatus( 'processing component %d (%d/%d)'%(i, arrayIndex, vtxCount))
            pWin.advanceProgress( 1 )

        #    get cv coordinates
        cvPos = dp.xform('%s.vtx[%d]'%(shape, i), q=True, t=True, ws=True)

        #    set geoCosntraint values
        u,v = getClosestUVValuesOnMesh(shape, cvPos, offset=True)

        if not ( (0<u<1) and (0<v<1) ):
            sys.stdout.write('#* meshToJointArray() -> invalid u/v for component %d of %s, clamping\n'%(i, shape.name()))
            u = max(0.001, min(u, 1))
            v = max(0.001, min(v, 1))

        arrayGeoCst.setAttr('uValue[%d]'%arrayIndex, u, l=True)
        arrayGeoCst.setAttr('vValue[%d]'%arrayIndex, v, l=True)

        #   create joint
        jnt = nameFunctions.addDescriptionToName(baseJntName, unicode(i).zfill(len(unicode(vtxCount))))
        jnt = dp.createNode('joint', n=jnt, p=parent)
        jointList.append(jnt)

        #    connect joint
        multMat = nameFunctions.changeType(jnt.name(), 'mm')
        multMat = dp.createNode('multMatrix', n=multMat)
        arrayGeoCst.connect(multMat, 'outMatrices[%d]'%arrayIndex, 'matrixIn[0]')
        jnt.connect(multMat, 'parentInverseMatrix', 'matrixIn[1]')

        decompMat = nameFunctions.changeType(jnt.name(), 'dm')
        decompMat = dp.createNode('decomposeMatrix', n=decompMat)
        multMat.connect(decompMat, 'matrixSum', 'inputMatrix')

        decompMat.connect(jnt, 'outputTranslate', 't')
        decompMat.connect(jnt, 'outputRotate', 'r')

#        if not parent:
#            arrayGeoCst.connect(jnt, 'outTranslate[%d]'%arrayIndex, 't')
#        else:
#            #    create pointMatrixMult
#            pmm = nameFunctions.changeType(jnt.name(), 'pmm')
#            pmm = dp.createNode('pointMatrixMult', n=pmm)
#
#            arrayGeoCst.connect(pmm, 'outTranslate[%d]'%arrayIndex, 'inPoint')
#            parent.connect(pmm, 'worldInverseMatrix', 'inMatrix')
#
#            #    connect to joint
#            pmm.connect(jnt, 'output', 't')

        #    increment array index
        arrayIndex += 1

    #    end progress window
    if pWinState:
        pWin.endProgress()


    return jointList


def meshToJointArrayFollicle(mesh, parent=None, compIndexList=None):
    '''
    Create joint for every vertex on mesh
    Follicle solution since the geoCosntraint orientation is not reliable enough...
    '''
    #    sanity check
    if not dp.objExists(mesh):
        sys.stderr.write('! meshToJointArray() -> input %s not found, aborting\n'%unicode(mesh))
        return
    mesh, shape = dp.DependNode(mesh).filterTransformAndShape()
    if not (shape and shape.asMObject().hasFn(OpenMaya.MFn.kMesh)):
        sys.stderr.write('! meshToJointArray() -> invalid shape, aborting\n')
        return

    if parent:
        if dp.objExists(parent):
            parent = dp.DependNode(parent)
        else:
            sys.stdout.write('#* meshToJointArray() -> parent %s not found, setting to None\n'%unicode(parent))
            parent = None

    #    define array size
    vtxCount = shape.asMItGeometry().count()
    indexList = compIndexList
    if not compIndexList:
        indexList = range(vtxCount)
    else:
        vtxCount = len(indexList)

    #    init progress window
#    pWin = OpenMayaUI.MProgressWindow()
#    pWinState = pWin.reserve()
#    if pWinState:
#        pWin.startProgress()
#        pWin.setTitle('Processing %s to joints'%shape.name())
#        pWin.setProgressRange( 0, vtxCount )

    #    parse vtx
    baseJntName = nameFunctions.changeType(mesh.name(), 'jnt').split(':')[-1]
    jointList = dp.DependNodeArray()
    arrayIndex=0
    for i in indexList:
        #    update feedback ui
#        if pWinState:
#            pWin.setProgressStatus( 'processing component %d (%d/%d)'%(i, arrayIndex, vtxCount))
#            pWin.advanceProgress( 1 )

        #    get cv coordinates
        cvPos = dp.xform('%s.vtx[%d]'%(shape, i), q=True, t=True, ws=True)

        #    set geoCosntraint values
        u,v = getClosestUVValuesOnMesh(shape, cvPos, offset=True)

        if not ( (0<u<1) and (0<v<1) ):
            sys.stdout.write('#* meshToJointArray() -> invalid u/v for component %d of %s, clamping\n'%(i, shape.name()))
            u = max(0.001, min(u, 1))
            v = max(0.001, min(v, 1))

        #    create follicle
        jnt = nameFunctions.addDescriptionToName(baseJntName, unicode(i).zfill(len(unicode(vtxCount))))
        rivet = nameFunctions.addDescriptionToNameFix(jnt, 'Rivet')
        rivet = follicleRivet(shape, rivet, U=u, V=v, p=parent)

        #   create joint
        jnt = dp.createNode('joint', n=jnt, p=rivet)
        jointList.append(jnt)

        #    increment array index
        arrayIndex += 1

#    #    end progress window
#    if pWinState:
#        pWin.endProgress()

    return jointList

#===============================================================================
#    old stuff    ---
#===============================================================================

#    replaced by follicleRivet
#def matrixSurfaceRivet(name, surfaceShp, U=0.5, V=0.5):
#    '''
#    Create a locator riveted to surface with a fourByFourMatrix solution (cf Tim)
#
#    NOTES:
#    -surfaceShp must be a nurbsSurface shape or a transform containing a nurbsSurface
#    '''
#    #    check surfaceShp type
#    if not cmds.nodeType(surfaceShp) == 'nurbsSurface':
#        shpList =   cmds.listRelatives(surfaceShp, s=True, type='nurbsSurface')
#        if not shpList:
#            sys.stderr.write('! %s.constraintToTarget() -> input %s has no nurbsSurface shape, aborting\n' % (__name__, surfaceShp))
#            return
#        surfaceShp  =   shpList[0]
#
#    #    create locator
#    if not cmds.objExists(name):
#        name = cmds.createNode('transform', n=name)
#        cmds.createNode('locator', p=name, n=name+'Shape')
#    cmds.setAttr(name+'.inheritsTransform', 0)
#
#    #    point on surface info
#    ptSurfInf   =   cmds.createNode('pointOnSurfaceInfo', n=name+'_POSI')
#    cmds.connectAttr(surfaceShp+'.worldSpace',  ptSurfInf+'.inputSurface')
#    cmds.setAttr(ptSurfInf+'.turnOnPercentage', True, l=True)
#    cmds.setAttr(ptSurfInf+'.parameterU', U)
#    cmds.setAttr(ptSurfInf+'.parameterV', V)
#
#    #    vector product
#    vectorProduct   =   cmds.createNode('vectorProduct', n=name+'_VP')
#    cmds.setAttr(vectorProduct+'.operation', 2, l=True)
#
#    cmds.connectAttr(ptSurfInf+'.normal', vectorProduct+'.input1')
#    cmds.connectAttr(ptSurfInf+'.tangentU', vectorProduct+'.input2')
#
#    #    fourByFour
#    fbfm    =   cmds.createNode('fourByFourMatrix', n=name+'_FBFM')
#
#    cmds.connectAttr(vectorProduct+'.outputX', fbfm+'.in00')
#    cmds.connectAttr(vectorProduct+'.outputY', fbfm+'.in01')
#    cmds.connectAttr(vectorProduct+'.outputZ', fbfm+'.in02')
#
#    cmds.connectAttr(ptSurfInf+'.normalizedNormalX', fbfm+'.in10')
#    cmds.connectAttr(ptSurfInf+'.normalizedNormalY', fbfm+'.in11')
#    cmds.connectAttr(ptSurfInf+'.normalizedNormalZ', fbfm+'.in12')
#
#    cmds.connectAttr(ptSurfInf+'.normalizedTangentUX', fbfm+'.in20')
#    cmds.connectAttr(ptSurfInf+'.normalizedTangentUY', fbfm+'.in21')
#    cmds.connectAttr(ptSurfInf+'.normalizedTangentUZ', fbfm+'.in22')
#
#    cmds.connectAttr(ptSurfInf+'.positionX', fbfm+'.in30')
#    cmds.connectAttr(ptSurfInf+'.positionY', fbfm+'.in31')
#    cmds.connectAttr(ptSurfInf+'.positionZ', fbfm+'.in32')
#
#    #    decompose matrix
#    decomp  =   cmds.createNode('decomposeMatrix', n=name+'_DM')
#    cmds.connectAttr(fbfm+'.output', decomp+'.inputMatrix')
#
#    #    connect obj
#    cmds.connectAttr(decomp+'.outputTranslate', name+'.t')
#    cmds.connectAttr(decomp+'.outputRotate', name+'.r')
#    cmds.connectAttr(decomp+'.outputScale', name+'.s')
#
#    #    clean/lock
#    attributeFunctions.lockAll(name)
#
#    return name

#    replaced by makeRivetFromList
#def createClosestMatrixSurfaceRivet(objList, surfaceShp):
#    '''Create a matrix rivet for each obj in list based on closest point on surface'''
#    #    check input type
#    if not type(objList) == list:
#        objList =   [objList]
#
#    #    check surfaceShp type
#    surface =   surfaceShp
#    if not cmds.nodeType(surfaceShp) == 'nurbsSurface':
#        shpList =   cmds.listRelatives(surfaceShp, s=True, type='nurbsSurface')
#        if not shpList:
#            sys.stderr.write('! %s.constraintToTarget() -> input %s has no nurbsSurface shape, aborting\n' % (__name__, surfaceShp))
#            return
#        surfaceShp  =   shpList[0]
#    else:
#        surface =   cmds.listRelatives(surfaceShp, p=True)[0]
#
#    #    duplicate/freeze surface (closest point on surface doesn't take into account surface transformations)
#    surfaceDup  =   cmds.duplicate(surface, n=surface+'_tmpRivetFreezedDup')[0]
#    attributeFunctions.lockAll(surfaceDup, unlock=True)
#    if cmds.listRelatives(surfaceDup, p=True):
#        cmds.parent(surfaceDup, w=True)
#    cmds.makeIdentity(surfaceDup, a=True)
#
#    #    create tmp loc for objection position
#    tmpLoc  =   cmds.createNode('transform', n='tmpRivetClosestPointLoc')
#    locShp  =   cmds.createNode('locator', p=tmpLoc, n=tmpLoc+'Shape')
#
#
#    """
#    #    mesh case
#    if surfaceShp.type()=='mesh':
#        #    create/connect closest point on mesh info
#        cpInfo  =   pmc.createNode('closestPointOnMesh', n='tmpRivetMeasure_CPOM')
#        surfaceDup.getShape().outMesh   >>  cpInfo.inMesh
#        tmpLoc.getShape().worldPosition >>  cpInfo.inPosition
#    """
#    #    nurbsSurface case
#    normalizeUV     =   False
#    uRange          =   None
#    vRange          =   None
#    if cmds.nodeType(surfaceShp)=='nurbsSurface':
#        #    create/connect closest point on surface info
#        cpInfo  =   cmds.createNode('closestPointOnSurface', n='tmpRivetMeasure_CPOS')
#        dupShp  =   cmds.listRelatives(surfaceDup, s=True)[0]
#        cmds.connectAttr(dupShp+'.local', cpInfo+'.inputSurface')
#        cmds.connectAttr(locShp+'.worldPosition', cpInfo+'.inPosition')
#
#        normalizeUV =   True
#        uRange      =   cmds.getAttr(surfaceShp+'.minMaxRangeU')
#        vRange      =   cmds.getAttr(surfaceShp+'.minMaxRangeV')
#
#    #    create rivet for selected objects
#    rivetList   =   []
#    for obj in objList:
#        #    place tmpLoc
#        cmds.xform(tmpLoc, ws=True, t=cmds.xform(obj, q=True, ws=True, rp=True))
#
#        #    define UV coords
#        uCoord  =   cmds.getAttr(cpInfo+'.u')
#        vCoord  =   cmds.getAttr(cpInfo+'.v')
#
#        if normalizeUV:
#            #    follicles on nurbsSurfaces use normalized UV
#            uCoord  =   abs((uCoord-uRange[0][0])/(uRange[0][1]-uRange[0][0]))
#            vCoord  =   abs((vCoord-vRange[0][0])/(vRange[0][1]-vRange[0][0]))
#
#        #    create rivet
#        rivetList.append(matrixSurfaceRivet(obj+'Rivet', surface, U=uCoord, V=vCoord))
#
#    #    clean
#    cmds.delete([tmpLoc, surfaceDup])
#
#    return rivetList
