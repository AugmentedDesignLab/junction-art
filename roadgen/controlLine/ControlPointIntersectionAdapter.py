from junctions.Intersection import Intersection
from roadgen.controlLine.ControlPoint import ControlPoint
from roadgen.controlLine.ControlLine import ControlLine
import math, logging
import numpy as np


class ControlPointIntersectionAdapter:

    @staticmethod
    def createIntersection(point: ControlPoint):

        distance = 15

        for adjPoint in point.adjacentPoints:
            # # we get a point between point and adjPoint which is close to the point.
            # len = math.sqrt((point.position[0] - adjPoint.position[0]) ** 2 + (point.position[1] - adjPoint.position[1]) ** 2)
            # xDiff = adjPoint.position[0] - point.position[0]
            # theta = math.acos(xDiff / len)

            line = ControlLine(None, point.position, adjPoint.position)
            incidentPoint = line.createNextControlPoint(distance)

    

    @staticmethod
    def getHeading(centerPos, pointPos):

        pointPos = [pointPos[0], pointPos[1]]
        # translate point to center
        pointPos[0] = pointPos[0] - centerPos[0]
        pointPos[1] = pointPos[1] - centerPos[1]

        # find angle wrt 1, 0
        xDir = [1, 0]

        unit_vector_1 = xDir / np.linalg.norm(xDir)
        unit_vector_2 = pointPos / np.linalg.norm(pointPos)
        dot_product = np.dot(unit_vector_1, unit_vector_2)
        absAngle = np.arccos(dot_product)
        if pointPos[1] >= 0:
            return absAngle
        else:
            return 2 * np.pi - absAngle

    
    @staticmethod
    def orderAjacentCW(point: ControlPoint):
        headingDic = {}
        for adjP in point.adjacentPoints:
            heading = ControlPointIntersectionAdapter.getHeading(point.position, adjP.position)
            headingDic[heading] = adjP

        for key in sorted(headingDic):
            point.adjacentPointsCWOrder[key] = headingDic[key]
        pass
        



