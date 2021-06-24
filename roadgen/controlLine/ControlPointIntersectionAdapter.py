from extensions.moreHelpers import laneWidths
from junctions.Intersection import Intersection
from roadgen.controlLine.ControlPoint import ControlPoint
from roadgen.controlLine.ControlLine import ControlLine
from extensions.CountryCodes import CountryCodes
import math, logging, pyodrx
import numpy as np
import logging

class ControlPointIntersectionAdapter:

    
    @staticmethod
    def createIntersection(id, builder, point: ControlPoint, firstIncidentId, randomizeDistance = False, randomizeHeading=False):

        ControlPointIntersectionAdapter.orderAjacentCW(point)
        distance = 15
        country = CountryCodes.US
        laneWidth = 3
        roadDefs = []

        nIncidentPoints = len(point.adjacentPointsCWOrder)

        for heading, adjPoint in point.adjacentPointsCWOrder.items():
            # # we get a point between point and adjPoint which is close to the point.
            # len = math.sqrt((point.position[0] - adjPoint.position[0]) ** 2 + (point.position[1] - adjPoint.position[1]) ** 2)
            # xDiff = adjPoint.position[0] - point.position[0]
            # theta = math.acos(xDiff / len)
            randomDistance = distance
            if randomDistance:
                randomDistance = distance * np.random.uniform(0.5, 1.1)
            if randomizeHeading:
                heading = heading * np.random.uniform(0.95, 1.05)

            if point.position[0] <= adjPoint.position[0]:
                line = ControlLine(None, point.position, adjPoint.position)
                incidentPoint = line.createNextControlPoint(randomDistance)
            else:
                line = ControlLine(None, adjPoint.position, point.position)
                incidentPoint = line.createNextControlPoint(line.len - randomDistance)
            logging.info(f"Incident point {incidentPoint.position}, heading {round(math.degrees(heading), 2)}")
            
            skipEndpoint = None
            medianType = None
            if nIncidentPoints >= 3:
                if np.random.choice([True, False], p=[0.3, 0.7]):
                    medianType='partial'
                    skipEndpoint = pyodrx.ContactPoint.end
                # else:
                #     medianType='full'


            roadDef = {
                'x': incidentPoint.position[0], 'y': incidentPoint.position[1], 'heading': heading, 
                'leftLane': 1, 'rightLane': 1, 
                'medianType': medianType, 'skipEndpoint': skipEndpoint
            }
            roadDefs.append(roadDef)

        intersection = builder.createIntersectionFromPointsWithRoadDefinition(odrID=0,
                                                                roadDefinition=roadDefs,
                                                                firstRoadId=firstIncidentId,
                                                                straightRoadLen=10, getAsOdr = False)
        return intersection

            

    @staticmethod
    def getAdjacentPointOutsideRoadIndexMap(point: ControlPoint, intersection: Intersection):
        map = {}
        # orderedAdjacentPoints = list(point.adjacentPointsCWOrder.values())
        # index = orderedAdjacentPoints.index(adjP)

        index = 0
        for adjP in point.adjacentPointsCWOrder.values():
            # map[adjP] = intersection.incidentRoads[index]
            map[adjP] = index
            index += 1
        
        return map
        


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
        



