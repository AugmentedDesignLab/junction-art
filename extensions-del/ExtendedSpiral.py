import pyodrx

class ExtendedSpiral(pyodrx.Spiral):

    def __init__(self,curvstart,curvend,length=None,angle=None,cdot=None):
        """ initalizes the Spline
 
        Parameters
        ----------
            curvstart (float): starting curvature of the Spiral
 
            curvend (float): final curvature of the Spiral
        """ 
        self.angle = angle
        super().__init__(curvstart, curvend, length, angle, cdot)

        pass