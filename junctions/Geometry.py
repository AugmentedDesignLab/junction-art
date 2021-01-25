from abc import ABC, abstractmethod
import numpy as np
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

        curveRange = np.arange(spiral.curvestart + 0.001, spiral.curveEnd, 0.001)

        fromCurv = spiral.curvstart

        points = []

        for nextCurve in curveRange:
        
            eulerSp = EulerSpiral.createFromLengthAndCurvature(self.length, fromCurv, nextCurve)
            (deltax, deltay, t) = eulerSp.calc(self.length, x, y, self.curvstart, h)
            points.append((deltax, deltay))