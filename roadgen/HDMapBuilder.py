from roadgen.layout.MapBuilder import MapBuilder
from roadgen.layout.Grid import Grid
from roadgen.layout.IntersectionAdapter import IntersectionAdapter
from junctions.SequentialJunctionBuilder import SequentialJunctionBuilder
from library.Configuration import Configuration
from junctions.LaneConfiguration import LaneConfigurationStrategies
import pyodrx
import numpy as np
import logging
logging.basicConfig(level=logging.INFO, filename="hdmap-builder.log")


class HDMapBuilder:

    def __init__(self, nIntersections, p=[0.2, 0.7, 0.1, 0.1], startId=0, seed=0, debug=True) -> None:

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
        
        self.grid = Grid(size=(500, 500), cellSize=(100, 100))

        self.mapBuilder = MapBuilder(self.grid, [], random_seed=40)

        self.debug = debug

        pass


    def createIntersections(self):

        maxNumberOfRoadsPerJunction = 4
        maxLanePerSide = 1
        minLanePerSide = 1

        for sl in range(self.nIntersections):
            intersection = self.builder.createWithRandomLaneConfigurations("", 
                                sl, 
                                maxNumberOfRoadsPerJunction=maxNumberOfRoadsPerJunction, 
                                maxLanePerSide=maxLanePerSide, 
                                minLanePerSide=minLanePerSide, 
                                internalConnections=True, 
                                cp1=pyodrx.ContactPoint.end,
                                internalLinkStrategy = LaneConfigurationStrategies.SPLIT_ANY,
                                getAsOdr=False)
            directionIntersection = self.intersectionAdapter.intersectionTo4DirectionIntersection(intersection)
            self.intersections[directionIntersection] = intersection

        
    
    def buildMap(self):

        # 1 create intersections and direction intersections.
        self.createIntersections()
        self.mapBuilder.setDirectionIntersections(list(self.intersections.keys()))
        self.mapBuilder.run(self.nIntersections * 2)

