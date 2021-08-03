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
    def createIntersection(id, builder, point: ControlPoint, firstIncidentId, 
                            randomizeDistance = False, 
                            randomizeHeading=False,
                            laneConfigurations = None,
                            debug=False
                            ):

        # ControlPointIntersectionAdapter.orderAjacentCW(point)
        distance = 15
        maxDistance = 50
        country = CountryCodes.US
        laneWidth = 3
        roadDefs = []

        # point.printAdjacentPointsCW()

        nIncidentPoints = len(point.adjacentPointsCWOrder)
        # if nIncidentPoints > 3:
        #     print(f"4 arms")

        if nIncidentPoints == 0:
            raise Exception(f"ControlPointIntersectionAdapter: createIntersection adjacentPointsCWOrder is empty")

        for heading, adjPoint in point.adjacentPointsCWOrder.items():
            # # we get a point between point and adjPoint which is close to the point.
            
            # randomDistance = distance
            randomDistance = ControlPointIntersectionAdapter.getMinDistance(point, adjPoint, laneConfigurations=laneConfigurations)
            # print(f"distance for point {adjPoint.position} is {randomDistance}")

            if randomDistance > maxDistance:
                raise Exception(f"ControlPointIntersectionAdapter: angle too tight to generate intersection with specified lanes")
            if randomDistance:
                randomDistance = randomDistance * np.random.uniform(1, 1.2)
            if randomizeHeading:
                heading = heading * np.random.uniform(0.95, 1.05)

            if point.position[0] <= adjPoint.position[0]:
                line = ControlLine(None, point.position, adjPoint.position)
                incidentPoint = line.createNextControlPoint(randomDistance)
            else:
                line = ControlLine(None, adjPoint.position, point.position)
                incidentPoint = line.createNextControlPoint(line.len - randomDistance)
            
            actualDistance = math.sqrt((point.position[0] - incidentPoint.position[0]) ** 2 + (point.position[1] - incidentPoint.position[1]) ** 2 )
            # print(f"Incident point {incidentPoint.position}, heading {round(math.degrees(heading), 2)} with actual distance {actualDistance}")
            if debug:
                logging.info(f"Incident point {incidentPoint.position}, heading {round(math.degrees(heading), 2)}")
            
            skipEndpoint = None
            medianType = None
            if nIncidentPoints >= 3:
                if np.random.choice([True, False], p=[0.3, 0.7]):
                    medianType='partial'
                    skipEndpoint = pyodrx.ContactPoint.end
                # else:
                #     medianType='full'

            n_left =  1
            n_right = 1

            if laneConfigurations is not None:
                (n_left, n_right) = laneConfigurations[point][adjPoint]

            roadDef = {
                'x': incidentPoint.position[0], 'y': incidentPoint.position[1], 'heading': heading, 
                'leftLane': n_left, 'rightLane': n_right, 
                'medianType': medianType, 'skipEndpoint': skipEndpoint
            }
            roadDefs.append(roadDef)

        try:
            intersection = builder.createIntersectionFromPointsWithRoadDefinition(odrID=id,
                                                                roadDefinition=roadDefs,
                                                                firstRoadId=firstIncidentId,
                                                                straightRoadLen=10, getAsOdr = False)
            if debug:
                logging.info(f"ControlPointIntersectionAdapter: createIntersection for point {point.position}")
                logging.info(roadDefs)
                logging.info(intersection)
            return intersection
        except Exception as e:
            logging.error(f"ControlPointIntersectionAdapter: point {point.position}: {roadDefs}")
            logging.error(e)
            raise e



    # @staticmethod 
    # def getMinDistance(point: ControlPoint, adjPoint, laneConfigurations = None):

    #     """
    #         Assumes start contact points are incident points
    #     """
    
    #     laneWidth = 3
    #     minDistance = 10
    #     headings = list(point.adjacentPointsCWOrder.keys())
    #     adjPoints = list(point.adjacentPointsCWOrder.values())


    #     # get prev and next points
    #     curIndex = adjPoints.index(adjPoint)
    #     prevIndex = curIndex - 1
    #     if curIndex == len(adjPoints) - 1:
    #         nextIndex = 0
    #     else:
    #         nextIndex = curIndex + 1
        
    #     prevPoint = adjPoints[prevIndex]
    #     nextPoint = adjPoints[nextIndex]
        
    #     n_left =  1
    #     n_right = 1

    #     if laneConfigurations is not None:
    #         (n_left, n_right) = laneConfigurations[point][adjPoint]

    #     # min distance based on the difference in headings
    #     diffWithPrev = abs(headings[curIndex] - headings[prevIndex])
    #     n_left_prev =  1
    #     n_right_prev = 1

    #     if laneConfigurations is not None:
    #         (n_left_prev, n_right_prev) = laneConfigurations[point][prevPoint]
    #     maxNLanes = max(n_left, n_right_prev)
    #     if diffWithPrev <= np.pi / 4: # less than 90:
    #         minWithPrev = minDistance + maxNLanes * 15 / diffWithPrev
    #     elif diffWithPrev <= np.pi / 2: # less than 90:
    #         minWithPrev = minDistance + maxNLanes * 5 / diffWithPrev
    #     else:
    #         minWithPrev = minDistance + maxNLanes * 2
        
    #     if minDistance < minWithPrev:
    #         minDistance = minWithPrev

    #     diffWithNext = abs(headings[curIndex] - headings[nextIndex])
    #     n_left_next =  1
    #     n_right_next = 1

    #     if laneConfigurations is not None:
    #         (n_left_next, n_right_next) = laneConfigurations[point][nextPoint]
    #     maxNLanes = max(n_right, n_left_next)
    #     if diffWithNext <= np.pi / 4: # less than 45:
    #         minWithNext = minDistance + maxNLanes * 15 / diffWithNext
    #     elif diffWithNext <= np.pi / 2: # less than 45:
    #         minWithNext = minDistance + maxNLanes * 5 / diffWithNext
    #     else:
    #         minWithNext = minDistance + maxNLanes * 2
        
    #     if minDistance < minWithNext:
    #         minDistance = minWithNext

        
    #     return minDistance

    @staticmethod 
    def getMinDistance(point: ControlPoint, adjPoint, laneConfigurations = None):

        """
            Assumes start contact points are incident points
        """
    
        laneWidth = 3
        minDistance = 1
        headings = list(point.adjacentPointsCWOrder.keys())
        adjPoints = list(point.adjacentPointsCWOrder.values())


        # get prev and next points
        curIndex = adjPoints.index(adjPoint)
        prevIndex = curIndex - 1
        if curIndex == len(adjPoints) - 1:
            nextIndex = 0
        else:
            nextIndex = curIndex + 1
        
        prevPoint = adjPoints[prevIndex]
        nextPoint = adjPoints[nextIndex]
        
        # print(f"adjPoint", adjPoint)
        # print(f"prevPoint", prevPoint)
        # print(f"nextPoint", nextPoint)
        # print(f"adjHeading", headings[curIndex])
        # print(f"prevHeading", headings[prevIndex])
        # print(f"nextHeading", headings[nextIndex])

        n_left =  1
        n_right = 1

        if laneConfigurations is not None:
            (n_left, n_right) = laneConfigurations[point][adjPoint]

        # min distance based on the difference in headings
        diffWithPrev = abs(headings[curIndex] - headings[prevIndex]) % (np.pi * 2)

        if diffWithPrev > np.pi:
            diffWithPrev = np.pi * 2 - diffWithPrev

        n_left_prev =  1
        n_right_prev = 1

        if laneConfigurations is not None:
            (n_left_prev, n_right_prev) = laneConfigurations[point][prevPoint]

        totalLaneWidth = (n_left + n_right_prev + 1) * laneWidth
        
        if diffWithPrev <= np.pi / 2: # less than 90:
            minWithPrev = abs(totalLaneWidth / math.sin(diffWithPrev))
        else:
            minWithPrev = totalLaneWidth

        # print(f"minWithPrev", minWithPrev)
        # print(f"totalLaneWidth", totalLaneWidth)
        # print(f"diffWithPrev", diffWithPrev)

        
        if minDistance < minWithPrev:
            minDistance = minWithPrev

        diffWithNext = abs(headings[curIndex] - headings[nextIndex]) % (np.pi * 2)
        if diffWithNext > np.pi:
            diffWithNext = np.pi * 2 - diffWithNext
        n_left_next =  1
        n_right_next = 1

        if laneConfigurations is not None:
            (n_left_next, n_right_next) = laneConfigurations[point][nextPoint]
        
        totalLaneWidth = (n_right + n_left_next + 1) * laneWidth

        if diffWithNext <= np.pi / 2: # less than 90:
            minWithNext = abs(totalLaneWidth / math.sin(diffWithNext))
        else:
            minWithNext = totalLaneWidth

        # print(f"minWithNext", minWithNext)
        # print(f"totalLaneWidth", totalLaneWidth)
        # print(f"diffWithNext", diffWithNext)

        if minDistance < minWithNext:
            minDistance = minWithNext

        

        return minDistance
        

        
        

            

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

        for key in sorted(headingDic, reverse=True):
            point.adjacentPointsCWOrder[key] = headingDic[key]
        pass
        



