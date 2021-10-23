import numpy as np
import math

from junctionart.junctions.StandardCurvatures import StandardCurvature
from junctionart.junctions.StandardCurveTypes import StandardCurveTypes

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
    
    @staticmethod
    def getCurvatureForNonOverlappingRoads(angleBetweenRoads = 120, numberOfLanes = 2, laneOffset = 3):
        """Angle in degree

        Args:
            angleBetweenRoads ([type]): clockwise angle from the road with lower id to higher id.
            numberOfLanes: how many lanes 
            laneOffset: offset of each lane
        """
        radius = laneOffset * (numberOfLanes - 0.5)
        angle = math.radians(angleBetweenRoads)
        curve = 1/radius
        return curve, angle



    @staticmethod
    def getMaxCurvatureAgainstMaxRoadWidth(angleBetweenRoads, maxLaneWidth):
        """Angle in degree

        Args:
            angleBetweenRoads ([type]): clockwise angle from the road with lower id to higher id.
            numberOfLanes: how many lanes 
            laneOffset: offset of each lane
        """
        radius = maxLaneWidth 
        if radius < 3:
            radius = 3
        curve = 1/radius
        return curve


    @staticmethod
    def getCurvatureForAngleBetweenRoadAndLength(angleBetweenRoads, length, curveType):
        """The length of the curve will roughly be 'length'. It's useful to make long curves irrespective of angle between roads.

        Args:
            angleBetweenRoads ([type]): clockwise angle between two roads (simple presentation)
            length ([type]): desired length of the curve road that will be used to connect the roads.

        Returns:
            [type]: [description]
        """

        # length adjustment
        if curveType == StandardCurveTypes.LongArc:
            length = length * 0.9
        elif curveType == StandardCurveTypes.Simple: # spirals cover more distance for a given angle.
            length = length * 0.5

        angleRad = np.pi - angleBetweenRoads
        return angleRad / length

    
    @staticmethod
    def getLength(angleBetweenRoads, curvature, curveType):

        angleRad = np.pi - angleBetweenRoads

        length = angleRad / curvature

        if curveType == StandardCurveTypes.LongArc:
            length = length * 1.1
        elif curveType == StandardCurveTypes.Simple: # spirals cover more distance for a given angle.
            length = length * 2
        
        return length

