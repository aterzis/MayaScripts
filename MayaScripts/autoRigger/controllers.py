'''
(c) Arthur Terzis 2011

This is my implementation of a controller setup for my auto-rigger. The modules will create objects of
this class for each control instance.

Each controller class is derived from the BaseControl Class
The only method that gets overriden in the child classes is the _define_shape method
which defines the shape of the control at origin.

The same methods can be run on each child control, since all the methods are in the base class

'''


from maya import cmds
from maya import OpenMaya



class BaseControl(object):
    '''
        All control classes will inherit from this base class
    '''
    def __init__(self, name="C_ctl_curve_0", colour=False, joint=False):

        self.name = name
        self.__colours = {'black':1, 'dark_grey':2, 'grey':3, 'magenta':4, 'dark_blue':5,
                        'blue':6, 'dark_green':7, 'dark_purple':8, 'purple':9, 'brown':10,
                        'dark_brown':11, 'dark_red':12, 'red':13, 'green':14, 'medium_blue':15,
                        'white':16, 'yellow':17, 'light_blue':18, 'light_green':19, 'pink':20,
                        'light_brown':21, 'light_yellow':22, 'medium_green':23, 'default':0}

        self._cvs = []
        self._closed = False
        self._deg = 1
        self._knots = []
        self._colour = colour
        
        # used to create a special setup with a joint and group under the control for skinning
        self._joint = joint


    def _define_shape(self):
        '''
            virtual method for inheritance
        '''
        return True


    def rename(self, name):
        if not cmds.objExists(name):
            try:
                self.name  = cmds.rename(self.name, name, ignoreShape=False)
                self.shape = cmds.rename(self.shape, name + "Shape")
            except:
                print "rename failed, skipping"
        else:
            print "Name already taken, can not rename control object"


    def create(self):
        self.name = cmds.curve(per=self._closed,
                                    d=self._deg,
                                    k=self._knots,
                                    p=self._cvs,
                                    n=self.name)

        self.shape = cmds.listRelatives(self.name, s=True)[0]
        # curve command was not naming the shape node properly
        self.shape = cmds.rename(self.shape, self.name + "Shape")
        
        if self._colour:
            self.set_colour(self._colour)
            
        if self._joint:
            self._add_joint()

    
    def _add_joint(self):
        '''
        adds a joint under the curve, and then creates an offset
        '''
        pos = cmds.xform(self.name, q=True, ws=True, t=True)

        cmds.select(cl=True)
        self.skin_jnt = cmds.joint(n="%s_skn_jnt" %self.name, p=pos)
        cmds.setAttr("%s.v" %self.skin_jnt, 0)
        
        cmds.parent(self.skin_jnt, self.name)
        
        # and then group everything - access offset via self.group 
        self.add_offset()
        

    def set_position(self, trans=False, rot=False, sc=False, obj=None):
        if obj:
            trans = cmds.xform(obj, q=True, ws=True, t=True)
#             rot = cmds.xform(obj, q=True, ws=True, ro=True)
        if trans:
            cmds.xform(self.name, ws=True, t=trans)
        if rot:
            cmds.xform(self.name, ws=True, ro=rot)
        if sc:
            cmds.xform(self.name, ws=True, s=sc)
        # freeze transforms to zero out the control
        cmds.makeIdentity(self.name, apply=True, t=True, r=True, s=True)
        
    def set_offset_position(self, trans=False, rot=False, sc=False, obj=None):
        if obj:
            trans = cmds.xform(obj, q=True, ws=True, t=True)
        if trans:
            cmds.xform(self.group, ws=True, t=trans)
        if rot:
            cmds.xform(self.group, ws=True, ro=rot)
        if sc:
            cmds.xform(self.group, ws=True, s=sc)
        # freeze transforms to zero out the control
#         cmds.makeIdentity(self.group, apply=True, t=True, r=True, s=True)
        
        
    def set_pivot(self, trans=False, obj=None):
        if obj:
            trans = cmds.xform(obj, q=True, ws=True, t=True)
        if trans:
            cmds.xform(self.name, ws=True, rp=trans, sp=trans)


    def set_rotate_order(self, order='xyz'):
        order_table = {'xyz':0,
                       'yzx':1,
                       'zxy':2,
                       'xzy':3,
                       'yxz':4,
                       'zyx':5}
        
        if order in order_table.keys():
            cmds.setAttr('%s.rotateOrder' %self.name, order_table[order])
        else:
            print "NOT a valid rotation order"


    def add_offset(self, level=0):
        cmds.select(clear=True)
        self.group = cmds.group(n=self.name.replace('ctl', 'grp'), empty=True)
        
        # make sure group has same pivot as control
        pivot = cmds.xform(self.name, q=True, ws=True, t=True)
        cmds.xform(self.group, ws=True, rp=pivot, sp=pivot)
        
        cmds.parent(self.name, self.group)


    def set_colour(self, colour = 'red'):
        if colour in self.__colours.keys():
            index = self.__colours[colour]
            cmds.setAttr('%s.overrideEnabled' %self.shape, 1)
            cmds.setAttr('%s.overrideColor' %self.shape, index)
        else:
            print "NOT a valid colour option"
            return False

    def set_limits(self, trans=False, rot=False, scale=False):
        '''
        limit argument is a list of tuples for xyz
        [(xmin, xmax), (ymin, ymax), (zmin, zmax)]
        '''
        if trans:
            cmds.transformLimits(self.name, etx=[True, True], tx=trans[0],
                                 ety=[True, True], ty=trans[1],
                                 etz=[True, True], tz=trans[2])


    def lock_hide(self, attr, offset=False):
        if offset:
            cmds.setAttr("%s.%s" %(self.group, attr), l=True, k=False, cb=False)
        else:
            cmds.setAttr("%s.%s" %(self.name, attr), l=True, k=False, cb=False)


    def hide_rotation(self, rot=['rx', 'ry', 'rz'], offset=False):
        for attr in rot:
            self.lock_hide(attr, offset)


    def hide_translation(self, trans=['tx', 'ty', 'tz'], offset=False):
        for attr in trans:
            self.lock_hide(attr, offset)


    def hide_scale(self, scale=['sx', 'sy', 'sz'], offset=False):
        for attr in scale:
            self.lock_hide(attr, offset)


    def hide_transforms(self, v=True):
        self.hide_rotation()
        self.hide_scale()
        self.hide_translation()
        if v:
            self.lock_hide("v")


#####################################
#  General Controls
#####################################

class ArcControl(BaseControl):

    def __init__(self, name="C_ctl_arc_0", colour=False, joint=False):
        BaseControl.__init__(self, name, colour, joint)
        self._define_shape()
        self.create()


    def _define_shape(self):
        '''
            half circle
        '''
        self._cvs =  [( -0.0, 0.0, -1.0 ),
                      ( -0.2612, 0.0, -1.0 ),
                      ( -0.7836, 0.0, -0.7836 ),
                      ( -1.1082, 0.0, -0.0 ),
                      (-0.7836, -0.0, 0.7836 ),
                      ( -0.2612, -0.0, 1.0 ),
                      ( -0.0, -0.0, 1.0 )    ]

        self._deg = 3
        self._knots = [0.0 , 0.0 , 0.0 , 1.0 , 2.0 , 3.0 , 4.0 , 4.0 , 4.0]


class ArrowControl(BaseControl):

    def __init__(self, name="C_ctl_arrow_0", colour=False, joint=False):
        BaseControl.__init__(self, name, colour, joint)
        self._define_shape()
        self.create()

    def _define_shape(self):
        '''
            single pointed arrow
        '''
        self._cvs =[(1.0,0.0,0.0),
                    (1.0,0.0,-2.0),
                    (2.0,0.0,-2.0),
                    (0.0,0.0,-4.0),
                    (-2.0,0.0,-2.0),
                    (-1.0,0.0,-2.0),
                    (-1.0,0.0,0.0),
                    (1.0,0.0,0.0)]

        self._knots = [0.0, 1.0, 2.0, 3.0, 4.0, 5.0, 6.0, 7.0]


class Arrow4Control(BaseControl):

    def __init__(self, name="C_ctl_arrow_0", colour=False, joint=False):
        BaseControl.__init__(self, name, colour, joint)
        self._define_shape()
        self.create()

    def _define_shape(self):
        '''
            flat, 4 sided arrow
        '''
        self._cvs = [(1.0,0.0,-1.0),
                    (1.0,0.0,-3.0),
                    (2.0,0.0,-3.0),
                    (0.0,0.0,-5.0),
                    (-2.0,0.0,-3.0),
                    (-1.0,0.0,-3.0),
                    (-1.0,0.0,-1.0),
                    (-3.0,0.0,-1.0),
                    (-3.0,0.0,-2.0),
                    (-5.0,0.0,0.0),
                    (-3.0,0.0,2.0),
                    (-3.0,0.0,1.0),
                    (-1.0,0.0,1.0),
                    (-1.0,0.0,3.0),
                    (-2.0,0.0,3.0),
                    (0.0,0.0,5.0),
                    (2.0,0.0,3.0),
                    (1.0,0.0,3.0),
                    (1.0,0.0,1.0),
                    (3.0,0.0,1.0),
                    (3.0,0.0,2.0),
                    (5.0,0.0,0.0),
                    (3.0,0.0,-2.0),
                    (3.0,0.0,-1.0),
                    (1.0,0.0,-1.0),]

        self._knots =[0.0, 1.0, 2.0, 3.0, 4.0, 5.0, 6.0, 7.0, 8.0, 9.0, 10.0, 11.0,
                      12.0, 13.0, 14.0, 15.0, 16.0, 17.0, 18.0, 19.0, 20.0, 21.0, 22.0, 23.0, 24.0]


class BoxControl(BaseControl):

    def __init__(self, name="C_ctl_box_0", colour=False, joint=False):
        BaseControl.__init__(self, name, colour, joint)
        self._define_shape()
        self.create()


    def _define_shape(self):
        '''
            Box at origin
        '''
        self._cvs = [(0.5, -0.5, 0.5) ,
                     (0.5, 0.5, 0.5) ,
                     (-0.5, 0.5, 0.5) ,
                     (-0.5, 0.5, -0.5) ,
                     (-0.5, -0.5, -0.5) ,
                     (0.5, -0.5, -0.5) ,
                     (0.5, -0.5, 0.5) ,
                     (-0.5, -0.5, 0.5) ,
                     (-0.5, 0.5, 0.5) ,
                     (0.5, 0.5, 0.5) ,
                     (0.5, 0.5, -0.5) ,
                     (0.5, -0.5, -0.5) ,
                     (-0.5, -0.5, -0.5) ,
                     (-0.5, -0.5, 0.5) ,
                     (-0.5, 0.5, 0.5) ,
                     (-0.5, 0.5, -0.5) ,
                     (0.5, 0.5, -0.5) ]

        self._knots = [0.0 , 4.0 , 7.0 , 10.0 , 13.0 , 16.0 , 19.0 , 22.0 , 25.0,
                       28.0 ,31.0 , 34.0 , 37.0 , 40.0 , 43.0 , 46.0 , 49.0]
        
        
class CircleControl(BaseControl):

    def __init__(self, name="C_ctl_circle_0", colour=False, joint=False):
        BaseControl.__init__(self, name, colour, joint)
        self._define_shape()
        self.create()


    def _define_shape(self):
        '''
            Flat horizontal circle
        '''
        self._cvs = [( 0.5196, 0.0, -0.3 ),
                      ( -0.0, 0.0, -0.6 ),
                      ( -0.5196, 0.0, -0.3 ),
                      ( -0.5196, -0.0, 0.3 ),
                      ( -0.0, -0.0, 0.6 ),
                      ( 0.5196, -0.0, 0.3 ),
                      ( 0.5196, 0.0, -0.3 ),
                      ( -0.0, 0.0, -0.6 ),
                      ( -0.5196, 0.0, -0.3 )]

        self._deg = 3
        self._closed = True
        self._knots = [-2.0 ,-1.0 ,0.0 ,1.0 ,2.0 ,3.0 ,4.0 ,5.0 ,6.0 ,7.0 ,8.0]


class CurveArrowControl(BaseControl):

    def __init__(self, name="C_ctl_arrow_0", colour=False, joint=False):
        BaseControl.__init__(self, name, colour, joint)
        self._define_shape()
        self.create()

    def _define_shape(self):
        '''
            single pointed arrow
        '''
        self._cvs =[( 0.0655, -0.0, -0.5762 ),
                    ( 0.5128, -0.0, -0.5445 ),
                    ( 0.2938, -0.0, -0.4962 ),
                    ( 0.4193, -0.0, -0.4193 ),
                    ( 0.5479, -0.0, -0.227 ),
                    ( 0.5931, -0.0, 0.0 ),
                    ( 0.5479, -0.0, 0.227 ),
                    ( 0.4193, -0.0, 0.4193 ),
                    ( 0.2947, -0.0, 0.4972 ),
                    ( 0.5128, -0.0, 0.5445 ),
                    ( 0.0655, -0.0, 0.5762 ),
                    ( 0.2825, -0.0, 0.1838 ),
                    ( 0.2316, -0.0, 0.4144 ),
                    ( 0.343, -0.0, 0.3431 ),
                    ( 0.4483, -0.0, 0.1857 ),
                    ( 0.4852, -0.0, 0.0 ),
                    ( 0.4483, -0.0, -0.1857 ),
                    ( 0.343, -0.0, -0.3431 ),
                    ( 0.2308, -0.0, -0.4128 ),
                    ( 0.2825, -0.0, -0.1838 ),
                    ( 0.0655, -0.0, -0.5762 )]

        self._knots = [0.0 , 1.0 , 2.0 , 3.0 , 4.0 , 5.0 , 6.0 , 7.0 , 8.0 , 9.0 ,
                       10.0 , 11.0 , 12.0 , 13.0 , 14.0 , 15.0 , 16.0 , 17.0 ,
                       18.0 , 19.0 ,20.0]


class DiamondControl(BaseControl):

    def __init__(self, name="C_ctl_diamond_0", colour=False, joint=False):
        BaseControl.__init__(self, name, colour, joint)
        self._define_shape()
        self.create()

    def _define_shape(self):
        '''
           diamond controller shape
        '''
        self._cvs = [( 0.4973, 0.0, 0.0 ),
                     ( -0.0001, 0.0, -0.4971 ),
                     ( -0.0001, 0.4985, 0.0001 ),
                     ( -0.4985, 0.0, -0.0001 ),
                     ( -0.0001, 0.0, -0.4971 ),
                     ( 0.0, -0.4973, 0.0 ),
                     ( -0.4985, 0.0, -0.0001 ),
                     ( -0.0, 0.0, 0.4973 ),
                     ( -0.0001, 0.4985, 0.0001 ),
                     ( 0.4973, 0.0, 0.0 ),
                     ( -0.0, 0.0, 0.4973 ),
                     ( 0.0, -0.4973, 0.0 ),
                     ( 0.4973, 0.0, 0.0 )]

        self._knots =[0.0 , 1.0 , 2.0 , 3.0 , 4.0 , 5.0 , 6.0 , 7.0 , 8.0 , 9.0 ,
                      10.0 , 11.0 , 12.0]


class LocatorControl(BaseControl):

    def __init__(self, name="C_ctl_locator_0", colour=False, joint=False):
        BaseControl.__init__(self, name, colour, joint)
        self._define_shape()
        self.create()


    def _define_shape(self):
        '''
            Box at origin
        '''
        self._cvs = [( 0.0, -0.5, 0.0 ),
                     ( 0.0, 0.5, 0.0 ),
                     ( 0.0, 0.0, 0.0 ),
                     ( 0.0, 0.0, -0.5 ),
                     ( 0.0, 0.0, 0.5 ),
                     ( 0.0, 0.0, 0.0 ),
                     ( -0.5, 0.0, 0.0 ),
                     ( 0.5, 0.0, 0.0 )]

        self._knots = [ 0.0 , 1.0 , 2.0 , 3.0 , 4.0 , 5.0 , 6.0 , 7.0]


class PyramidControl(BaseControl):

    def __init__(self, name="C_ctl_pyramid_0", colour=False, joint=False):
        BaseControl.__init__(self, name, colour, joint)
        self._define_shape()
        self.create()

    def _define_shape(self):
        '''
            Pyramid controller shape
        '''
        self._cvs = [(-0.5,3.8295984268188477e-05,0.49999994039535522),
                    (0.49999994039535522,3.8295984268188477e-05,0.5),
                    (0.49999997019767761,3.8295984268188477e-05,-0.49999997019767761),
                    (-0.49999991059303284,3.8295984268188477e-05,-0.50000005960464478),
                    (0.0,0.83079832792282104,0.0),
                    (0.49999994039535522,3.8295984268188477e-05,0.5),
                    (0.49999997019767761,3.8295984268188477e-05,-0.49999997019767761),
                    (0.0,0.83079832792282104,0.0),
                    (-0.5,3.8295984268188477e-05,0.49999994039535522),
                    (-0.49999991059303284,3.8295984268188477e-05,-0.50000005960464478)]

        self._knots =[0.0, 1.0, 2.0, 3.0, 4.0, 5.0, 6.0, 7.0, 8.0, 9.0]


class ToothControl(BaseControl):
    '''
    because it looks like a sharp tooth, not because it is used for teeth
    '''

    def __init__(self, name="C_ctl_pyramid_0", colour=False, joint=False):
        BaseControl.__init__(self, name, colour, joint)
        self._define_shape()
        self.create()

    def _define_shape(self):
        '''
            tooth controller shape
        '''
        self._cvs = [(1.9147992134094238e-05,0.099999999999999992,0.24999997019767761),
                    (1.9147992134094238e-05,-0.099999988079071053,0.25),
                    (1.9147992134094238e-05,-0.099999994039535522,-0.24999998509883881),
                    (1.9147992134094238e-05,0.09999998211860657,-0.25000002980232239),
                    (0.41539916396141058,1.1102230246251565e-16,0.0),
                    (1.9147992134094238e-05,-0.099999988079071053,0.25),
                    (1.9147992134094238e-05,-0.099999994039535522,-0.24999998509883881),
                    (0.41539916396141058,1.1102230246251565e-16,0.0),
                    (1.9147992134094238e-05,0.099999999999999992,0.24999997019767761),
                    (1.9147992134094238e-05,0.09999998211860657,-0.25000002980232239),]
        
        self._knots = [0.0, 1.0, 2.0, 3.0, 4.0, 5.0, 6.0, 7.0, 8.0, 9.0]



class ShurikenControl(BaseControl):

    def __init__(self, name="C_ctl_shuriken_0", colour=False, joint=False):
        BaseControl.__init__(self, name, colour, joint)
        self._define_shape()
        self.create()

    def _define_shape(self):
        '''
           diamond controller shape
        '''
        self._cvs = [    (0.0, 0.0, 0.295) ,
                     (-0.497, 0.0, 0.497) ,
                     (-0.295, 0.0, 0.0) ,
                     (-0.497, 0.0, -0.497) ,
                     (0.0, 0.0, -0.295) ,
                     (0.497, 0.0, -0.497) ,
                     (0.295, 0.0, 0.0) ,
                     (0.497, 0.0, 0.497) ,
                     (0.0, 0.0, 0.295) ]

        self._knots =[0.0 , 0.537 , 1.075 , 1.612 , 2.150 , 2.687 , 3.225 , 3.762 , 4.300 ]


class SphereControl(BaseControl):

    def __init__(self, name="C_ctl_sphere_0", colour=False, joint=False):
        BaseControl.__init__(self, name, colour, joint)
        self._define_shape()
        self.create()


    def _define_shape(self):
        '''
            sphere control shape
        '''
        self._cvs = [   ( 0.0, 0.5056, 0.0 ),
                        ( 0.0, 0.4378, -0.2528 ),
                        ( 0.0, 0.2528, -0.4378 ),
                        ( 0.0, 0.0, -0.5056 ),
                        ( 0.0, -0.2528, -0.4378 ),
                        ( 0.0, -0.4378, -0.2528 ),
                        ( 0.0, -0.5056, 0.0 ),
                        ( 0.0, -0.4378, 0.2528 ),
                        ( 0.0, -0.2528, 0.4378 ),
                        ( 0.0, 0.0, 0.5056 ),
                        ( 0.0, 0.2528, 0.4378 ),
                        ( 0.0, 0.4378, 0.2528 ),
                        ( 0.0, 0.5056, 0.0 ),
                        ( -0.2528, 0.4378, 0.0 ),
                        ( -0.4378, 0.2528, 0.0 ),
                        ( -0.5056, 0.0, 0.0 ),
                        ( -0.4378, -0.2528, 0.0 ),
                        ( -0.2528, -0.4378, 0.0 ),
                        ( 0.0, -0.5056, 0.0 ),
                        ( 0.2528, -0.4378, 0.0 ),
                        ( 0.4378, -0.2528, 0.0 ),
                        ( 0.5056, 0.0, 0.0 ),
                        ( 0.4378, 0.2528, 0.0 ),
                        ( 0.2528, 0.4378, 0.0 ),
                        ( 0.0, 0.5056, 0.0 ),
                        ( 0.0, 0.4378, -0.2528 ),
                        ( 0.0, 0.2528, -0.4378 ),
                        ( 0.0, 0.0, -0.5056 ),
                        ( 0.2528, 0.0, -0.4378 ),
                        ( 0.4378, 0.0, -0.2528 ),
                        ( 0.5056, 0.0, 0.0 ),
                        ( 0.4378, 0.0, 0.2528 ),
                        ( 0.2528, 0.0, 0.4378 ),
                        ( 0.0, 0.0, 0.5056 ),
                        ( -0.2528, 0.0, 0.4378 ),
                        ( -0.4378, 0.0, 0.2528 ),
                        ( -0.5056, 0.0, 0.0 ),
                        ( -0.4378, 0.0, -0.2528 ),
                        ( -0.2528, 0.0, -0.4378 ),
                        ( 0.0, 0.0, -0.5056 )    ]

        self._knots = [0.0 , 1.0 , 2.0 , 3.0 , 4.0 , 5.0 , 6.0 , 7.0 , 8.0 , 9.0 ,
                       10.0 , 11.0 , 12.0 , 13.0 , 14.0 , 15.0 , 16.0 , 17.0 , 18.0 , 19.0 ,
                       20.0 , 21.0 , 22.0 , 23.0 , 24.0 , 25.0 , 26.0 , 27.0 , 28.0 , 29.0 ,
                       30.0 , 31.0 , 32.0 , 33.0 , 34.0 , 35.0 , 36.0 , 37.0 , 38.0 , 39.0     ]


class SquareControl(BaseControl):

    def __init__(self, name="C_ctl_box_0", colour=False, joint=False):
        BaseControl.__init__(self, name, colour, joint)
        self._define_shape()
        self.create()

    def _define_shape(self):
        '''
            flat horizontal square at origin
        '''
        self._cvs = [   ( -0.5, 0.0, -0.5 ),
                        ( 0.5, 0.0, -0.5 ),
                        ( 0.5, 0.0, 0.5 ),
                        ( -0.5, 0.0, 0.5 ),
                        ( -0.5, 0.0, -0.5 )    ]

        self._knots = [0.0 , 1.0 , 2.0 , 3.0 , 4.0]


class StarControl(BaseControl):

    def __init__(self, name="C_ctl_arrow_0", colour=False, joint=False):
        BaseControl.__init__(self, name, colour, joint)
        self._define_shape()
        self.create()


    def _define_shape(self):
        '''
            multi pointed arrow control
        '''
        self._cvs =[(1.2325248553316348,-0.015000562413539628,0.50885414388844197),
                    (1.0105487913965072,-0.012161109945534612,0.13494420758198444),
                    (0.9441806852666017,-0.011445284794313499,0.29572112560278363),
                    (0.28977217794697108,-0.0034680975053394038,-0.00034414770173185616),
                    (0.94347907215939464,-0.011146904572473162,-0.29796426262334563),
                    (1.0102271550490325,-0.012024261774552141,-0.1373454588536287),
                    (1.2313181660965213,-0.014487595080034296,-0.51178184840837382),
                    (0.80998290638010151,-0.0093921901683230863,-0.61920187016278661),
                    (0.87673098926975035,-0.010269547370398958,-0.45858306639307855),
                    (0.20465749288467738,-0.0023493240708222542,-0.20515930202674859),
                    (0.4564679905187089,-0.0050346400722995933,-0.87788306229913537),
                    (0.61723210208371293,-0.006991235169717681,-0.81151078266151799),
                    (0.50882214699606132,-0.0054879928260351523,-1.2326230381595629),
                    (0.13493976738874203,-0.0011214498774651405,-1.0106276215743808),
                    (0.29570387895371542,-0.0030780449748821735,-0.94425534193675276),
                    (-0.00034240666335871861,0.00014564694305607695,-0.28979455131238119),
                    (-0.2979356742496011,0.0040268463493702989,-0.94355016205347653),
                    (-0.1373288771321578,0.0021371590956565153,-1.0103043493617534),
                    (-0.51173504788861579,0.0067264018737736454,-1.2314102170514793),
                    (-0.61914926848450036,0.0078062208567982513,-0.81004178743687305),
                    (-0.45854247136705606,0.0059165336030827746,-0.87679597474517301),
                    (-0.2051422505497672,0.0025553061947242179,-0.20467208212132704),
                    (-0.87781257913669886,0.010729459643087165,-0.45649804362360591),
                    (-0.81144447300675782,0.010013634491864801,-0.61727496164442108),
                    (-1.2325248553316459,0.015000562413532524,-0.50885414388844197),
                    (-1.0105487913965361,0.012161109945527758,-0.13494420758197023),
                    (-0.94418068526661947,0.011445284794306421,-0.29572112560278541),
                    (-0.28977217794698418,0.0034680975053323852,0.00034414770169632902),
                    (-0.9434790721594164,0.011146904572469305,0.29796426262334741),
                    (-1.0102271550490645,0.012024261774545067,0.1373454588536287),
                    (-1.2313181660965438,0.014487595080027385,0.51178184840835783),
                    (-0.80998290638012338,0.0093921901683147891,0.61920187016279371),
                    (-0.87673098926977766,0.010269547370392105,0.45858306639305013),
                    (-0.20465749288470303,0.0023493240708149007,0.20515930202675925),
                    (-0.45646799051874765,0.0050346400722924897,0.87788306229911939),
                    (-0.61723210208373791,0.0069912351697107421,0.81151078266151444),
                    (-0.50882214699608297,0.0054879928260267181,1.2326230381595629),
                    (-0.1349397673887387,0.0011214498774583404,1.010627621574379),
                    (-0.29570387895373007,0.0030780449748768184,0.94425534193675631),
                    (0.00034240666333396064,-0.00014564694306465169,0.28979455131237408),
                    (0.29793567424957967,-0.0040268463493772083,0.94355016205347297),
                    (0.13732887713212127,-0.0021371590956621497,1.0103043493617676),
                    (0.5117350478885867,-0.0067264018737793613,1.2314102170514882),
                    (0.61914926848447727,-0.0078062208568050774,0.81004178743686595),
                    (0.45854247136702575,-0.0059165336030885755,0.87679597474516946),
                    (0.20514225054973156,-0.002555306194729658,0.20467208212132348),
                    (0.87781257913666011,-0.010729459643094215,0.45649804362360058),
                    (0.81144447300675193,-0.010013634491871879,0.61727496164442286),
                    (1.2325248553316348,-0.015000562413539628,0.50885414388844197)]

        self._knots = [0.0, 1.0, 2.0, 3.0, 4.0, 5.0, 6.0, 7.0, 8.0, 9.0, 10.0, 11.0, 12.0,
                       13.0, 14.0, 15.0, 16.0, 17.0, 18.0, 19.0, 20.0, 21.0, 22.0, 23.0, 24.0,
                       25.0, 26.0, 27.0, 28.0, 29.0, 30.0, 31.0, 32.0, 33.0, 34.0, 35.0, 36.0,
                       37.0, 38.0, 39.0, 40.0, 41.0, 42.0, 43.0, 44.0, 45.0, 46.0, 47.0, 48.0]


#####################################
#  Face Controls
#####################################
class FaceBaseControl(BaseControl):
    '''
     different control structure requires some slightly different implementations
    '''
    def __init__(self, name="C_ctl_Square_0", colour="yellow"):
        BaseControl.__init__(self, name, colour, joint=False)
        
    
    def set_position(self, trans=False, rot=False, sc=False, obj=None):
        '''
        no need to freeze transforms
        '''
        if obj:
            trans = cmds.xform(obj, q=True, ws=True, t=True)
        if trans or obj:
            cmds.xform(self.name, ws=True, t=trans)
        if rot:
            cmds.xform(self.name, ws=True, ro=rot)
        if sc:
            cmds.xform(self.name, ws=True, s=sc)
    
        
class SquareFaceControl(FaceBaseControl):
    '''
     slight different implementation, using other control object to create a 
     square face control panel
    '''
    def __init__(self, name="C_ctl_Square_0", colour="yellow"):
        BaseControl.__init__(self, name, colour, joint=False)
        self.colour = colour
        self.create(name)
         
    def create(self, name):
        #make control border
        panel = SquareControl()
        panel.set_position(rot=[90,0,0], sc=[2,2,2])
        panel.hide_transforms()
        cmds.setAttr("%s.overrideEnabled" %panel.shape, 1)
        cmds.setAttr("%s.overrideDisplayType" %panel.shape, 2)
        
        #make the animation control 
        control = Arrow4Control(name)
        control.set_position(rot=[90,0,0], sc=[0.1,0.1,0.1])
        control.set_colour(self.colour)
        control.hide_rotation()
        control.hide_scale()
        control.lock_hide("v")
        control.lock_hide("tz")
        control.set_limits(trans=[(-1,1), (-1,1),(-1,1)])
        
        #clean
        self.name = cmds.group([panel.name, control.name], n="%s_grp" %name)
        self.ctl = control.name
        self.shape = control.shape
        cmds.parent(control.name, panel.name)
        panel.rename("%s_border" %name)


class HorizontalFaceControl(FaceBaseControl):
    '''
     slight different implementation, using other control object to create a 
     square face control panel
    '''
    def __init__(self, name="C_ctl_Horizontal_0", colour="yellow", orient="centre"):
        '''
        orient = centre, left or right determines the starting position of the anim ctl
        '''
        BaseControl.__init__(self, name, colour, joint=False)
        self.colour = colour
        self.orient = orient
        self.create(name)
         
    def create(self, name):
        #make control border
        panel = SquareControl()
        panel.set_position(rot=[90,0,0], sc=[2,1,0.5])
        cmds.setAttr("%s.overrideEnabled" %panel.shape, 1)
        cmds.setAttr("%s.overrideDisplayType" %panel.shape, 2)
        
        #make the animation control 
        control = Arrow4Control(name)
        control.set_position(rot=[90,0,0], sc=[0.1,0.1,0.1])
        control.set_colour(self.colour)
        control.set_limits(trans=[(-1,1), (-1,1),(-1,1)])

        #clean
        self.name = cmds.group([panel.name, control.name], n="%s_grp" %name)
        self.ctl = control.name
        self.shape = control.shape
        cmds.parent(control.name, panel.name)
        panel.rename("%s_border" %name)
        
        #scale and set limits to re-orient the controller and keep it normalised
        if self.orient == "left":
            control.set_position(trans=[-1,0,0])
            panel.set_position(sc=[0.5,1,1])
            cmds.setAttr("%s.sx" %self.name, 2)
            control.set_limits(trans=[(0,1), (0,0),(0,0)])
            
        if self.orient == "right":
            control.set_position(trans=[1,0,0])
            panel.set_position(sc=[0.5,1,1])
            cmds.setAttr("%s.sx" %self.name, 2)
            cmds.setAttr("%s.rotateAxisY" %control.name, 180)
            control.set_limits(trans=[(-1,0), (0,0),(0,0)])
        
        #lock and hide
        panel.hide_transforms()
        control.hide_rotation()
        control.hide_scale()
        control.lock_hide("v")
        control.lock_hide("tz")
        control.lock_hide("ty")


class VerticalFaceControl(FaceBaseControl):
    '''
     slight different implementation, using other control object to create a 
     square face control panel
    '''
    def __init__(self, name="C_ctl_Horizontal_0", colour="yellow", orient="centre"):
        '''
        orient = centre, top or bottom determines the starting position of the anim ctl
        '''
        BaseControl.__init__(self, name, colour, joint=False)
        self.colour = colour
        self.orient = orient
        self.create(name)
         
    def create(self, name):
        #make control border
        panel = SquareControl()
        panel.set_position(rot=[90,0,0], sc=[0.5,1,2])
        cmds.setAttr("%s.overrideEnabled" %panel.shape, 1)
        cmds.setAttr("%s.overrideDisplayType" %panel.shape, 2)
        
        #make the animation control 
        control = Arrow4Control(name)
        control.set_position(rot=[90,0,0], sc=[0.1,0.1,0.1])
        control.set_colour(self.colour)
        control.set_limits(trans=[(-1,1), (-1,1),(-1,1)])

        #clean
        self.name = cmds.group([panel.name, control.name], n="%s_grp" %name)
        self.ctl = control.name
        self.shape = control.shape
        cmds.parent(control.name, panel.name)
        panel.rename("%s_border" %name)
        
        #scale and set limits to re-orient the controller and keep it normalised
        if self.orient == "bottom":
            control.set_position(trans=[0,-1,0])
            panel.set_position(sc=[1,0.5,1])
            cmds.setAttr("%s.sy" %self.name, 2)
            control.set_limits(trans=[(0,0), (0,1),(0,0)])
            
        if self.orient == "top":
            control.set_position(trans=[0,1,0])
            panel.set_position(sc=[1,0.5,1])
            cmds.setAttr("%s.sy" %self.name, 2)
            cmds.setAttr("%s.rotateAxisX" %control.name, 180)
            control.set_limits(trans=[(0,0), (-1,0),(0,0)])
            
        #lock and hide
        panel.hide_transforms()
        control.hide_rotation()
        control.hide_scale()
        control.lock_hide("v")
        control.lock_hide("tz")
        control.lock_hide("tx")
        
    


#####################################
#  utility functions
#####################################

def get_curve_info(name=False):
    '''
     used to get the curve data from a hand drawn curve in maya - for adding a new curve type to the
     class structure
    '''
    if not name:
        name = cmds.ls(sl=True)[0]
    
    #    sanity check
    if not cmds.objExists(name):
        print 'object %s not found, aborting' % name
        return

    #    check for nurbs curve shape
    if cmds.nodeType(name) == "nurbsCurve":
        shape   =   name
    else:
        shpList =   cmds.listRelatives(name, s=True)
        shape   =   shpList[0]

    # use the API to get the curve data
    Mlist = OpenMaya.MSelectionList()
    OpenMaya.MGlobal.getSelectionListByName(shape, Mlist)
    dPath = OpenMaya.MDagPath()
    Mlist.getDagPath(0, dPath)

    crv = OpenMaya.MFnNurbsCurve(dPath)

    degree = crv.degree()

    cvs = OpenMaya.MPointArray()
    knots = OpenMaya.MDoubleArray()

    crv.getCVs(cvs)
    crv.getKnots(knots)

    # print to the script editor for use
    print "DEGREE"
    print degree

    print "CVS"
    length = cvs.length()
    print "["
    for i in range(length):
        print ('(' + `cvs[i][0]` + ',' + `cvs[i][1]` +',' + `cvs[i][2]`+'),')
    print "]"

    print "KNOTS"
    print knots




#####################################
#  CODE TESTING
#####################################

#test = ArcControl()
#test = CircleControl()
#test.setColour('green')
#test.set_position([0,1,0], [0,90,0])


#test.add_offset()
#test.hide_rotation()
#test.hide_translation()
#test.hide_scale()
#test.lock_hide("v")
#get_curve_info("curve1")