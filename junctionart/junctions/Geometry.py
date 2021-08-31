from abc import ABC, abstractmethod
import numpy as np
import math
import pyodrx
from scipy.interpolate import CubicHermiteSpline

class Geometry(ABC):

    @staticmethod
    def headingsTooClose(h1, h2, threshold = 0.1):
        h1 = h1 % (np.pi*2)
        h2 = h2 % (np.pi*2)
        if abs(h1 - h2) % np.pi <= threshold:
            return True
        return False

    

    @staticmethod
    def getLengthOfGeoms(geoms):
        """[summary]

        Args:
            geoms ([type]): List of Geometries of type Arc, Spiral, Line, ParamPoly3

        Returns:
            [type]: [description]
        """
        totalLength = 0
        for geom in geoms:
            _, _, _, length = geom.get_end_data(0, 0, 0)
            totalLength += length
        
        return totalLength

    
    @staticmethod
    def evalPoly(coeffs, pRange):
        vals = []
        for p in pRange:
            val = coeffs[0] # first one is the intercept
            for i in range(1, len(coeffs)):
                val += coeffs[i] * p
                p = p * p # smelly but faster than powers
            
            vals.append(val)
        
        return vals


    @staticmethod
    def evalSpiral(spiral):
        raise NotImplementedError()
        # curveRange = np.arange(spiral.curvestart + 0.001, spiral.curveEnd, 0.001)

        # fromCurv = spiral.curvstart

        # points = []

        # for nextCurve in curveRange:
        
        #     eulerSp = EulerSpiral.createFromLengthAndCurvature(self.length, fromCurv, nextCurve)
        #     (deltax, deltay, t) = eulerSp.calc(self.length, x, y, self.curvstart, h)
        #     points.append((deltax, deltay))


    
    @staticmethod
    def inertialToLocal(localCenter, localRotation, intertialPoint):

        uBeforeRotation = intertialPoint[0] - localCenter[0]
        vBeforeRotation = intertialPoint[1] - localCenter[1]

        u = uBeforeRotation * math.cos(localRotation) + vBeforeRotation * math.sin(localRotation)
        v = -uBeforeRotation * math.sin(localRotation) + vBeforeRotation * math.cos(localRotation) 

        return u, v

    @staticmethod
    def positiveNormalizeHeading(h):
        h = h % (np.pi *2) 
        if h < 0.0:
            h = (np.pi *2) + h
        return h


    @staticmethod
    def getRelativeHeading(rootHeading, anotherHeading):
        return (anotherHeading + (np.pi * 2) - rootHeading) % (np.pi * 2)

        
    @staticmethod
    def headingToTangent(h, tangentMagnitude):

        xComponent = math.cos(h) * tangentMagnitude
        yComponent = math.sin(h) * tangentMagnitude

        return (xComponent, yComponent)


    @staticmethod
    def getCoeffsForParamPoly(x1, y1, h1, x2, y2, h2, cp1, cp2, vShiftForSamePoint=0):
        """ Assumes traffice goes from point1 to point2. By default if the contact point is start, traffic is going into the road, and end, traffic is going out. """

        if cp1 == pyodrx.ContactPoint.start:
            h1 = h1 + np.pi

        if cp2 == pyodrx.ContactPoint.end:
            h2 = h2 + np.pi

        h1 = h1 % (np.pi * 2)
        h2 = h2 % (np.pi * 2)

        # TODO we need to solve the problem with param poly, not a straight road, as there can still be some angles near threshold for which it can fail.

        # if Geometry.headingsTooClose(h1, h2):
        #     # return a straight road. This is flawed because heading is assumed to be 0 for straight roads in pyodrx
        #     return self.getStraightRoadBetween(newRoadId, road1, road2, incomingCp, ioutgoingCp,
        #                             isJunction=isJunction,
        #                             n_lanes=n_lanes,
        #                             lane_offset=lane_offset,
        #                             laneSides=laneSides)
            # TODO return a curve because points can have the same heading, but big translation which creates problem.

        tangentMagnitude = math.sqrt((x1 - x2) ** 2 + (y1 - y2) ** 2) 

        if tangentMagnitude < 3: # it too short, for U-turns
            tangentMagnitude = 3

        localRotation = h1 # rotation of local frame wrt inertial frame.

        u1 = 0
        v1 = 0

        u2, v2 = Geometry.inertialToLocal((x1, y1), localRotation, (x2, y2))

        if u1 == u2 and v1 == v2:
            v1 -= vShiftForSamePoint
            v2 += vShiftForSamePoint

        localStartTangent = Geometry.headingToTangent(0, tangentMagnitude)
        localEndHeading = Geometry.getRelativeHeading(h1, h2)
        localEndTangent = Geometry.headingToTangent(localEndHeading, tangentMagnitude)


        X = [u1, u2]
        Y = [v1, v2]

        tangentX = [localStartTangent[0], localEndTangent[0]]
        tangentY = [localStartTangent[1], localEndTangent[1]]

        # print(f"connecting road #{road1.id} and # {road2.id}: {x1, y1, x2, y2}")
        # print(f"connecting road #{road1.id} and # {road2.id}: X, Y, tangentX, tangentY")
        # print(X)
        # print(Y)
        # print(tangentX)
        # print(tangentY)

        p = [0, 1]

        hermiteX = CubicHermiteSpline(p, X, tangentX)
        hermiteY = CubicHermiteSpline(p, Y, tangentY)

        xCoeffs = hermiteX.c.flatten()
        yCoeffs = hermiteY.c.flatten()
        return xCoeffs, yCoeffs


