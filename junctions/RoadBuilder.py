import numpy as np
import os
import pyodrx 
import math

import junctions

class RoadBuilder:


    def getJunctionSelection(self, isJunction):
        if isJunction:
            return 1
        return -1


    def createSimpleCurve(self, connectionRoadId, angleBetweenEndpoints, isJunction = False, curvature = junctions.StandardCurvature.Medium):

        junction = self.getJunctionSelection(isJunction)
        totalRotation = np.pi - angleBetweenEndpoints
        arcAngle = np.pi / 10000000
        clothAngle = totalRotation / 2
        
        return pyodrx.create_cloth_arc_cloth(curvature, arc_angle=arcAngle, cloth_angle=clothAngle, r_id=connectionRoadId, junction = junction)

    
    def createSimpleCurveWithLongArc(self, connectionRoadId, angleBetweenEndpoints, isJunction = False, curvature = junctions.StandardCurvature.Medium): 
        
        junction = self.getJunctionSelection(isJunction)

        totalRotation = np.pi - angleBetweenEndpoints

        # most of the angleBetweenEndpoints should be assigned to the Arc
        arcAngle = totalRotation * 0.8 # main curve
        clothAngle = (totalRotation * 0.2) / 2 # curve more.

        print(f"arcAngle: {math.degrees(arcAngle)}")
        print(f"clothAngle: {math.degrees(clothAngle)}")

        return pyodrx.create_cloth_arc_cloth(curvature, arc_angle=arcAngle, cloth_angle=clothAngle, r_id=connectionRoadId, junction = junction)

