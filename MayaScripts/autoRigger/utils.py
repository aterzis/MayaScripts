'''
(c) Arthur Terzis 2011

A collection of utility Functions for rigging

'''
from maya import cmds
from maya import OpenMaya
from maya import OpenMayaAnim as OMA

def split_joint(joint, div=2, upAxis="tx"):
    '''
    A function to split a joint into segments
    joint is the start joint
    div = the number of divisions you want to split the joint into 
    
    returns the new joint chain in a list
    '''
    
    if cmds.objExists(joint):
        start_joint = joint
        end_joint = cmds.listRelatives(joint, typ="joint")[0]
    else:
        print "invalid joint argument"
        return 
    
    max_length = cmds.getAttr("%s.%s" %(end_joint,upAxis))
    jnt_length = max_length / div
    new_jnts = list()
    new_jnts.append(start_joint)
    
    # duplicate the start joint, and parent it under the heirarchy
    for i in range(div-1):
        jnt = cmds.duplicate(start_joint, po=True)
        cmds.parent(jnt, new_jnts[i])
        cmds.setAttr("%s.%s" %(jnt[0],upAxis), jnt_length)
        new_jnts.extend(jnt)
    
    cmds.parent(end_joint, new_jnts[-1])    
    cmds.setAttr("%s.%s" %(end_joint,upAxis), jnt_length)
    new_jnts.append(end_joint)
    
    return new_jnts


def visibility(nodes, vis=False):
    '''
    simple hide vis function - turns off by default
    '''
    if not isinstance(nodes, list):
        nodes = [nodes]
        
    for node in nodes:  
        cmds.setAttr("%s.visibility" %node, vis)


def lock_hide(nodes, t=True, r=True, s=True, v=True, other=False):
    '''
    lock and hide function 
    '''
    
    trans= ['tx', 'ty', 'tz']
    rot  = ['rx', 'ry', 'rz']
    scale= ['sx', 'sy', 'sz']
    
    if not isinstance(nodes, list):
        nodes = [nodes]
        
    for node in nodes:    
        if t:
            for attr in trans:
                cmds.setAttr("%s.%s" %(node, attr), l=True, k=False, cb=False)
        if r:
            for attr in rot:
                cmds.setAttr("%s.%s" %(node, attr), l=True, k=False, cb=False)
        if s:
            for attr in scale:
                cmds.setAttr("%s.%s" %(node, attr), l=True, k=False, cb=False)
                
        if v:
            cmds.setAttr("%s.v" %node, l=True, k=False, cb=False)
            
        if other:
            for attr in other:
                cmds.setAttr("%s.%s" %(node, attr), l=True, k=False, cb=False)
                
def find_unique_name(name):
    pass

def create_rivet(surface, follow):
    '''
    rivet an object to a surface using a follicle
    surface is the target object 
    follow is the object being riveted to the surface
    '''
    #get the closest UVS
    surface_shape = cmds.listRelatives(surface, s=True)[0]
    point = cmds.xform(follow, q=True, ws=True, t=True)
    U, V = find_closest_UV(surface_shape, point)
    
    # create follicle
    follicle_shape = cmds.createNode('follicle')
    follicle = cmds.listRelatives(follicle_shape, p=True)[0]
    cmds.setAttr('%s.inheritsTransform'%follicle, 0)
    cmds.connectAttr('%s.outRotate'%follicle_shape, '%s.rotate'%follicle, f=True)
    cmds.connectAttr('%s.outTranslate'%follicle_shape, '%s.translate'%follicle, f=True)
    cmds.setAttr('%s.pu'%follicle_shape, U)
    cmds.setAttr('%s.pv'%follicle_shape, V)

    #    connect surface to follicle
    cmds.connectAttr('%s.worldMatrix[0]'%surface_shape, '%s.inputWorldMatrix'%follicle_shape, f=True)
    cmds.connectAttr('%s.worldMesh[0]'%surface_shape, '%s.inputMesh'%follicle_shape, f=True)

    # Connect the follicle output to the follow object
    cmds.connectAttr('%s.rotate'%follicle, '%s.rotate'%follow, f=True)
    cmds.connectAttr('%s.translate'%follicle, '%s.translate'%follow, f=True)
    cmds.rename(follicle, "%s_follicle" %follow)

    return follicle
    
    
def find_closest_UV(shape, point=False, obj=False):
    '''
    get closest UV's from the point to the surface using maya API
    point is a list of [x,y,z] world space position
    shape is the name of the shape node
    can pass in an object instead of a point. 
    '''
    sel = OpenMaya.MSelectionList()
    OpenMaya.MGlobal.getSelectionListByName(shape, sel)
    dPath = OpenMaya.MDagPath()
    sel.getDagPath(0, dPath)
    mesh = OpenMaya.MFnMesh(dPath)
    
    if point:
        pos = point
    elif obj:
        pos = cmds.xform(obj, q=True, ws=True, t=True)
    mPoint = OpenMaya.MPoint(pos[0], pos[1], pos[2])
    
    # find and use default set list
    setList = list()
    mesh.getUVSetNames(setList)
    uvSet = setList[0]
    
    pArray = [0, 0]
    floatPtr = OpenMaya.MScriptUtil()
    floatPtr.createFromList(pArray, 2)
    uvPoint = floatPtr.asFloat2Ptr()
    
    # query the UV
    mesh.getUVAtPoint(mPoint, uvPoint, OpenMaya.MSpace.kWorld , uvSet)
    U = OpenMaya.MScriptUtil.getFloat2ArrayItem(uvPoint, 0, 0)
    V = OpenMaya.MScriptUtil.getFloat2ArrayItem(uvPoint, 0, 1)
    
    
    return U, V
    
    
def skinAs(source=None, target=None, sel=True):
    '''
    copies across the skin cluster and weights from a source mesh to a target mesh
    can work on selection - ensure that source is selected first, followed by target mesh
    '''
    if sel:
        source, target = cmds.ls(sl=True, l=True)
    elif not cmds.objExists(source) and not cmds.objExists(target):
        print "No valid geometry selected - try again"
        return False

    source_shp = cmds.listRelatives(source, s=True, ni=True)
    target_shp = cmds.listRelatives(target, s=True, ni=True)
    
    # find the skin cluster on the mesh
    his = cmds.listHistory(source_shp, pdo=True)
    skin = False
    for node in his:
        if cmds.nodeType(node) == "skinCluster":
            skin = node
            
#    skin = cmds.listConnections(source_shp, type="skinCluster" )
    if skin:
        joints = cmds.skinCluster(skin, q=True, inf=True)
    else:
        print "source mesh does not have a skinCluster to copy"
        return False
    
    if joints and source_shp and target_shp:
        new_skin = cmds.skinCluster(joints, target, tsb=True, sm=1, nw=1)
        source_UV = cmds.polyUVSet(source, q=True, auv=True)
        target_UV= cmds.polyUVSet(target, q=True, auv=True)
        if source_UV == target_UV:
            # if UV sets match, copy across using the UV maps - get a better result for transfer from low to high res meshes
            cmds.copySkinWeights(ss=skin, ds=new_skin[0], sa="closestPoint", nm=True, nr=True, uv=[source_UV[0], target_UV[0]])
        else:
            # else do a standard weight copy
            cmds.copySkinWeights(ss=skin, ds=new_skin[0], sa="closestPoint", nr=True, nm=True)
        print "skin weights copied from %s to %s" %(source, target)
        return True
    else:
        print "copying skin weights failed - check your source and target mesh selections"
        return False    
   
    
def mirror_settings(orig="L_eyeSettings", copy="R_eyeSettings"):
    '''
    used to copy over the attributes from orig to copy on a rig attribute node
    
    should make this more generic - and use the listAttr command
    '''
    attrs = ["eyeRangeUp", "eyeRangeDown", "eyeRangeLeft", "eyeRangeRight", "upperLidBlinkMax", "lowerLidBlinkMax", "upperLidOpen",
             "upperLidClosed", "lowerLidOpen", "lowerLidClosed", "upperLidFollowMult", "lowerLidFollowMult", "hoizontalFollowMult"]
    
    for attr in attrs:
        val = cmds.getAttr("%s.%s" %(orig, attr))
        cmds.setAttr("%s.%s" %(copy, attr), val)

        
def label_joint(joint, side="C", typ="Other", label=False):
    '''
    Side = C, L or R or N(one)
    typ = predefined maya type or other
    label = Label string i.e. uLid
    '''
    
    side_id = {"C":0,
               "L":1,
               "R":2,
               "N":3}
    
    #note - only using these in the face builder - should expand this to have the whole set
    type_id = {"Other":18,
               "Root":1,
               "Head":8}
    
    if not cmds.objExists(joint):
        print "joint %s does not exist, skipping labeling" %joint
        return False
    
    if side in side_id.keys():
        cmds.setAttr("%s.side" %joint, side_id[side])
    else:
        print "Invalid side argument passed in, joint labeling incomplete for %s" %joint
    
    if typ in type_id.keys():
        cmds.setAttr("%s.type" %joint, type_id[typ])
    else:
        print "Invalid type argument passed in, joint labeling incomplete for %s" %joint
    
    if label and typ =="Other":
        cmds.setAttr("%s.otherType" %joint, label, type="string")
        

def anim_cam(panels="C_jaw_controls", cam_type="face"):
    '''
    create a camera that is focused on a set of controls (usually face) for use in animation
    panels = the object you want the camera to focus on
    '''
    anim_cam = cmds.camera(n="%s_ctls_cam" %cam_type)[0]
    tmp = cmds.parentConstraint(panels, anim_cam, mo=False)
    cmds.delete(tmp)
    cmds.setAttr("%s.tz" %anim_cam, 20)
    cmds.setAttr("%s.v" %anim_cam, 0)
    
    cmds.parent(anim_cam, panels)
    
    
def curve_from_edge(): 
    '''
    creates a curve from the selected edges
    Need to select the edges individually in the order that makes up the curve for attach curve to work
    it's crude, but it does what I need it to do 
    
    This is dodgy and doesn't always work....need to re-write
    '''
    edges = cmds.ls(sl=True)
    curves = list()
    
    for edge in edges:
        crv = cmds.duplicateCurve(edge)
        curves.append(crv[0])
        
    new_curve = cmds.attachCurve(curves, ch=1, rpo=0, kmk=1, m=1, bb=0.5, bki=0, p=0.1)
    cmds.delete(curves)
    cmds.rebuildCurve(new_curve[0], ch=1 ,rpo= 1 ,rt= 0 ,end= 1 ,kr= 0 ,kcp= 1 ,kep= 1 ,kt= 0 ,s= 4 ,d= 3 ,tol= 0.01)
    
    return new_curve


def invert_blendWeights(flood=False):
    '''
    to help split up a shape between left and right, by inverting the blendshape weights
    select the geo (shape node) you want to run this on
    
    flood flag set to true to reset all the blendWeights to 1
    doesn't always work....need to re-write
    '''
    sel = cmds.ls(sl=True, type='shape')
    if not sel:
        print "You need to select a shape" 
        return False
    
    # find the blendshape connected to this node
    blend = False
    nodes = cmds.listHistory(sel[0], pdo=True)
    for node in nodes:
        if cmds.nodeType(node) == "blendShape":
            blend = node
    
    if not blend:
        print "No blendshape node found connected to %s" %sel[0]
        return False
    
    MSel = OpenMaya.MSelectionList()
    OpenMaya.MGlobal.getSelectionListByName(sel[0], MSel)
    dPath = OpenMaya.MDagPath()
    MSel.getDagPath(0, dPath)
    mesh = OpenMaya.MFnMesh(dPath)
    
    verts = mesh.numVertices()
    shapes = cmds.blendShape(blend, q=True, wc=True)
    
    for shape in range(shapes):
        for vert in range(verts):
            if flood:
                val = 1
            else:
                val = cmds.getAttr("%s.inputTarget[0].inputTargetGroup[%s].targetWeights[%s]" %(blend, shape, vert))
                val = 1-val
            
            cmds.setAttr("%s.inputTarget[0].inputTargetGroup[%s].targetWeights[%s]" %(blend, shape, vert), val)
    
    if flood:
        print "Blend weight maps reset back to 1"
    else:
        print "Blend weight maps inverted"
        
