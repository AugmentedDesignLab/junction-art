import numpy as np
import os, math
import pyodrx 
import math
import dill
from junctions.RoadBuilder import RoadBuilder
from junctions.StandardCurvatures import StandardCurvature
from junctions.StandardCurveTypes import StandardCurveTypes
from junctions.JunctionMerger import JunctionMerger
import extensions
from junctions.moreExceptions import *
from junctions.AngleCurvatureMap import AngleCurvatureMap
import logging


class JunctionHarvester:

    def __init__(self, 
                outputDir, 
                outputPrefix, 
                lastId=0, 
                minAngle = np.pi / 10, 
                maxAngle = np.pi, 
                straightRoadLen = 10,
                esminiPath = "F:\\myProjects\\av\\esmini"):
        """The angle between two connected roads are >= self.minAngle <= self.maxAngle

        Args:
            outputDir ([type]): [description]
            outputPrefix ([type]): [description]
            lastId (int, optional): [description]. Defaults to 0.
            minAngle ([type], optional): [description]. Defaults to np.pi/10.
            maxAngle ([type], optional): [description]. Defaults to np.pi.
            straightRoadLen : used both for normal and connection roads
            esminiPath: Path to esmini to generate images for roads.
        """

        self.destinationPrefix = os.path.join(outputDir, outputPrefix)
        self.minAngle = minAngle
        self.maxAngle = maxAngle
        self.lastId = lastId
        self.straightRoadLen = straightRoadLen

        self.roadBuilder = RoadBuilder()

        self.junctionMerger = JunctionMerger(outputDir, outputPrefix, lastId)

        self.esminiPath = esminiPath

        if os.path.isdir(self.esminiPath) is False:
            logging.warn(f"Esmini path not found {self.esminiPath}. Will break if you try to save images using harvester.")

        pass


    

    def getOutputPath(self, fname):
        return self.destinationPrefix + fname + '.xodr'

    
    def createOdr(self, name, roads, junctions):
        
        odr = extensions.ExtendedOpenDrive(name)
        for r in roads:
            odr.add_road(r)
        
        for junction in junctions:
            odr.add_junction(junction)

        print(f"starting adjustment. May freeze!!!!!!!!!!!!!")
        odr.adjust_roads_and_lanes()

        return odr


    def harvest2ways2Lanes(self, stepAngle=np.pi/20, maxTries = 100, seed=39):
        """We create junctions of two roads. Will create at least one road per angle.

        Args:
            stepAngle ([type], optional): used to generate angles between roads in conjunction with min and max angles. Defaults to np.pi/20.
            maxTries (int, optional): maximum number of junctions will be maxTries. Defaults to 1000.
            seed (int, optional): defaults to 39
        """
        np.random.seed(seed)
        # for each angle
        countCreated = 0
        roadsPerAngle = self.getRoadsPerAngle(maxTries, stepAngle)

        angleBetweenRoads = self.minAngle 
        odrObjectsPerAngle = {} # we will save the odrs keyed by angles

        while (countCreated < maxTries and angleBetweenRoads < self.maxAngle ):

            odrObjects = self.randomSome2ways2Lanes(angleBetweenRoads, roadsPerAngle)
            odrObjectsPerAngle[str(angleBetweenRoads)] = odrObjects
            countCreated += roadsPerAngle
            angleBetweenRoads += stepAngle
        
        print(f"created {countCreated} roads")

        # Save the odrs

        with(open(self.destinationPrefix + "harvested2R2LOrds.dill", "wb")) as f:
            dill.dump(odrObjectsPerAngle, f)
            print("Odr objects saved to " + self.destinationPrefix + "harvested2R2LOrds.dill" )

        pass


    def getRoadsPerAngle(self, maxTries, stepAngle):
        roadsPerAngle = round((maxTries * stepAngle)/(self.maxAngle - self.minAngle))
        if roadsPerAngle == 0:
            roadsPerAngle = 1
        return roadsPerAngle

    
    def randomSome2ways2Lanes(self, angleBetweenRoads, numberOfRoads, saveImage=True):
        """Creates 2way junctions where the connected roads have fixed angle

        Args:
            angleBetweenRoads ([type]): The angle between the roads. The connecting road is a curve that ensures the angle is preserved.
            numberOfRoads ([type]): number of roads to be generated

        Returns:
            [type]: [description]
        """

        print( f"randomSome2ways2Lanes: creating {numberOfRoads} for angle: {math.degrees(angleBetweenRoads)}")
        odrObjects = []
        for i in range( numberOfRoads):
            odr = self.random2ways2Lanes(angleBetweenRoads)
            odrObjects.append(odr)

            # 1. save the xml file
            fname = "2R2L_" + str(round(math.degrees(angleBetweenRoads))) + "_no" + str(i)
            xmlPath = self.getOutputPath(fname)
            odr.write_xml(xmlPath)

            # 2. save image
            if saveImage is True:
                extensions.saveRoadImageFromFile(xmlPath, self.esminiPath)

        return odrObjects


    def random2ways2Lanes(self, angleBetweenRoads):
        # print( f"random2ways2Lanes: creating a road network for angle: {math.degrees(angleBetweenRoads)}")
        roads = []
        roads.append(pyodrx.create_straight_road(0, length=self.straightRoadLen)) # cannot reuse roads due to some references to links cannot be reinitialized with pyodrx lib.
        roads.append(self.createRandomConnectionConnectionRoad(1, angleBetweenRoads))
        roads.append(pyodrx.create_straight_road(2, length=self.straightRoadLen))

        self.link3RoadsWithMidAsJunction(roads)
        junction = self.create2RoadJunction(roads)

        self.lastId += 1

        odrName = 'R2_L2_' + str(self.lastId)
        odr = self.createOdr(odrName, roads, [junction])

        return odr


    def createRandomConnectionConnectionRoad(self, connectionRoadId, angleBetweenRoads):
        """The magic connectionRoad

        Args:
            angleBetweenRoads ([type]): The angle between the roads which this connectionRoad is suppose to connect together
            connectionRoadId ([type]): id to be assigned to the new connection road.
        """

        if angleBetweenRoads > 3.05: # when it's greater than 174 degrees, create a straight road
            return pyodrx.create_straight_road(connectionRoadId, length=self.straightRoadLen, junction=1)

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

    
    def connect2LaneRoads(self, incomingRoadId, connectionRoadId,):
        """Assumes no center lane offset.

        Args:
            incomingRoadId ([type]): [description]
            connectionRoadId ([type]): [description]
        """
        connection = pyodrx.Connection(incomingRoadId, connectionRoadId, pyodrx.ContactPoint.start)
        connection.add_lanelink(-1,-1)
        return connection

        
    def harvest3WayJunctionsFrom2Ways(self, ingredientsFile, maxTries = 100, randomizeAngleSelection = True):
        """Merges 2 way junctions into 3 ways.

        Args:
            ingredientsFile ([type]): [description]
            maxTries (int, optional): [description]. Defaults to 100.
            randomizeAngleSelection (bool, optional): If True it will pick 2R roads randomly without any angle filtering. If false, it will only connect 2R roads which have different angles. Defaults to True.

        Raises:
            NotImplementedError: [description]
        """
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
                try:
                    selectedOdrs = [odrList[np.random.choice(numberOfOds)], odrList[np.random.choice(numberOfOds)]]
                    newOdr = self.junctionMerger.merge2R2L(selectedOdrs)
                    generatedOdrs.append(newOdr)
                    self.lastId += 1

                except IncompatibleRoadsException:
                    continue
                
        else: 
            # TODO angle permutation for merging 2ways
            raise NotImplementedError("Angle permutation is not implemented yet")

    
        
        with(open(self.destinationPrefix + "harvested3R2LOrds.dill", "wb")) as f:
            dill.dump(generatedOdrs, f)
            print("Odr objects saved to " + self.destinationPrefix + "_harvested3R2LOrds.dill" )

        pass 


    def harvestByPainting2L(self, maxNumberOfRoadsPerJunction, triesPerRoadCount, save=True, saveImage=True):
        """[summary]

        Args:
            maxNumberOfRoadsPerJunction ([type]): [description]
            triesPerRoadCount ([type]): number of junctions to be created for each set of roads.
            save (bool, optional): [description]. Defaults to True.
            saveImage (bool, optional): [description]. Defaults to True.
        """

        
        for numRoads in range(3, maxNumberOfRoadsPerJunction + 1):
            for _ in range(triesPerRoadCount):
               self.drawLikeAPainter2L(numRoads)
               self.lastId += 1

        pass

    

    def drawLikeAPainter2L(self, maxNumberOfRoadsPerJunction, save=True, saveImage=True):
        if maxNumberOfRoadsPerJunction < 3:
            raise Exception("drawLikeAPainter is not for the weak. Please add more than 3 roads")

        roads = []
        roads.append(pyodrx.create_straight_road(0, length=self.straightRoadLen * 4)) # first road

        availableAngle = 1.8 * np.pi # 360 degrees
        maxAnglePerConnection = availableAngle / (maxNumberOfRoadsPerJunction - 1)
        action = self.actionAfterDrawingOne(roads, availableAngle, maxNumberOfRoadsPerJunction)
        nextRoadId = 1
        while (action != "end"):

            print(f"availableAngle {math.degrees(availableAngle)}, number of roads: {len(roads) / 2}")
            previousRoadId = nextRoadId - 1
            newConnectionId = nextRoadId
            nextRoadId += 1
            newRoadId = nextRoadId
            nextRoadId += 1

            # 1. create a road
            newRoad = pyodrx.create_straight_road(newRoadId, self.straightRoadLen)

            # 2. create a new connection road
            newConnection, availableAngle = self.createNewConnectionForDrawing(action, newConnectionId, availableAngle, maxAnglePerConnection)
            
            # 5 add new roads and increase road id
            roads.append(newConnection)
            roads.append(newRoad)

            roads[previousRoadId].add_successor(pyodrx.ElementType.junction, newConnection.id)

            if newConnection.id == 1:
                newConnection.add_predecessor(pyodrx.ElementType.road, previousRoadId, pyodrx.ContactPoint.end)
            else:
                newConnection.add_predecessor(pyodrx.ElementType.road, previousRoadId, pyodrx.ContactPoint.start)
            
            newConnection.add_successor(pyodrx.ElementType.road, newRoad.id, pyodrx.ContactPoint.start) 
            newRoad.add_predecessor(pyodrx.ElementType.junction, newConnection.id)


            # 6 get next action
            action = self.actionAfterDrawingOne(roads, availableAngle, maxNumberOfRoadsPerJunction)
            pass
        
        # 3. create connections and junction
        # trying with their function

        junction = self.createJunctionForASeriesOfRoads(roads)

        print(f"number of roads created {len(roads)}")
        odrName = 'Draw_Rmax' + str(maxNumberOfRoadsPerJunction) + '_L2_' + str(self.lastId)
        odr = self.createOdr(odrName, roads, [junction])

        # The last connection and resetting odr

        lastConnection = self.createLastConnectionForLastAndFirstRoad(nextRoadId, roads, junction)
        odr.add_road(lastConnection)

        # odr.reset()
        # odr.add_road(lastConnection)
        # odr.adjust_roads_and_lanes()

        odr.resetAndReadjust()
        

        xmlPath = self.getOutputPath(odr.name)
        if save:
            odr.write_xml(xmlPath)

        if saveImage:
            extensions.saveRoadImageFromFile(xmlPath, self.esminiPath)

        return odr




    def createLastConnectionForLastAndFirstRoad(self, nextRoadId, roads, junction):

        lastConnectionId = nextRoadId + 100
        lastConnection = self.roadBuilder.getConnectionRoadBetween(lastConnectionId, roads[0], roads[-1], pyodrx.ContactPoint.end, pyodrx.ContactPoint.start)
        lastConnection.add_predecessor(pyodrx.ElementType.road, roads[-1].id, pyodrx.ContactPoint.start)
        lastConnection.add_successor(pyodrx.ElementType.road, roads[0].id, pyodrx.ContactPoint.end)

        roads[-1].add_successor(pyodrx.ElementType.junction, lastConnectionId, pyodrx.ContactPoint.start) 
        roads[0].add_predecessor(pyodrx.ElementType.junction, lastConnectionId, pyodrx.ContactPoint.end) 


        connectionL = pyodrx.Connection(roads[-1].id, lastConnectionId, pyodrx.ContactPoint.start)
        connectionL.add_lanelink(-1,-1)
        junction.add_connection(connectionL)
        
        roads.append(lastConnection)

        return lastConnection

    def createNewConnectionForDrawing(self, action, newConnectionId, availableAngle, maxAnglePerConnection):

        newConnection = None
        newConnection, availableAngle = self.createCurveForDrawing(availableAngle, maxAnglePerConnection, newConnectionId, curveType= StandardCurveTypes.LongArc)
        return newConnection, availableAngle
        # if action is 'straightLine':
        #     newConnection = pyodrx.create_straight_road(newConnectionId, self.straightRoadLen, junction=1)
        #     availableAngle -= np.pi
        # elif action is 'curve':
        #     newConnection, availableAngle = self.createCurveForDrawing(availableAngle, maxAnglePerConnection, newConnectionId, curveType= StandardCurveTypes.LongArc)
        # elif action is 'spiral':
        #     newConnection, availableAngle = self.createCurveForDrawing(availableAngle,maxAnglePerConnection,  newConnectionId, curveType= StandardCurveTypes.Simple)
        # elif action is 's':
        #     newConnection, availableAngle = self.createCurveForDrawing(availableAngle, maxAnglePerConnection, newConnectionId, curveType= StandardCurveTypes.S)

        # return newConnection, availableAngle


    def createCurveForDrawing(self, availableAngle, maxAnglePerConnection, newConnectionId, curveType):
        angleBetweenEndpoints = self.getSomeAngle(availableAngle, maxAnglePerConnection)
        availableAngle -= angleBetweenEndpoints
        # curvature = StandardCurvature.getRandomValue()
        curvature = AngleCurvatureMap.getCurvatureForJunction(angleBetweenEndpoints)

        print(f"Curvature for angle {math.degrees(angleBetweenEndpoints)} is {curvature}")
        # if curvature < StandardCurvature.Medium.value:
        #     curvature = StandardCurvature.Medium.value

        newConnection = self.roadBuilder.createCurve(newConnectionId, angleBetweenEndpoints, isJunction=True, curvature=curvature, curveType=curveType)
        return newConnection, availableAngle


    def createJunctionForASeriesOfRoads(self, roads):
        """[summary]

        Args:
            roads ([type]): even indices are roads, odd indices are connection roads  of the junction

        Returns:
            [type]: [description]
        """

        junction = pyodrx.Junction("spiderJunction", 0)

        connectionId = 1

        while (connectionId < len(roads)):

            print(f"connecting roads {connectionId-1} {connectionId}")
            connectionL = pyodrx.Connection(connectionId-1, connectionId, pyodrx.ContactPoint.start)
            connectionL.add_lanelink(-1,-1)

            # if (connectionId + 1) < len(roads):
            #     connectionR = pyodrx.Connection(connectionId+1, connectionId, pyodrx.ContactPoint.end)
            # else:
            #     connectionR = pyodrx.Connection(0, connectionId, pyodrx.ContactPoint.end)

            # connectionR.add_lanelink(1,1)

            junction.add_connection(connectionL)
            # junction.add_connection(connectionR)

            connectionId += 2
        
        return junction


    def getSomeAngle(self, availableAngle, maxAnglePerConnection):

        angle = (availableAngle * np.random.choice(10)) / 9

        
        if angle < self.minAngle:
            angle = self.minAngle

        if angle > maxAnglePerConnection:
            angle = maxAnglePerConnection
        return angle

    
    def actionAfterDrawingOne(self, currentRoads, availableAngle, maxNumberOfRoads):


        actions = ['straightLine', "curve", "spiral", "s"]
        
        if availableAngle < self.minAngle:
            return "end"
        
        if len(currentRoads) >= (maxNumberOfRoads * 2 - 1): # dont count connection roads
            return "end"
        
        return actions[np.random.choice(len(actions))]


