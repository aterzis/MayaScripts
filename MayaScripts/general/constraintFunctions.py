import sys
from maya import cmds
from maya import OpenMaya
from maya import mel
import math
from Functions import attributeFunctions
from Functions import checkFunctions
from Functions import connectFunctions
from Functions import dagFunctions
from Functions import nameFunctions
from Functions import nodeFunctions
from Functions import xformFunctions
from Functions import apiFunctions

from Functions.errorFunctions import GeppettoError
from Interfaces import loggerInterfaces

def applyRetarget(inputExternalNode, outputNode, externalNodeParent = None, outputNodeParent = None,translate=True, rotate=True):
    def _setMatrixAttr(matrix, attr):
        evalString = 'setAttr -type "matrix" "' + attr + '" '
        evalString += str(matrix(0, 0)) + ' '
        evalString += str(matrix(0, 1)) + ' '
        evalString += str(matrix(0, 2)) + ' '
        evalString += str(matrix(0, 3)) + ' '
        evalString += str(matrix(1, 0)) + ' '
        evalString += str(matrix(1, 1)) + ' '
        evalString += str(matrix(1, 2)) + ' '
        evalString += str(matrix(1, 3)) + ' '
        evalString += str(matrix(2, 0)) + ' '
        evalString += str(matrix(2, 1)) + ' '
        evalString += str(matrix(2, 2)) + ' '
        evalString += str(matrix(2, 3)) + ' '
        evalString += str(matrix(3, 0)) + ' '
        evalString += str(matrix(3, 1)) + ' '
        evalString += str(matrix(3, 2)) + ' '
        evalString += str(matrix(3, 3))

        mel.eval(evalString)

    def _getWorldMatrix(nodeName):
        worldMatrix = OpenMaya.MMatrix()
        if nodeName:
            sel = OpenMaya.MSelectionList()
            sel.add(nodeName)
            dagPath = OpenMaya.MDagPath()
            sel.getDagPath(0, dagPath)
            worldMatrix = dagPath.inclusiveMatrix()

        return worldMatrix

    node = cmds.createNode("rigRetargetConstraint")

    externalParentMatrix = OpenMaya.MMatrix()
    if externalNodeParent:
        externalParentMatrix = _getWorldMatrix(externalNodeParent)

    parentMatrix = OpenMaya.MMatrix()
    if outputNodeParent:
        parentMatrix = _getWorldMatrix(outputNodeParent)

    externalMatrix = _getWorldMatrix(inputExternalNode)
    childMatrix = _getWorldMatrix(outputNode)

    externalOffset = childMatrix * externalMatrix.inverse()
    externalParentOffset = externalParentMatrix * parentMatrix.inverse()
    localOffset = childMatrix * parentMatrix.inverse()

    _setMatrixAttr(externalOffset, node + ".externalOffset")
    _setMatrixAttr(externalParentOffset, node + ".externalParentOffset")
    _setMatrixAttr(localOffset, node + ".localOffset")

    if externalNodeParent:
        cmds.connectAttr(externalNodeParent + ".worldMatrix", node + ".externalParent")

    if outputNodeParent:
        cmds.connectAttr(outputNodeParent + ".worldMatrix", node + ".parent")

    cmds.connectAttr(inputExternalNode + ".worldMatrix", node + ".external")

    if translate:
        cmds.connectAttr(node + ".outTranslate", outputNode + ".translate")
    if rotate:
        cmds.connectAttr(node + ".outRotate", outputNode + ".rotate")

    return node


def weightedBlend(driver1, driver2, driven, weightTo1 = .5,switchObject = None, switchName = None, constraintType = 'orient', switchRange = 10):
    '''
    constrains the driven to the drivers with a preset weight - ie if weightTo1 is set to .8, then
    the function weights the constrain .8 to driver1 and .2 to driver 2.  A control is created on the swith object from -1 0, 1,
    '0' keeps the .8/.2 split,  '-1' weights 100% to object 2, and '1' weights it 100% to object 1.
    the range input sets the maximum value of the resulting slider on the switch onbject
    '''
    splitName = str(driven).split('_')
    #make constraint
    if constraintType == 'orient':
        constraint = cmds.orientConstraint(driver1, driven,  mo = True, w = weightTo1, n = splitName[0]+'_ocn_'+splitName[2]+'BlendedConstraint_'+splitName[-1])
        constraintA = cmds.orientConstraint(driver2, driven, mo = True, w = 1-weightTo1)
        cmds.setAttr(constraint[0]+'.interpType', 2)
#    elif constraintType == 'parent':
#        constraint = cmds.parentConstraint(driver1,  driven,  mo = True, w = [weightTo1], n = splitName[0]+'_pcn_'+splitName[2]+'BlendedConstraint_'+splitName[-1], st = ['x','y','z'])
#        constraintA = constraint = cmds.parentConstraint(driver2, driven,  mo = True, w = [weightTo1], n = splitName[0]+'_pcn_'+splitName[2]+'BlendedConstraintA_'+splitName[-1], st = ['x','y','z'])
#        cmds.setAttr(constraint[0]+'.interpType', 0)
#         cmds.setAttr(constraintA[0]+'.interpType', 0)
    else:
        print ' hey - if you a constraint of type '+constraintType+' go ahead and implement it - cos it aint here!'
    if switchName == None:
        #make or find blenderSwitch on switchObject
        if 'weightedBlender' in cmds.listAttr(switchObject): #not super-robust for multiples - fix if needed later
            pass
        else:
            cmds.addAttr(switchObject, ln = 'weightedBlender', dv = 0, min = -switchRange, max = switchRange, keyable = True)
        blendAttr = switchObject+'.weightedBlender'
    else:
        if switchName in cmds.listAttr(switchObject): #not super-robust for multiples - fix if needed later
            pass
        else:
            cmds.addAttr(switchObject, ln = switchName, dv = 0, min = -switchRange, max = switchRange, keyable = True)
        blendAttr = switchObject+'.'+switchName


    #setup the blender
    ramp = cmds.createNode('remapValue', n = splitName[0]+'_rmp_'+splitName[2]+'weightTo1_'+splitName[-1])
    cmds.setAttr(ramp+'.inputMin', -switchRange)
    cmds.setAttr(ramp+'.inputMax', switchRange)
    cmds.setAttr(ramp+'.value[0].value_Position', 0 )
    cmds.setAttr(ramp+'.value[0].value_FloatValue',0 )
#    cmds.setAttr(ramp+'.value[0].value_Interp', 2)
    cmds.setAttr(ramp+'.value[1].value_Position', .5 )
    cmds.setAttr(ramp+'.value[1].value_FloatValue',weightTo1)
    cmds.setAttr(ramp+'.value[1].value_Interp', 2)
    cmds.setAttr(ramp+'.value[2].value_Position', 1 )
    cmds.setAttr(ramp+'.value[2].value_FloatValue',1 )
#    cmds.setAttr(ramp+'.value[2].value_Interp', 2)


    #setup the reverse
    reverse = cmds.createNode('reverse', n = splitName[0]+'_rvs_'+splitName[2]+'weightTo2_'+splitName[-1])
    #connect them!!!
    cmds.connectAttr(blendAttr, ramp+'.inputValue')
    cmds.connectAttr(ramp+'.outValue', reverse+'.inputX')
    cmds.connectAttr(ramp+'.outValue', constraint[0]+'.'+driver1+'W0' )
    cmds.connectAttr(reverse+'.outputX', constraint[0]+'.'+driver2+'W1' )

def pointSwitch(control, driven, drivers, attrName, attachPointIndex, defaultValue, enumName):
    '''
    Similar as a parent switch but only for translation/position (does not get affect by rotation in any way)
    '''
    createNodeClass = nodeFunctions.CreateUtilityNode()

    side = nameFunctions.getSide(driven)
    description = nameFunctions.getDescription(driven)

    drivenParent=dagFunctions.addParent(driven)
    drivenConstraint=dagFunctions.addParent(drivenParent)

    #    ADD ATTRIBUTE
    enum = ''
    for i in range(len(drivers)):
            enum = enum.__add__(enumName[i]+':')
    cmds.addAttr(control, k=True, ln= attrName, at='enum', en=enum, dv=defaultValue)

    #    GET OFFSETS
    offsets=[]
    for i in range(len(drivers)):
        offsets.append(xformFunctions.worldOffsetBetween(drivers[i], driven))

    #    CREATE POINT CONSTRAINT
    con=cmds.pointConstraint(drivers, drivenParent, n=side + '_pnt_' + description + drivers[i].capitalize() + 'PointSwitchConstraint_0')

    #    SWITCH between the different spaces
    offPma = createNodeClass.create('plusMinusAverage', side, description + drivers[i].capitalize() + 'PointSwitchOffset', 0)
    cmds.connectAttr(offPma + '.output3D', con[0] + '.offset')
    for i in range(len(drivers)):
        valCon = createNodeClass.create('condition', side, description + drivers[i].capitalize() + 'PointSwitchValue', 0)
        cmds.connectAttr((control + '.' + attrName), (valCon + '.firstTerm'))
        cmds.setAttr ((valCon + '.colorIfTrueR'), 1)
        cmds.setAttr ((valCon + '.colorIfFalseR'), 0)
        cmds.setAttr ((valCon + '.secondTerm'), i)
        cmds.connectAttr((valCon + '.outColorR'), (con[0] + '.' + drivers[i] + 'W' + str(i)))

        offCon = createNodeClass.create('condition', side, description + drivers[i].capitalize() + 'PointSwitchOffset', 0)
        cmds.connectAttr((control + '.' + attrName), (offCon + '.firstTerm'))
        cmds.setAttr ((offCon + '.colorIfTrueR'), offsets[i][0])
        cmds.setAttr ((offCon + '.colorIfTrueG'), offsets[i][1])
        cmds.setAttr ((offCon + '.colorIfTrueB'), offsets[i][2])
        cmds.setAttr ((offCon + '.colorIfFalseR'), 0)
        cmds.setAttr ((offCon + '.colorIfFalseG'), 0)
        cmds.setAttr ((offCon + '.colorIfFalseB'), 0)
        cmds.setAttr ((offCon + '.secondTerm'), i)
        cmds.connectAttr(offCon + '.outColor', offPma + '.input3D[' + str(i) + ']')

    cmds.parentConstraint(drivers[attachPointIndex], drivenConstraint, mo=True)

    #    Clean up the Create Node Class.
    createNodeClass.lockAndHide()
    createNodeClass.setIsHistoricallyInteresting()

    return drivenConstraint

def parentSwitch(control, driven, drivers=[], type='parent', attrName='parentSwitch', enumName=[], addParentToDriven=False, defaultValue=0 , skip = False):
    loggerInterfaces.gLog('info', ('constraintFunctions.parentSwitch ' + control + ' ' + driven + ' ' + str(drivers) + ' ' + str(enumName)))
    constraint = ''
    #    Instantiate the Create Utility Node Class
    createNodeClass = nodeFunctions.CreateUtilityNode()

    #    name
    side = nameFunctions.getSide(driven)
    description = nameFunctions.getDescription(driven)

    objDrivers=[]
    for driver in drivers:
        driverName = nameFunctions.addDescriptionToName(nameFunctions.changeType(driver, 'grp'), nameFunctions.flatten(driven) + 'parentSwitchOffset')
        objDrivers.append(cmds.createNode('transform',n=driverName))
        cmds.parent(objDrivers[-1], driven, r=True)
        cmds.parent(objDrivers[-1], driver)
        attributeFunctions.lockAndHide(objDrivers[-1],['t','r', 's', 'v'])

    if addParentToDriven:
        driven = dagFunctions.addParent(driven)
        if nameFunctions.getType(driven) == 'ctl':
            driven = cmds.rename(driven, nameFunctions.changeType(driven, 'grp'))

    if type == 'parent' or type == 'orient':
        constraint = createNodeClass.createConstraint('%sConstraint' %(type), objDrivers, driven, ['maintainOffset=True'])

    elif type == 'parentSkipTranslate':
        constraint = createNodeClass.createConstraint('parentConstraint', objDrivers, driven, ['maintainOffset=True, st = ["x", "y", "z"]'])

    else:
        print 'Unknown constraint type. Skipping...'

    attributeFunctions.lockAndHide(driven,['t','r', 's', 'v'])

    enum = ''
    for i in range(len(drivers)):
            enum = enum.__add__(enumName[i]+':')

    cmds.addAttr(control, k=True, ln= attrName, at='enum', en=enum, dv=defaultValue)

    for i in range(len(objDrivers)):
        condition = createNodeClass.create('condition', side, '%sParentSwitch' %(description), i)

        cmds.connectAttr((control + '.' + attrName), (condition + '.firstTerm'))
        cmds.setAttr ((condition + '.colorIfTrueR'), 1)
        cmds.setAttr ((condition + '.colorIfFalseR'), 0)
        cmds.setAttr ((condition + '.secondTerm'), i)
        cmds.connectAttr((condition + '.outColorR'), (constraint[0] + '.' + str(objDrivers[i]) + 'W' + str(i)))

    cmds.setAttr(control + '.' + attrName, defaultValue)

    #    Clean up the Create Node Class.
    createNodeClass.lockAndHide()
    createNodeClass.setIsHistoricallyInteresting()

    #    Return the created constraint
    return constraint


def setMatrixAttr(matrix, attr):
        evalString = 'setAttr -type "matrix" "' + attr + '" '
        evalString += str(matrix(0, 0)) + ' '
        evalString += str(matrix(0, 1)) + ' '
        evalString += str(matrix(0, 2)) + ' '
        evalString += str(matrix(0, 3)) + ' '
        evalString += str(matrix(1, 0)) + ' '
        evalString += str(matrix(1, 1)) + ' '
        evalString += str(matrix(1, 2)) + ' '
        evalString += str(matrix(1, 3)) + ' '
        evalString += str(matrix(2, 0)) + ' '
        evalString += str(matrix(2, 1)) + ' '
        evalString += str(matrix(2, 2)) + ' '
        evalString += str(matrix(2, 3)) + ' '
        evalString += str(matrix(3, 0)) + ' '
        evalString += str(matrix(3, 1)) + ' '
        evalString += str(matrix(3, 2)) + ' '
        evalString += str(matrix(3, 3))

        mel.eval(evalString)

#========================================================================================
#FUNCTION:      parentSwitch2
#DESCRIPTION:   calculates the ini offset and applies an applyNspaceSwitch
#USAGE:         applyNspaceSwitch(drivers = ["char_L_driver_GRP"], driven = "char_L_driven_GRP")
#RETURN:        nada
#REQUIRES:      checkFunctions, OpenMaya, rigSpaceSwitch.so
#AUTHOR:        Catalin Niculescu
#DATE:          06.07.10
#Version        1.0.0
#========================================================================================
def parentSwitch2(control, driven, drivers=[], type='parent', attrName='parentSwitch',
                  enumName=[], addParentToDriven=False, defaultValue = 0 , skip = False,
                  skipRotate = False, skipTranslate = False, createOffsetNode = False, offsetNodeParent = None,
                  key = False, isSwitch = True):
    loggerInterfaces.gLog('info', ('constraintFunctions.parentSwitch ' + control + ' ' + driven + ' ' + str(drivers) + ' ' + str(enumName)))

    #check
    if not drivers:
        raise GeppettoError("No driver specified")
    if not driven:
        raise GeppettoError("No driven specified")
    checkFunctions.loadPlugin("rigSpaceSwitch")

    if offsetNodeParent:
        check.objExists(offsetNodeParent)

    for i in drivers:
        checkFunctions.objExists(i)
    checkFunctions.objExists(driven)

    offsetNode = None

    #create the node
    nd = nodeFunctions.CreateUtilityNode()
    description = nameFunctions.getDescription(driven)
    side = nameFunctions.getSide(driven)
    nss = nd.create("rigSpaceSwitch", side, description, "0", 1)
    cmds.setAttr(nss + ".spaceSwitch", defaultValue)

    for i in range(len(drivers)):
        description = nameFunctions.getDescription(drivers[i])
        #calculate the offset between driver and driven
        #get the MDagPaths
        driverTrans = apiFunctions.DependNode(drivers[i]).asMDagPath().inclusiveMatrixInverse()
        drivenTrans = apiFunctions.DependNode(driven).asMDagPath().inclusiveMatrix()

        offsetMM = drivenTrans * driverTrans
        offsetTM = OpenMaya.MTransformationMatrix(offsetMM)
        offsetMM = offsetTM.asMatrix()

        #get the position
        pos = offsetTM.getTranslation(OpenMaya.MSpace.kWorld)

        #get the rotation
        euler = offsetTM.eulerRotation()

        #create the offset node if needed
        if createOffsetNode:
            offsetNode = nd.create("transform", side, description + "Offset", "0", 1)

            #set its attrs
            cmds.setAttr(offsetNode + ".t", pos[0], pos[1], pos[2], type = "double3")
            cmds.setAttr(offsetNode + ".r", math.degrees(euler.x), math.degrees(euler.y), math.degrees(euler.z), type = "double3")

            #lnh
            attributeFunctions.lockAndHide(offsetNode, ["s", "v"])

            #key the offsetNode
            if key:
                cmds.setKeyframe(offsetNode)

            cmds.connectAttr(offsetNode + ".wm", nss + ".offsetMatrix[" + str(i) + "]")
        else:
            setMatrixAttr(offsetMM, nss + ".offsetMatrix[" + str(i) + "]")

        #connect the node
        cmds.connectAttr(drivers[i] + ".wm", nss + ".driverMatrix[" + str(i) + "]")

    if not type == "parentSkipTranslate":
        cmds.connectAttr(nss + ".outTranslate", driven + ".t")
    if not type == "parentSkipRotate":
        cmds.connectAttr(nss + ".outRotate", driven + ".r")

    cmds.connectAttr(driven + ".parentInverseMatrix", nss + ".parentInverseWorldMatrix")

    #add the switch attr and connect, if this is for a spaceSwitch setup
    if isSwitch:
        attr = attributeFunctions.addAttr(control, attrName, "enum", enumName)
        cmds.connectAttr(attr, nss + ".spaceSwitch")


    #clean up
    nd.setIsHistoricallyInteresting()
    nd.lockAndHide()

    return [nss, offsetNode]


#    please note that we can only blend when have 2 targets
def blendMultiConstraintByAttribute(sources, targets, object, attribute, type='orient', mo=False):
    #    Instantiate the Create Utility Node Class
    createNodeClass = nodeFunctions.CreateUtilityNode()

#    print 'constraintFunctions.blendMultiConstraintByAttribute ' + str(sources) + ' ' + str(targets) + ' ' + object + ' ' + attribute + ' ' + type
    constraints = multiConstraint(sources, targets, type, mo=mo)

    for i in range(len(constraints)):
        side = nameFunctions.getSide(constraints[i])
        description = nameFunctions.getDescription(constraints[i])

        reverse = createNodeClass.create('reverse', side, description, 0)

        connectFunctions.create((object + '.' + attribute), (constraints[i] + '.' + sources[0][i] + 'W0'))
        connectFunctions.create((object + '.' + attribute), (reverse + '.inputX'))
        connectFunctions.create((reverse + '.outputX'), (constraints[i] + '.' + sources[1][i] + 'W1'))

    #    Clean up the Node Class
    createNodeClass.lockAndHide()
    createNodeClass.setIsHistoricallyInteresting()

#    useage: when driving the base jointChain using the FK and IK jointChain.
#    multiConstraint([['a1', 'a2', 'a3'],['b1', 'b2', 'b3']], ['c1', 'c2', 'c3'])
def multiConstraint(sources, targets, type='orient', mo=False):
    constraints = []

    nSources = len(sources)
    nElements = len(sources[0])

    for i in range(nElements):
        s = []
        for j in range(nSources):
            s.append(sources[j][i])

        constraints.append(create(s,targets[i],type=type, mo=mo))

    return constraints

#    usage: create(sources=['c_grp_test_0'], target='c_grp_test_1')
def create(sources, target, type='orient', mo=True, lockTarget=True):
    #print '[create] ' + str(sources) + ' ' + str(target) + ' ' + type
    constraint = ''

    #    Instantiate the Create Utility Node Class
    createNodeClass = nodeFunctions.CreateUtilityNode()

    #    unlock attributes
    if cmds.nodeType(target) != 'ikHandle':
        attributeFunctions.lockAndHide(target, ['t', 'r', 's'], unlock=True)

    #    name
    constraintType = type + 'Constraint'

    if type != 'poleVector':
        constraint = createNodeClass.createConstraint('%sConstraint' %(type), sources, target, ['maintainOffset=%s' %(str(mo))])
    else:
        constraint = createNodeClass.createConstraint('%sConstraint' %(type), sources, target, None)

    #    Clean up the Node Class
    createNodeClass.lockAndHide()
    createNodeClass.setIsHistoricallyInteresting()

    if lockTarget:
        #    lock all attributes
        if cmds.nodeType(target) != 'ikHandle':
            attributeFunctions.lockAndHide(target, ['t', 'r', 's'])

    return constraint[0]

#===============================================================================
#    Matrix constraint type    ---
#===============================================================================
def constraintToTarget(target, objList, t=True, r=True, s=True, sh=True, mo=False, store=False, vbzLvl=2):
    '''
    Constraint list items to target (point, orient, scale and shear constraint) with matrices (much faster than normal constraints)

    FLAGS:
    -mo (bool): maintain offset in constraint
    -store (bool): store constraint info for 'automatic re-constraint' (see reconstraintAllToTarget() # To Do)
    -vbzLvl (int 0 to 4): defines the feedback verbose level
    '''
    #    sanity check
    if not cmds.objExists(target):
        if vbzLvl>0:
            sys.stderr.write('! %s.constraintToTarget() -> target %s not found, aborting.\n' % (__name__, unicode(target)))
        return

    if not type(objList) == list:
        objList =   [objList]

    #    parse objList
    constraintNodeList  =   list()
    for obj in objList:
        if not cmds.objExists(obj):
            if vbzLvl>1:
                sys.stdout.write('#* %s.constraintToTarget() -> %s not found, skipping.\n' % (__name__, unicode(obj)))
            continue

        #    get current lock state
        lockState   =   cmds.getAttr('%s.tx' %obj, l=True)

        #    unlock
        if lockState:
            attributeFunctions.unlockTRSV(obj)

        #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
        #    check/delete current matrix constraint connections
        inConnections   =   list()
        if t:
            connections =   cmds.listConnections('%s.t' %obj, s=True, d=False)
            if connections:
                inConnections.append(connections[0])
        if r:
            connections =   cmds.listConnections('%s.r' %obj, s=True, d=False)
            if connections and not (connections[0] in inConnections):
                inConnections.append(connections[0])
        if s:
            connections =   cmds.listConnections('%s.s' %obj, s=True, d=False)
            if connections and not (connections[0] in inConnections):
                inConnections.append(connections[0])
        if sh:
            connections =   cmds.listConnections('%s.shear' %obj, s=True, d=False)
            if connections and not (connections[0] in inConnections):
                inConnections.append(connections[0])

        #    check for non matrix constraint connections
        for connection in inConnections:
            #    skip matrix constraints connections
            if cmds.nodeType(connection) == 'decomposeMatrix':
                continue

            #    abort on non matrix constraint
            if vbzLvl>1:
                sys.stdout.write('#* %s.constraintToTarget() -> %s has non decomposeMatrixtype connection, skipping\n' % (__name__, obj))
            continue

        #    delete matrix constraint connections
        if inConnections:
            if vbzLvl>3:
                sys.stdout.write('#   %s.constraintToTarget() -> %s is already connected, removing connection\n' % (__name__, obj))
            cmds.delete(inConnections)

        #    define baseName
        baseName    =   obj.split('|')[-1].split(':')[-1]
        try:
            baseName    =   nameFunctions.addDescriptionToName(baseName, 'Cst')
            baseName    =   nameFunctions.findUniqueName(baseName)
        except:
            baseName    =   'C_grp_%sCst_0'%baseName

        #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
        #    maintain offset case:

        #    get the inverse matrix of the offset and store on fourByFourMatrix
        offsetFbfMatrix =   None
        indexOffset     =   0
        offsetInvMatrix =   None
        if mo:
            #    get target world matrix
            tgtWorldMatrixList  =   cmds.getAttr('%s.worldMatrix[0]'%target)
            tgtWorldMatrix      =   OpenMaya.MMatrix()
            OpenMaya.MScriptUtil().createMatrixFromList( tgtWorldMatrixList, tgtWorldMatrix )

            #    get object world inverse matrix
            objParentInvMatrixList  =   cmds.getAttr('%s.worldInverseMatrix[0]'%obj)
            objParentInvMatrix  =   OpenMaya.MMatrix()
            OpenMaya.MScriptUtil().createMatrixFromList( objParentInvMatrixList, objParentInvMatrix )

            #    get offset inverse matrix
            offsetMatrix    =   tgtWorldMatrix*objParentInvMatrix
            offsetInvMatrix =   offsetMatrix.inverse()

            #    create matrix offset holder
            offsetFbfMatrix =   nameFunctions.changeType(baseName, 'fbfm')
            offsetFbfMatrix =   nameFunctions.addDescriptionToName(offsetFbfMatrix, 'Offset')
            offsetFbfMatrix =   cmds.createNode('fourByFourMatrix', n=offsetFbfMatrix)
            for row in range(4):
                for column in range(4):
                    cmds.setAttr('%s.in%d%d'%(offsetFbfMatrix, row, column), offsetInvMatrix(row, column), l=True)

            #    update connection index offset
            indexOffset =   1

        #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
        #    matrix constraint

        #    create multMatrix node
        multMx =   nameFunctions.changeType(baseName, 'mm')
        multMx  =   cmds.createNode('multMatrix', n=multMx)
        if mo:
            cmds.connectAttr('%s.output' %offsetFbfMatrix, '%s.matrixIn[0]'%multMx)
        cmds.connectAttr('%s.worldMatrix[0]' %target, '%s.matrixIn[%d]'%(multMx, indexOffset))
        cmds.connectAttr('%s.parentInverseMatrix[0]' %obj, '%s.matrixIn[%d]'%(multMx, indexOffset+1))

        #    create decompose matrix
        decompMatrix  =   nameFunctions.changeType(baseName, 'dmx')
        decompMatrix  =   cmds.createNode('decomposeMatrix', n=decompMatrix)
        cmds.connectAttr('%s.matrixSum' %multMx, '%s.inputMatrix' %decompMatrix)


        #    reset joint orients
        if cmds.nodeType(obj) == 'joint':
            cmds.setAttr('%s.jo'%obj, 0,0,0)

        #    connect
        if t:
            cmds.connectAttr('%s.outputTranslate'%decompMatrix, '%s.t'%obj)
        if r:
            cmds.connectAttr('%s.outputRotate'%decompMatrix, '%s.r'%obj)
        if s:
            cmds.connectAttr('%s.outputScale'%decompMatrix, '%s.s'%obj)
        if sh:
            cmds.connectAttr('%s.outputShear'%decompMatrix, '%s.shear'%obj)

        #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
        #    relock
        if lockState:
            attributeFunctions.lockAndHideTransforms(obj)

        #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
        #    update return list
        constraintNodeList.extend([decompMatrix, multMx])
        if mo:
            constraintNodeList.append(offsetFbfMatrix)

        #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
        #    store constraint infos for automatic re-constraint
        if not store:
            continue

        #    transform connection infos
        cstInfoAttrList =   list()
        if (t and r and s and sh):
            cstInfoAttrList.append('cstTgtSrc')
        else:
            if t:
                cstInfoAttrList.append('cstTgtSrcTr')
            if r:
                cstInfoAttrList.append('cstTgtSrcRo')
            if s:
                cstInfoAttrList.append('cstTgtSrcSc')
            if sh:
                cstInfoAttrList.append('cstTgtSrcSh')

        #    add infos
        for attr in cstInfoAttrList:
            #    add missing attr
            if not cmds.attributeQuery(attr, n=obj, ex=True):
                cmds.addAttr(obj, ln=attr, dt='string')
            cmds.setAttr('%s.%s' %(obj, attr), l=False)
            cmds.setAttr('%s.%s' %(obj, attr), target, type='string', l=True)

        #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
        #    store mo infos
        if not mo:
            continue

        moAttr    =   'cstTgtSrcMo'
        if not cmds.attributeQuery(moAttr, n=obj, ex=True):
            cmds.addAttr(obj, ln=moAttr, at='matrix')

        cmds.setAttr('%s.%s'%(obj, moAttr), l=False)
        setMatrixAttr(offsetInvMatrix, '%s.%s'%(obj, moAttr))
        cmds.setAttr('%s.%s'%(obj, moAttr), l=True)

    return constraintNodeList


