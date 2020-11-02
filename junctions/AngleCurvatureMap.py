import numpy as np
import math

from junctions.StandardCurvatures import StandardCurvature

class AngleCurvatureMap:

    @staticmethod
    def getCurvatureForJunction(angleBetweenRoads, standardCurvature = StandardCurvature.Medium.value):
        """Angle must be normalized by 360

        Args:
            angleBetweenRoads ([type]): clockwise angle from the road with lower id to higher id.
        """

        angle = angleBetweenRoads
        if angle > 1.5 * np.pi:
            angle = 2 * np.pi  - angleBetweenRoads

        if angle <= (np.pi / 2) : # less than 90 or greater than 270
            if angle < (np.pi / 4) : # less than 45 or > 315
                if angle < (np.pi / 6):
                    return StandardCurvature.UltraSharp.value
                return StandardCurvature.Sharp.value
            if angle < (np.pi / 3): # less than 45
                return StandardCurvature.MediumSharp.value
            
            return StandardCurvature.Medium.value
        else:
            angle = abs(angle - np.pi) # now lower the angle means lower the curvature as the junction tends to be straighter

            if angle < (np.pi / 2) : # less than 90 or greater than 270
                if angle < (np.pi / 4) : # less than 45 or > 315
                    if angle < (np.pi / 6):
                        return StandardCurvature.VeryWide.value
                    return StandardCurvature.Wide.value
                if angle < (np.pi / 3): # less than 45
                    return StandardCurvature.MediumWide.value
                return StandardCurvature.Medium.value

            return StandardCurvature.Medium.value
