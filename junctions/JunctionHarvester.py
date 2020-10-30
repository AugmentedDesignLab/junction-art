import numpy as np
import os
import pyodrx 
import math
import dill
from junctions.RoadBuilder import RoadBuilder
from junctions.StandardCurvatures import StandardCurvature
from junctions.StandardCurveTypes import StandardCurveTypes
from junctions.JunctionMerger import JunctionMerger
import extensions


class JunctionHarvester:

    def __init__(self, outputDir, outputPrefix, lastId=0, minAngle = np.pi / 10, maxAngle = np.pi):
        """The angle between two connected roads are >= self.minAngle <= self.maxAngle

        Args:
            outputDir ([type]): [description]
            outputPrefix ([type]): [description]
            lastId (int, optional): [description]. Defaults to 0.
            minAngle ([type], optional): [description]. Defaults to np.pi/10.
            maxAngle ([type], optional): [description]. Defaults to np.pi.
        """

        self.destinationPrefix = os.path.join(outputDir, outputPrefix)
        self.minAngle = minAngle
        self.maxAngle = maxAngle
        self.lastId = lastId

        self.roadBuilder = RoadBuilder()

        self.junctionMerger = JunctionMerger(outputDir, outputPrefix, lastId)

        pass


    

    def getOutputPath(self, fname):
        return self.destinationPrefix + fname + '.xodr'

    

    def harvest2ways2Lanes(self, stepAngle=np.pi/20, maxTries = 100, seed=39):
        """We create junctions of two roads. Will create at least one road per angle.

        Args:
            stepAngle ([type], optional): used to generate angles between roads in conjunction with min and max angles. Defaults to np.pi/20.
            maxTries (int, optional): maximum number of junctions will be maxTries. Defaults to 1000.
            seed (int, optional): defaults to 39
        """
        np.random.seed(seed)
        # for each angle
        tries = 0
        roadsPerAngle = round((maxTries * stepAngle)/(self.maxAngle - self.minAngle))
        if roadsPerAngle == 0:
            roadsPerAngle = 1

        angleBetweenRoads = self.minAngle 
        odrObjectsPerAngle = {}
        while (tries < maxTries and angleBetweenRoads < self.maxAngle ):

            odrObjects = self.randomSome2ways2Lanes(angleBetweenRoads, roadsPerAngle)
            odrObjectsPerAngle[str(angleBetweenRoads)] = odrObjects
            tries += roadsPerAngle
            angleBetweenRoads += stepAngle
        
        print(f"created {tries} roads")

        with(open(self.destinationPrefix + "harvested2R2LOrds.dill", "wb")) as f:
            dill.dump(odrObjectsPerAngle, f)
            print("Odr objects saved to " + self.destinationPrefix + "harvested2R2LOrds.dill" )

        pass

    
    def randomSome2ways2Lanes(self, angleBetweenRoads, roadsPerAngle):

        print( f"randomSome2ways2Lanes: creating {roadsPerAngle} for angle: {math.degrees(angleBetweenRoads)}")
        odrObjects = []
        for i in range( roadsPerAngle):
            odr = self.random2ways2Lanes(angleBetweenRoads)
            fname = "road2lane2angle" + str(round(math.degrees(angleBetweenRoads))) + "no" + str(i)
            odr.write_xml(self.getOutputPath(fname))
            odrObjects.append(odr)

        return odrObjects


    def random2ways2Lanes(self, angleBetweenRoads):
        # print( f"random2ways2Lanes: creating a road network for angle: {math.degrees(angleBetweenRoads)}")
        roads = []
        roads.append(pyodrx.create_straight_road(0)) # cannot reuse roads due to some references to links cannot be reinitialized with pyodrx lib.
        roads.append(self.createRandomConnectionConnectionRoad(1, angleBetweenRoads))
        roads.append(pyodrx.create_straight_road(2))

        self.link3RoadsWithMidAsJunction(roads)
        junction = self.create2RoadJunction(roads)

        self.lastId += 1
        odr = pyodrx.OpenDrive('R2_L2_' + str(self.lastId))
        for r in roads:
            odr.add_road(r)
        
        
        odr.add_junction(junction)
        print(f"starting adjustment. May freeze!!!!!!!!!!!!!")
        odr.adjust_roads_and_lanes()
        # print("adjustment done, didn't freeze!!!!!!!!!")

        return odr


    def createRandomConnectionConnectionRoad(self, connectionRoadId, angleBetweenRoads):
        """The magic connectionRoad

        Args:
            angleBetweenRoads ([type]): The angle between the roads which this connectionRoad is suppose to connect together
            connectionRoadId ([type]): id to be assigned to the new connection road.
        """

        if round(angleBetweenRoads) == round(np.pi): # when it's greater than 171.89 degrees, create a straight road
            return pyodrx.create_straight_road(connectionRoadId, length=10, junction=1)

        connectionRoad = self.roadBuilder.createRandomCurve(connectionRoadId, angleBetweenRoads, isJunction=True)
        return connectionRoad


    def link3RoadsWithMidAsJunction(self, roads):
        roads[0].add_successor(pyodrx.ElementType.junction,1, pyodrx.ContactPoint.start)
        self.linkInsideRoad(roads[1], 0, 2)
        roads[2].add_predecessor(pyodrx.ElementType.junction,1, pyodrx.ContactPoint.end)


    def linkInsideRoad(self, connectionRoad, predecessorId, successorId):
        connectionRoad.add_predecessor(pyodrx.ElementType.road, predecessorId, pyodrx.ContactPoint.end)
        connectionRoad.add_successor(pyodrx.ElementType.road, successorId, pyodrx.ContactPoint.start)

        pass

    def create2RoadJunction(self, roads):
        """[summary]

        Args:
            roads ([type]): 3 roads with mid as the junction type.
        """

        connection = self.connect2LaneRoads(0, 1)
        junction = pyodrx.Junction('test',1)
        junction.add_connection(connection)

        return junction

    
    def connect2LaneRoads(self, incomingRoadId, connectionRoadId):
        """Assumes no center lane offset.

        Args:
            incomingRoadId ([type]): [description]
            connectionRoadId ([type]): [description]
        """
        connection = pyodrx.Connection(incomingRoadId, connectionRoadId, pyodrx.ContactPoint.start)
        connection.add_lanelink(-1,-1)
        return connection

        
    def harvest3WayJunctionsFrom2Ways(self, ingredientsFile, maxTries = 100, randomizeAngleSelection = True):
        with(open(ingredientsFile, 'rb')) as f:
            odrDic = dill.load(f)

        selectedOdrs = None
        generatedOdrs = []
        if randomizeAngleSelection:
            odrList = []
            for angleOdrList in odrDic.values():
                odrList += angleOdrList

            numberOfOds = len(odrList)

            for _ in range(maxTries):
                selectedOdrs = [odrList[np.random.choice(numberOfOds)], odrList[np.random.choice(numberOfOds)]]
                newOdr = self.junctionMerger.merge2R2L(selectedOdrs)
                generatedOdrs.append(newOdr)
                
        else: 
            # TODO angle permutation for merging 2ways
            raise NotImplementedError("Angle permutation is not implemented yet")

    
        
        with(open(self.destinationPrefix + "harvested3R2LOrds.dill", "wb")) as f:
            dill.dump(generatedOdrs, f)
            print("Odr objects saved to " + self.destinationPrefix + "_harvested3R2LOrds.dill" )

        pass 



