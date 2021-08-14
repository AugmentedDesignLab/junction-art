from analysis.metrics.fov.Angle import Angle
import numpy as np

class FovComplexity:


    @staticmethod
    def getAngleDeviationFromSightLine(p1, p2, p3):
        """ p1, p2 forms sightline (in reverse direction), p2, p3 forms other road vector"""

        deviation = np.pi - Angle.cornerAngle(p1, p2, p3) # because the vector for sightline is -v(p1, p2)
        return deviation