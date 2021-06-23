from junctions.Intersection import Intersection
from roadgen.controlLine.ControlLineGrid import ControlLineGrid
from roadgen.controlLine.ControlLine import ControlLine
from roadgen.controlLine.ControlPointIntersectionAdapter import ControlPointIntersectionAdapter
from junctions.LaneSides import LaneSides
from junctions.RoadBuilder import RoadBuilder
from extensions.ExtendedRoad import ExtendedRoad
from junctions.ODRHelper import ODRHelper
from junctions.RoadLinker import RoadLinker
from junctions.LaneBuilder import LaneBuilder
from junctions.JunctionBuilderFromPointsAndHeading import JunctionBuilderFromPointsAndHeading
from extensions.CountryCodes import CountryCodes
import logging, math, pyodrx

class ControlLineBasedGenerator:


    def __init__(self, mapSize, debug=False, country=CountryCodes.US) -> None:
        self.name = "ControlLineBasedGenerator"
        self.mapSize = mapSize
        self.debug = debug
        self.lines = None
        self.pairs = None
        self.grid = None
        self.roadBuilder = RoadBuilder()
        self.laneBuilder = LaneBuilder()
        self.connectionRoads = []
        self.controlPointIntersectionMap = {} # controlpoint -> its intersection
        self.nextRoadId = 0
        self.odrList = []
        self.intersectionBuilder = JunctionBuilderFromPointsAndHeading(country=country,
                                                            laneWidth=3)
        pass



    
    def createGridWithHorizontalControlLines(self, nLines):

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

    
    def generateWithHorizontalControlines(self, name, nLines):

        self.createGridWithHorizontalControlLines(nLines)

        # create intersections for each control point

        # for each connection, find the pair of intersections, find the pair of controlpoints, create straight connection road.

        for (line1, line2, point1, point2) in self.grid.connections:

            if len(point1.adjacentPoints) < 3:
                # raise Exception(f"why less than 3 for point {point1.position}")
                print(f"why less than 3 for point {point1.position}")
                print(point1)
                # # skipping for now
                # continue

            if len(point2.adjacentPoints) < 3:
                # raise Exception(f"why less than 3 for point {point1.position}")
                print(f"why less than 3 for point {point2.position}")
                print(point2)
                # skipping for now
                # continue

            
            if point1 not in self.controlPointIntersectionMap and len(point1.adjacentPoints) > 2:
                point1.intersection = ControlPointIntersectionAdapter.createIntersection(self.intersectionBuilder, point1, self.nextRoadId)
                self.nextRoadId = point1.intersection.getLastRoadId() + 100
                point1.adjPointToOutsideIndex = ControlPointIntersectionAdapter.getAdjacentPointOutsideRoadIndexMap(point1, point1.intersection)
                self.controlPointIntersectionMap[point1] = point1.intersection
                self.odrList.append(point1.intersection.odr)
            if point2 not in self.controlPointIntersectionMap and len(point2.adjacentPoints) > 2:
                point2.intersection = ControlPointIntersectionAdapter.createIntersection(self.intersectionBuilder, point2, self.nextRoadId)
                self.nextRoadId = point2.intersection.getLastRoadId() + 100
                point2.adjPointToOutsideIndex = ControlPointIntersectionAdapter.getAdjacentPointOutsideRoadIndexMap(point2, point2.intersection)
                self.controlPointIntersectionMap[point2] = point2.intersection
                self.odrList.append(point2.intersection.odr)
        
        # now we have the intersections
        for (line1, line2, point1, point2) in self.grid.connections:
            if len(point1.adjacentPoints) < 3:
                # raise Exception(f"why less than 3 for point {point1.position}")
                # print(f"why less than 3 for point {point1.position}")
                # skipping for now
                continue

            if len(point2.adjacentPoints) < 3:
                # raise Exception(f"why less than 3 for point {point1.position}")
                # print(f"why less than 3 for point {point1.position}")
                # skipping for now
                continue

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

            # now we connect these incident roads.

            # we need to process point1 only
            # for adjP in point1.adjacentPointsCWOrder.values():
            #     point1IncidentIndex = point1.adjPointToOutsideIndex[adjP]
            #     point2IncidentIndex = ad
            

        
        combinedOdr = ODRHelper.combine(self.odrList, name)
        ODRHelper.addAdjustedRoads(combinedOdr, self.connectionRoads)
        return combinedOdr


    def reverseCP(self, cp):
         return pyodrx.ContactPoint.start if (cp == pyodrx.ContactPoint.end) else pyodrx.ContactPoint.end




    def connect(self, connectionRoadId, intersection1:Intersection, road1: ExtendedRoad, cp1, intersection2:Intersection, road2: ExtendedRoad, cp2, laneSides):


        if self.debug:
            logging.info(f"{self.name}: connecting intersections ({intersection1.id}, {intersection2.id})")


        connectionRoad = self.roadBuilder.getConnectionRoadBetween(connectionRoadId, road1, road2, cp1, cp2, isJunction=False, laneSides=laneSides)
        RoadLinker.createExtendedPredSuc(predRoad=road1, predCp=cp1, sucRoad=connectionRoad, sucCP=pyodrx.ContactPoint.start)
        RoadLinker.createExtendedPredSuc(predRoad=connectionRoad, predCp=pyodrx.ContactPoint.end, sucRoad=road2, sucCP=cp2)

        self.laneBuilder.createLanesForConnectionRoad(connectionRoad, road1, road2)

        x, y, h = road1.getPosition(cp1)
        ODRHelper.transformRoad(connectionRoad, x, y, h)
        connectionRoad.planview.adjust_geometires()

        # x2, y2, h2 = road2.getPosition(cp2)
        # print(x, y, h)
        # print(x2, y2, h2)
        


        self.connectionRoads.append(connectionRoad)
