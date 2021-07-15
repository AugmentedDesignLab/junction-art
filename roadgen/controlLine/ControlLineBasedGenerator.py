from roadgen.controlLine.ControlPoint import ControlPoint
from junctions.Intersection import Intersection
from roadgen.controlLine.ControlLineGrid import ControlLineGrid
from roadgen.controlLine.ControlLine import ControlLine
from roadgen.controlLine.ControlPointIntersectionAdapter import ControlPointIntersectionAdapter
from junctions.LaneSides import LaneSides
from junctions.RoadBuilder import RoadBuilder
from extensions.ExtendedRoad import ExtendedRoad
from junctions.ODRHelper import ODRHelper
from junctions.LaneLinker import LaneLinker
from junctions.RoadLinker import RoadLinker
from junctions.LaneBuilder import LaneBuilder
from junctions.JunctionBuilderFromPointsAndHeading import JunctionBuilderFromPointsAndHeading
from extensions.CountryCodes import CountryCodes
from junctions.LaneMarkGenerator import LaneMarkGenerator
import logging, math, pyodrx
import numpy as np

class ControlLineBasedGenerator:


    def __init__(self, mapSize, debug=False,
                    randomizeLanes=True,
                    randomizeDistance = True, randomizeHeading=False,
                    country=CountryCodes.US, seed=101) -> None:
        self.name = "ControlLineBasedGenerator"
        self.mapSize = mapSize
        self.randomizeLanes = randomizeLanes
        self.randomizeDistance = randomizeDistance
        self.randomizeHeading = randomizeHeading
        self.country = country
        self.debug = debug
        self.lines = None
        self.pairs = None
        self.grid = None
        self.laneLinker = LaneLinker(countryCode=country)
        self.roadBuilder = RoadBuilder()
        self.laneBuilder = LaneBuilder()
        self.laneMarkGenerator = LaneMarkGenerator(countryCode=country)
        self.connectionRoads = []
        self.controlPointIntersectionMap = {} # controlpoint -> its intersection
        self.nextRoadId = 0
        self.nextIntersectionId = 0
        self.odrList = []
        self.intersectionBuilder = JunctionBuilderFromPointsAndHeading(country=country,
                                                            laneWidth=3)
        self.laneConfigurations = None

        self.nLaneDistributionOnASide = [0.2, 0.5, 0.2, 0.1] # 0, 1, 2, 3
        
        np.random.seed(seed)
        pass


    #region grid
    def createGridWithHorizontalControlLines(self, nLines):

        self.lines = []
        self.pairs = []

        minSeperationBetweenEndpoints = 80
        maxSeperationBetweenEndpoints = 200

        bigSeperationAdditional = 200


        for i in range(nLines):

            start = (0,0)
            end = (self.mapSize[0], 0)

            if i > 0:
                prevLine = self.lines[-1]
                startY = prevLine.start[1] + np.random.uniform(minSeperationBetweenEndpoints, maxSeperationBetweenEndpoints)
                # endY = prevLine.end[1] + np.random.uniform(minSeperationBetweenEndpoints, maxSeperationBetweenEndpoints)
                endY = startY + np.random.uniform(-0.3, 0.3) * startY
                logging.info(f"{self.name}: endY before adjustment = {endY}")

                # validate min distance.
                
                if endY < prevLine.end[1] + minSeperationBetweenEndpoints:
                    # endY = prevLine.end[1] + np.random.uniform(minSeperationBetweenEndpoints, maxSeperationBetweenEndpoints) + minSeperationBetweenEndpoints
                    endY = prevLine.end[1] + minSeperationBetweenEndpoints
                    # endY = startY + np.random.uniform(0, 0.3) * startY
                
                # big seperation
                if np.random.choice([True, False], p=[0.25, 0.75]):
                    startY += bigSeperationAdditional
                    endY += bigSeperationAdditional

                startX = 0
                endX = self.mapSize[0]
                # randomly shorten lines
                if np.random.choice([True, False], p=[0.2, 0.8]):
                    #
                    endpoints = np.random.choice(['start', 'end', 'both'], p=[0.3, 0.3, 0.4])
                    if endpoints == 'start':
                        startX += endX * 0.2
                    if endpoints == 'end':
                        endX -= endX * 0.2
                    if endpoints == 'both':
                        startX += endX * 0.2
                        endX -= endX * 0.2

                


                start = (startX, startY)
                end = (endX, endY)

                endProjection = prevLine.line.project_point(end)
                endDistance = np.linalg.norm(np.array(end) - np.array(endProjection))
                
                logging.info(f"{self.name}: endDistance = {endDistance}")
                if endDistance < minSeperationBetweenEndpoints:
                    # a hack
                    end = (endX, endY + minSeperationBetweenEndpoints)



            line = ControlLine(i+1, start, end)

            logging.info(f"{self.name}: created line #{line.id} at {line.start}, {line.end}")

            self.lines.append(line)
            if i > 0:
                self.pairs.append((self.lines[-2], self.lines[-1]))

        self.grid = ControlLineGrid(controlLinePairs=self.pairs, debug=True)

        for pair in self.pairs:
            self.grid.connectControlLinesWithRectsAndTriangles(pair)

        for line in self.lines:
            self.grid.connectControlPointsOnALine(line)

        self.grid.plot()

        pass

    
    def createTestGridWithHorizontalControlLines(self, nLines):

        line1 = ControlLine(1, (0,0), (1000, 0))

        line2 = ControlLine(2, (0,100), (1000, 130))

        line3 = ControlLine(3, (0,250), (1000, 220))

        line4 = ControlLine(4, (100, 500), (600, 550))
        line5 = ControlLine(5, (0,600), (700, 620))
        line6 = ControlLine(6, (0,700), (1000, 700))
        line7 = ControlLine(7, (0,770), (1000, 800))
        
        pairs = [(line1, line2), (line2, line3), (line3, line4), (line4, line5), (line5, line6), (line6, line7)]
        self.lines= [line1, line2, line3, line4, line5, line6, line7]
        # pairs = [(line1, line2)]
        # self.lines= [line1, line2]
        self.pairs = pairs
        grid = ControlLineGrid(controlLinePairs=pairs, debug=True)

        for pair in self.pairs:
            grid.connectControlLinesWithRectsAndTriangles(pair)

        


        for line in self.lines:
            grid.connectControlPointsOnALine(line)

        self.grid = grid
        pass
    
    #endregion
    
    def generateWithHorizontalControlines(self, name, nLines):

        # 1 grid creation
        self.createGridWithHorizontalControlLines(nLines)

        # 1.1
        # build clockwise adjacent points structure
        
        self.buildClockwiseAdjacentMapForControlPoints()

        # 2. define lanes for each connection
        if self.randomizeLanes:
            self.createLaneConfigurationsForConnections()
        else:
            self.laneConfigurations = None

        # 3. create intersections for each control point
        self.createIntersectionsForControlPoints()

        # now we have the intersections
        # for each connection, find the pair of intersections, find the pair of controlpoints, create straight connection road.
        self.createConnectionRoadsBetweenIntersections()
        
        combinedOdr = ODRHelper.combine(self.odrList, name, countryCode=self.country)
        ODRHelper.addAdjustedRoads(combinedOdr, self.connectionRoads)
        return combinedOdr
        

    def buildClockwiseAdjacentMapForControlPoints(self):
        for (line1, line2, point1, point2) in self.grid.connections:
            if len(point1.adjacentPointsCWOrder) == 0:
                ControlPointIntersectionAdapter.orderAjacentCW(point1)
            if len(point2.adjacentPointsCWOrder) == 0:
                ControlPointIntersectionAdapter.orderAjacentCW(point2)
        pass


    def createIntersectionsForControlPoints(self):
        
        for (line1, line2, point1, point2) in self.grid.connections:

            
            if point1 not in self.controlPointIntersectionMap and len(point1.adjacentPoints) >= 2:
                print(f"{self.name}: Creating intersection for line {line1.id} p = {point1.position}")
                point1.intersection = ControlPointIntersectionAdapter.createIntersection(self.nextIntersectionId, self.intersectionBuilder, point1, self.nextRoadId,
                                                                                            randomizeDistance=self.randomizeDistance,
                                                                                            randomizeHeading=self.randomizeHeading,
                                                                                            laneConfigurations=self.laneConfigurations,
                                                                                            debug=self.debug)
                self.nextRoadId = point1.intersection.getLastRoadId() + 100
                self.nextIntersectionId += 1

                point1.adjPointToOutsideIndex = ControlPointIntersectionAdapter.getAdjacentPointOutsideRoadIndexMap(point1, point1.intersection)
                self.controlPointIntersectionMap[point1] = point1.intersection
                self.odrList.append(point1.intersection.odr)

            if point2 not in self.controlPointIntersectionMap and len(point2.adjacentPoints) >= 2:
                print(f"{self.name}: Creating intersection for line {line2.id} p = {point2.position}")
                point2.intersection = ControlPointIntersectionAdapter.createIntersection(self.nextIntersectionId, self.intersectionBuilder, point2, self.nextRoadId,
                                                                                            randomizeDistance=self.randomizeDistance,
                                                                                            randomizeHeading=self.randomizeHeading,
                                                                                            laneConfigurations=self.laneConfigurations,
                                                                                            debug=self.debug)
                self.nextRoadId = point2.intersection.getLastRoadId() + 100
                self.nextIntersectionId += 1

                point2.adjPointToOutsideIndex = ControlPointIntersectionAdapter.getAdjacentPointOutsideRoadIndexMap(point2, point2.intersection)
                self.controlPointIntersectionMap[point2] = point2.intersection
                self.odrList.append(point2.intersection.odr)

        pass


    def createConnectionRoadsBetweenIntersections(self):
        # for each connection, find the pair of intersections, find the pair of controlpoints, create straight connection road.
        for (line1, line2, point1, point2) in self.grid.connections:

            print(f"{self.name}: Creating connections between {point1.position} and {point2.position}")
            
            point1IncidentIndex = point1.adjPointToOutsideIndex[point2]
            point2IncidentIndex = point2.adjPointToOutsideIndex[point1]

            road1 = point1.intersection.incidentRoads[point1IncidentIndex]
            cp1 =  self.reverseCP(point1.intersection.incidentCPs[point1IncidentIndex])
            road2 = point2.intersection.incidentRoads[point2IncidentIndex]
            cp2 = self.reverseCP(point2.intersection.incidentCPs[point2IncidentIndex])

            self.connect(self.nextRoadId, intersection1=point1.intersection, road1=road1, cp1=cp1,
                                          intersection2=point2. intersection, road2=road2, cp2=cp2, 
                                          laneSides=LaneSides.BOTH)
            self.nextRoadId += 1
        pass

    #region lane configurations for each control point
    def createLaneConfigurationsForConnections(self):

        self.laneConfigurations = {}

        for (line1, line2, point1, point2) in self.grid.connections:

            point1_n_left =  np.random.choice([0, 1, 2, 3], p = self.nLaneDistributionOnASide)
            point1_n_right = np.random.choice([0, 1, 2, 3], p = self.nLaneDistributionOnASide)

            if point1_n_left == 0 and point1_n_right == 0:
                point1_n_left = 1


            if point1 not in self.laneConfigurations:
                self.laneConfigurations[point1] = {}

            if point2 not in self.laneConfigurations:
                self.laneConfigurations[point2] = {}
            
            if point2 not in self.laneConfigurations[point1]:
                # we need to update both
                print(f"{self.name}: createLaneConfigurationsForConnections: Lines ({line1.id, line2.id}, ({point1.position, point2.position}), lanes {point1_n_left, point1_n_right})")
                self.updateLaneConfigurations(point1, point2, point1_n_left, point1_n_right)
        
        self.fixLaneConfigurations(pyodrx.ContactPoint.start)


    def fixLaneConfigurations(self, cp):
        """Assumes all the incident points are START
        """

        # for each adjacent point, the number of incoming lanes must be less than or equal to number of outgoing lanes

        # all the points are connected by START
        for point in self.laneConfigurations:
            self.fixLaneConfigurationsForAPoint(cp, point)
    

    def fixLaneConfigurationsForAPoint(self, cp, point: ControlPoint):
        print(point)
        for adjPoint in point.adjacentPoints:
            # 1. nIncoming on the adjacent point must not be greater than cumulative nOutgoing of other adjacent points
            nIncoming, nOutgoingOthers = self.getIncomingAndOutgoingForIncidentPoint(cp, point=point, adjPoint=adjPoint)
            if nIncoming > nOutgoingOthers:
                nNewOutgoing = nIncoming - nOutgoingOthers
                self.increaseOutGoing(cp, point, adjPoint, nNewOutgoing)
            
            # TODO 2. if nOutgoing on the adjacent  is not 0, cumulative nIncoming of other adjacent points cannot be 0
            nOutgoing = self.getNumOutgoning(cp, self.laneConfigurations[point][adjPoint])
            if nOutgoing > 0:
                #
                nOutgoing, nIncomingOthers = self.getOutgoingAndIncomingForIncidentPoint(cp, point=point, adjPoint=adjPoint)
                if nIncomingOthers == 0:
                    self.addOneIncoming(cp, point, adjPoint)
                pass


    def getIncomingAndOutgoingForIncidentPoint(self, cp, point, adjPoint):

        nIncoming = self.getNumIncoming(cp, self.laneConfigurations[point][adjPoint])
        nOutgoingOthers = 0
        for otherPoint in point.adjacentPoints:
            if otherPoint != adjPoint:
                nOutgoingOthers +=self.getNumOutgoning(cp, self.laneConfigurations[point][otherPoint])
        return nIncoming, nOutgoingOthers    



    def getOutgoingAndIncomingForIncidentPoint(self, cp, point, adjPoint):

        nOutgoing = self.getNumOutgoning(cp, self.laneConfigurations[point][adjPoint])
        nIncomingOthers = 0
        for otherPoint in point.adjacentPoints:
            if otherPoint != adjPoint:
                nIncomingOthers +=self.getNumIncoming(cp, self.laneConfigurations[point][otherPoint])
        return nOutgoing, nIncomingOthers    


    def getNumIncoming(self, cp, laneTuple):

        if self.country == CountryCodes.US:
            if cp == pyodrx.ContactPoint.start:
                #left is incoming lanes
                return laneTuple[0]
            else: # 
                return laneTuple[1]
        else:
            raise Exception(f"{self.name}: getNumIncoming: getNumIncoming non US not implemented")
            

    def getNumOutgoning(self, cp, laneTuple):

        if self.country == CountryCodes.US:
            if cp == pyodrx.ContactPoint.start:
                #right lanes is outgoing
                return laneTuple[1]
            else: # left
                return laneTuple[0]
        else:
            raise Exception(f"{self.name}: getNumOutgoning: getNumIncoming non US not implemented")
            
    
    def addOneIncoming(self, cp, point, adjPoint):
        if self.debug:
            logging.info(f"{self.name}: addOneIncoming: increasing incoming lanes by 1 for intersection point {point.position} for incoming point {adjPoint.position}")

        otherAdjPoints = []
        for otherPoint in point.adjacentPoints:
            if otherPoint != adjPoint:
                otherAdjPoints.append(otherPoint)

        anotherAdjPoint = np.random.choice(otherAdjPoints)
        n_left, n_right = self.laneConfigurations[point][anotherAdjPoint]

        if self.country == CountryCodes.US:
            # increase n_right, as right is outgoing for START
            if cp == pyodrx.ContactPoint.start:
                n_left += 1
            else:
                n_right += 1
            
            self.updateLaneConfigurations(point, anotherAdjPoint, n_left, n_right)

            self.fixLaneConfigurationsForAPoint(cp, anotherAdjPoint)
        else:
            raise Exception(f"{self.name}: increaseOutGoing: getNumIncoming non US not implemented")
        pass

    def increaseOutGoing(self, cp, point, adjPoint, nNewOutgoing):

        if self.debug:
            logging.info(f"{self.name}: increaseOutGoing: increasing outgoing lanes by {nNewOutgoing} for intersection point {point.position} for incoming point {adjPoint.position}")
        otherAdjPoints = []
        for otherPoint in point.adjacentPoints:
            if otherPoint != adjPoint:
                otherAdjPoints.append(otherPoint)
        

        for _ in range(nNewOutgoing):
            # update one other adjacent point randomly. This will also change the other points incoming lanes. So, need to readjust that, too.
            anotherAdjPoint = np.random.choice(otherAdjPoints)
            n_left, n_right = self.laneConfigurations[point][anotherAdjPoint]
            if self.country == CountryCodes.US:
                # increase n_right, as right is outgoing for START
                if cp == pyodrx.ContactPoint.start:
                    n_right += 1
                else:
                    n_left += 1
                
                self.updateLaneConfigurations(point, anotherAdjPoint, n_left, n_right)

                self.fixLaneConfigurationsForAPoint(cp, anotherAdjPoint)
            else:
                raise Exception(f"{self.name}: increaseOutGoing: getNumIncoming non US not implemented")

    def updateLaneConfigurations(self, point1, point2, point1_n_left, point1_n_right):
            # we are connecting at the same cp
            point2_n_left = point1_n_right
            point2_n_right = point1_n_left
            self.laneConfigurations[point1][point2] = (point1_n_left, point1_n_right)
            self.laneConfigurations[point2][point1] = (point2_n_left, point2_n_right)
            # print(f"{self.name}: createLaneConfigurationsForConnections:  ({point1.position, point2.position}), lanes point1 {point1_n_left, point1_n_right}), lanes point2 {point2_n_left, point2_n_right}")


    #endregion

    def reverseCP(self, cp):
         return pyodrx.ContactPoint.start if (cp == pyodrx.ContactPoint.end) else pyodrx.ContactPoint.end




    def connect(self, connectionRoadId, intersection1:Intersection, road1: ExtendedRoad, cp1, intersection2:Intersection, road2: ExtendedRoad, cp2, laneSides):


        if self.debug:
            logging.info(f"{self.name}: connecting intersections ({intersection1.id}, {intersection2.id})")


        connectionRoad = self.roadBuilder.getConnectionRoadBetween(connectionRoadId, road1, road2, cp1, cp2, isJunction=False, laneSides=laneSides)
        RoadLinker.createExtendedPredSuc(predRoad=road1, predCp=cp1, sucRoad=connectionRoad, sucCP=pyodrx.ContactPoint.start)
        road1.addExtendedSuccessor(connectionRoad, 0, pyodrx.ContactPoint.start, xodr=True)
        RoadLinker.createExtendedPredSuc(predRoad=connectionRoad, predCp=pyodrx.ContactPoint.end, sucRoad=road2, sucCP=cp2)
        road2.addExtendedSuccessor(connectionRoad, 0, pyodrx.ContactPoint.end, xodr=True)

        self.laneBuilder.createLanesForConnectionRoad(connectionRoad, road1, road2)
        self.laneLinker.createLaneLinks(road1, connectionRoad)
        self.laneLinker.createLaneLinks(road2, connectionRoad)

        x, y, h = road1.getPosition(cp1)
        ODRHelper.transformRoad(connectionRoad, x, y, h)
        connectionRoad.planview.adjust_geometires()

        # x2, y2, h2 = road2.getPosition(cp2)
        # print(x, y, h)
        # print(x2, y2, h2)
        

        
        self.laneMarkGenerator.addBrokenWhiteToInsideLanesOfARoad(connectionRoad)
        self.connectionRoads.append(connectionRoad)
