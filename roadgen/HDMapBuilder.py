from junctions.LaneSides import LaneSides
from roadgen.definitions.DirectionIntersection import DirectionIntersection
from roadgen.layout.MapBuilder import MapBuilder
from roadgen.layout.Grid import Grid
from roadgen.layout.IntersectionAdapter import IntersectionAdapter
from junctions.SequentialJunctionBuilder import SequentialJunctionBuilder
from junctions.IntersectionValidator import IntersectionValidator
from library.Configuration import Configuration
from junctions.LaneConfiguration import LaneConfigurationStrategies
from junctions.ODRHelper import ODRHelper
from roadgen.layout.Network import Network
from extensions.CountryCodes import CountryCodes
import pyodrx
import numpy as np
import logging


class HDMapBuilder:

    def __init__(self, 
        nIntersections, p=[0.2, 0.7, 0.1, 0.1], 
        startId=0, seed=0, 
        mapSize=(500, 500), cellSize=(100, 100), 
        countryCode=CountryCodes.US,
        debug=True) -> None:

        self.nIntersections = nIntersections
        self.p = p # probability distribution of 3-way, 4, 5, 6
        self.intersections = {} # DirectionIntersection -> intersection
        self.placedIntersections = {}
        self.rotation = {}
        self.nextIntersectionId = startId

        self.countryCode = countryCode
        
        self.seed = seed
        self.builder = SequentialJunctionBuilder(
                                                    minAngle=np.pi/6, 
                                                    maxAngle=np.pi * .75,
                                                    straightRoadLen=1, 
                                                    probLongConnection=0.3,
                                                    probMinAngle=0.1,
                                                    probRestrictedLane=0,
                                                    maxConnectionLength=30,
                                                    minConnectionLength=12,
                                                    random_seed=self.seed)

        self.moreThan4Builder = SequentialJunctionBuilder(
                                                    minAngle=np.pi/10, 
                                                    maxAngle=np.pi * .75,
                                                    straightRoadLen=1, 
                                                    probLongConnection=0.5,
                                                    probMinAngle=0.5,
                                                    probRestrictedLane=0,
                                                    maxConnectionLength=50,
                                                    minConnectionLength=20,
                                                    random_seed=self.seed)


        self.validator = IntersectionValidator()
        self.intersectionAdapter = IntersectionAdapter()
        
        self.grid = Grid(size=mapSize, cellSize=cellSize)

        self.mapBuilder = MapBuilder(self.grid, [], random_seed=40)

        self.network = None

        self.debug = debug

        self.name = "HDMapBuilder"

        self.nextRoadId = 0

        pass


    def createIntersections(self):

        print(f"{self.name}: createIntersections")
        minLanePerSide = 1
        maxLanePerSide = 2
        self.nextRoadId = 0
        for sl in range(self.nIntersections):
            print(f"{self.name}: creating {sl + 1}")
            maxNumberOfRoadsPerJunction = np.random.choice([3, 4, 5], p=[0.5, 0.475, 0.025])
            intersection = self.createValidIntersection(sl, self.nextRoadId, maxNumberOfRoadsPerJunction, minLanePerSide, maxLanePerSide)
            
            self.nextRoadId = intersection.getLastRoadId() + 100
            directionIntersection = self.intersectionAdapter.intersectionTo4DirectionIntersection(intersection)
            self.intersections[directionIntersection] = intersection

    
    def createValidIntersection(self, id, firstRoadId, maxNumberOfRoadsPerJunction, minLanePerSide, maxLanePerSide, rotate=False):

        isEqualAngle = np.random.choice([False, True], p=[0.5, 0.5])
        minConnectionLength = self.builder.minConnectionLength

        if maxNumberOfRoadsPerJunction < 5:
            intersection = self.builder.createWithRandomLaneConfigurations("", 
                                id, 
                                firstRoadId=firstRoadId,
                                maxNumberOfRoadsPerJunction=maxNumberOfRoadsPerJunction, 
                                maxLanePerSide=maxLanePerSide, 
                                minLanePerSide=minLanePerSide, 
                                internalConnections=True, 
                                cp1=pyodrx.ContactPoint.end,
                                internalLinkStrategy = LaneConfigurationStrategies.SPLIT_ANY,
                                equalAngles=isEqualAngle,
                                getAsOdr=False)
        else:
            minConnectionLength = self.moreThan4Builder.minConnectionLength
            intersection = self.moreThan4Builder.createWithRandomLaneConfigurations("", 
                                id, 
                                firstRoadId=firstRoadId,
                                maxNumberOfRoadsPerJunction=maxNumberOfRoadsPerJunction, 
                                maxLanePerSide=maxLanePerSide, 
                                minLanePerSide=minLanePerSide, 
                                internalConnections=True, 
                                cp1=pyodrx.ContactPoint.end,
                                internalLinkStrategy = LaneConfigurationStrategies.SPLIT_ANY,
                                equalAngles=isEqualAngle,
                                getAsOdr=False)

        while (self.validator.validateIncidentPoints(intersection, minConnectionLength) == False):
            intersection = self.createValidIntersection(id, self.nextRoadId, maxNumberOfRoadsPerJunction, minLanePerSide, maxLanePerSide)

        if rotate:
            # self.rotation[intersection] = np.random.uniform(0, np.pi/10)
            self.rotation[intersection] = np.random.choice([np.pi/2, np.pi, np.pi * 1.5])
            intersection.transform(startX=0, startY=0, heading=self.rotation[intersection])
            
        return intersection


    def connectIntersectionsByCellAdjacency(self):
        
        self.network = Network(self.placedIntersections)
        for cell in self.grid.cellGenerator():
            if isinstance(cell.element, DirectionIntersection):
                couldConnect = False
                DI1 = cell.element
                # We need to check right and top only as left and bottoms are traversed before.
                if DI1.top.hasRoads():
                    DI2 = self.grid.topElement(cell)
                    if DI2 is not None and isinstance(DI2, DirectionIntersection):
                        if DI2.bot.hasRoads():
                            # We have a connection
                            quad1 = DI1.top
                            quad2 = DI2.bot
                            self.connectDirectionQuadrants(DI1, DI2, quad1, quad2)
                            couldConnect = True
                if DI1.right.hasRoads():
                    DI2 = self.grid.rightElement(cell)
                    if DI2 is not None and isinstance(DI2, DirectionIntersection):
                        if DI2.left.hasRoads():
                            # We have a connection
                            quad1 = DI1.right
                            quad2 = DI2.left
                            self.connectDirectionQuadrants(DI1, DI2, quad1, quad2)
                            couldConnect = True
                # if couldConnect == False:
                #     self.network.clusters.append(set([self.placedIntersections[DI1]]))


    def connectDirectionQuadrants(self, DI1, DI2, quad1, quad2):
        intersection1 = self.placedIntersections[DI1]
        intersection2 = self.placedIntersections[DI2]
        road1 = list(quad1.roads.keys())[0]
        cp1 = list(quad1.roads.values())[0]
        road2 = list(quad2.roads.keys())[0]
        cp2 = list(quad2.roads.values())[0]

        self.network.connect(self.nextRoadId, intersection1, road1, cp1, intersection2, road2, cp2, LaneSides.BOTH)
        self.nextRoadId += 1


    
    def adjustIntersectionPositions(self):
        odrList = []
        for cell in self.grid.cellGenerator():
            if isinstance(cell.element, DirectionIntersection):
                directionIntersection = cell.element
                x, y = self.grid.getAbsCellPosition(cell)
                # introduceNoise = np.random.choice([False, True], p=[0.1, 0.9])
                introduceNoise = True
                if introduceNoise:
                    # x = np.random.uniform(x, x + (cell.size[0] / 2))
                    # y = np.random.uniform(y, y + (cell.size[1] / 2))
                    # x = x + self.grid.cellNoises[cell] * cell.size[0]
                    # y = y + self.grid.cellNoises[cell] * cell.size[1]

                    xfactor = np.random.uniform(0, 1)
                    yFactor = np.random.uniform(0, 1)
                    # xfactor = 1
                    # yFactor = 1
                    x = x + self.grid.cellNoises[cell] * xfactor
                    y = y + self.grid.cellNoises[cell] * yFactor

                intersection = self.intersections[directionIntersection]
                if self.debug:
                    logging.info(f"Translating {intersection.id} to ({x}, {y})")

                rotation = 0
                if intersection in self.rotation:
                    rotation = self.rotation[intersection]

                intersection.transform(startX=x, startY=y, heading=rotation)
                # ODRHelper.transform(intersection.odr, startX=x, startY=y, heading=rotation)
                self.placedIntersections[directionIntersection] = intersection

                odrList.append(intersection.odr)
        return odrList

    
    def buildMap(self, name, plot=True):

        # 1 create intersections and direction intersections.
        if self.debug:
            logging.info(f"{self.name}: Building new HDMap")
        self.createIntersections()
        self.mapBuilder.setDirectionIntersections(list(self.intersections.keys()))
        self.mapBuilder.run(self.nIntersections * 2, plot=plot)

        # now each cell in the grid has reference to the direction intersection 
        if self.debug:
            logging.info(f"{self.name}: adjustIntersectionPositions")
        odrList = self.adjustIntersectionPositions()

        self.connectIntersectionsByCellAdjacency()

        combinedOdr = ODRHelper.combine(odrList, name, self.countryCode)
        ODRHelper.addAdjustedRoads(combinedOdr, self.network.connectionRoads)

        if self.debug:
            logging.info(f"{self.name}: buildMap: number of clusters: {len(self.network.clusters)}")
            self.network.logClusters()
        return combinedOdr

