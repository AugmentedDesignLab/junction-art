from roadgen.definitions.DirectionIntersection import DirectionIntersection
from roadgen.layout.MapBuilder import MapBuilder
from roadgen.layout.Grid import Grid
from roadgen.layout.IntersectionAdapter import IntersectionAdapter
from junctions.SequentialJunctionBuilder import SequentialJunctionBuilder
from library.Configuration import Configuration
from junctions.LaneConfiguration import LaneConfigurationStrategies
from junctions.ODRHelper import ODRHelper
import pyodrx
import numpy as np
import logging


class HDMapBuilder:

    def __init__(self, nIntersections, p=[0.2, 0.7, 0.1, 0.1], startId=0, seed=0, mapSize=(500, 500), cellSize=(100, 100), debug=True) -> None:

        self.nIntersections = nIntersections
        self.p = p # probability distribution of 3-way, 4, 5, 6
        self.intersections = {} # DirectionIntersection -> intersection
        self.nextIntersectionId = startId
        
        self.seed = seed
        self.builder = SequentialJunctionBuilder(
                                                    minAngle=np.pi/4, 
                                                    maxAngle=np.pi * .75,
                                                    straightRoadLen=5, 
                                                    probLongConnection=0.5,
                                                    probMinAngle=0.5,
                                                    probRestrictedLane=0.2,
                                                    maxConnectionLength=30,
                                                    minConnectionLength=12,
                                                    random_seed=self.seed)
        self.intersectionAdapter = IntersectionAdapter()
        
        self.grid = Grid(size=mapSize, cellSize=cellSize)

        self.mapBuilder = MapBuilder(self.grid, [], random_seed=40)

        self.debug = debug

        self.name = "HDMapBuilder"

        pass


    def createIntersections(self):

        maxNumberOfRoadsPerJunction = 4
        maxLanePerSide = 1
        minLanePerSide = 1
        startId = 0
        for sl in range(self.nIntersections):
            intersection = self.builder.createWithRandomLaneConfigurations("", 
                                sl, 
                                firstRoadId=startId,
                                maxNumberOfRoadsPerJunction=maxNumberOfRoadsPerJunction, 
                                maxLanePerSide=maxLanePerSide, 
                                minLanePerSide=minLanePerSide, 
                                internalConnections=True, 
                                cp1=pyodrx.ContactPoint.end,
                                internalLinkStrategy = LaneConfigurationStrategies.SPLIT_ANY,
                                getAsOdr=False)
            startId = intersection.getLastRoadId() + 100
            directionIntersection = self.intersectionAdapter.intersectionTo4DirectionIntersection(intersection)
            self.intersections[directionIntersection] = intersection

    
    def adjustIntersectionPositions(self):
        odrList = []
        for cell in self.grid.cellGenerator():
            if isinstance(cell.element, DirectionIntersection):
                directionIntersection = cell.element
                x, y = self.grid.getAbsCellPosition(cell)
                intersection = self.intersections[directionIntersection]
                if self.debug:
                    logging.info(f"Transforming {intersection.id} to ({x}, {y})")
                ODRHelper.transform(intersection.odr, startX=x, startY=y)
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
        combinedOdr = ODRHelper.combine(odrList, name)
        return combinedOdr

