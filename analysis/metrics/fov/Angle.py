import numpy as np

class Angle:

    @staticmethod
    def createVectorsForCorner(p0, p1, p2):
        """Corner at p1. returns the interior angle"""

        v0 = np.array(p0) - np.array(p1)
        v1 = np.array(p2) - np.array(p1)
        return v0, v1


    @staticmethod
    def cornerAngle(p0, p1, p2):
        """Corner at p1. returns the interior angle"""
        v0, v1 = Angle.createVectorsForCorner(p0, p1, p2)
        return Angle.vectorAngle(v0, v1)
        

    @staticmethod
    def vectorAngle(v0, v1):
        angle = np.math.atan2(np.linalg.det([v0,v1]),np.dot(v0,v1))
        return abs(angle)
    
    pass


