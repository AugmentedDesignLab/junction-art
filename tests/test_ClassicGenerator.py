import pyodrx as pyodrx
from junctionart.extensions.CountryCodes import CountryCodes
import unittest
from junctionart.library.Configuration import Configuration
# )
import junctionart.extensions as extensions, os
import math
from junctionart.roundabout.ClassicGenerator import ClassicGenerator
# test
from junctionart.junctions.JunctionBuilder import JunctionBuilder
from junctionart.junctions.LaneBuilder import LaneBuilder
from junctionart.junctions.CurveRoadBuilder import CurveRoadBuilder
from junctionart.junctions.StandardCurvatures import StandardCurvature
from junctionart.junctions.RoadBuilder import RoadBuilder
from junctionart.junctions.StraightRoadBuilder import StraightRoadBuilder
from junctionart.junctions.RoadLinker import RoadLinker
from junctionart.junctions.ODRHelper import ODRHelper
import numpy as np
import random


class test_ClassicGenerator(unittest.TestCase):
    def setUp(self):
        self.configuration = Configuration()

        self.builder = ClassicGenerator(country=CountryCodes.US, laneWidth=3)

        # test
        self.straightbuilder = StraightRoadBuilder()
        self.junctionBuilder = JunctionBuilder()
        self.laneBuilder = LaneBuilder()
        self.curveBuilder = CurveRoadBuilder()
        self.roadBuilder = RoadBuilder()
        pass

    def test_createRoundAboutFromIncidentPoints(self):

        threePoints = [
            {"x": 80, "y": 20, "heading": math.radians(0)},
            {"x": 210, "y": 20, "heading": math.radians(135)},
            {"x": 100, "y": 100, "heading": math.radians(370)},
            {"x": 160, "y": -50, "heading": math.radians(90)},
        ]
        odr = self.builder.generateWithIncidentPointConfiguration(
            ipConfig=threePoints
        )
        extensions.printRoadPositions(odr)
        extensions.view_road(
            odr, os.path.join("..", self.configuration.get("esminipath"))
        )
    
    def test_assignment1(self):

        road1 = self.straightbuilder.createRandom(
            roadId=1, minLanePerSide=2, maxLanePerSide=2
        )
        road2 = self.curveBuilder.create(
            2, angleBetweenEndpoints=np.pi / 3, n_lanes=4, curvature=0.1
        )

        road3 = self.straightbuilder.createRandom(
            roadId=3, minLanePerSide=2, maxLanePerSide=2
        )
        road4 = self.curveBuilder.create(
            4, angleBetweenEndpoints=-np.pi / 3, n_lanes=4, curvature=0.1
        )
        road5 = self.straightbuilder.createRandom(
            roadId=5, minLanePerSide=2, maxLanePerSide=2
        )
        road6 = self.curveBuilder.create(
            6, angleBetweenEndpoints=-np.pi / 3, n_lanes=4, curvature=0.1
        )

        # define successor predecessor relationships
        RoadLinker.createExtendedPredSuc(
            predRoad=road1,
            predCp=pyodrx.ContactPoint.end,
            sucRoad=road2,
            sucCP=pyodrx.ContactPoint.start,
        )
        RoadLinker.createExtendedPredSuc(
            predRoad=road2,
            predCp=pyodrx.ContactPoint.end,
            sucRoad=road3,
            sucCP=pyodrx.ContactPoint.start,
        )
        RoadLinker.createExtendedPredSuc(
            predRoad=road3,
            predCp=pyodrx.ContactPoint.end,
            sucRoad=road4,
            sucCP=pyodrx.ContactPoint.start,
        )
        RoadLinker.createExtendedPredSuc(
            predRoad=road4,
            predCp=pyodrx.ContactPoint.end,
            sucRoad=road5,
            sucCP=pyodrx.ContactPoint.start,
        )
        RoadLinker.createExtendedPredSuc(
            predRoad=road5,
            predCp=pyodrx.ContactPoint.end,
            sucRoad=road6,
            sucCP=pyodrx.ContactPoint.start,
        )
        self.laneBuilder.createLanesForConnectionRoad(road2, road1, road3)
        self.laneBuilder.createLanesForConnectionRoad(road3, road2, road4)
        self.laneBuilder.createLanesForConnectionRoad(road4, road3, road5)
        self.laneBuilder.createLanesForConnectionRoad(road5, road4, road6)
        # roads = [road1, road2]
        roads = [road1, road2, road3, road4, road5, road6]

        # 3. place the roads into a map
        odr = extensions.createOdrByPredecessor(
            "First simple road network with one straight road only", roads, [], CountryCodes.US
        )

        xmlPath = f"output/test_assignment1.xodr"
        odr.write_xml(xmlPath)

        extensions.view_road(
            odr, os.path.join("..", self.configuration.get("esminipath"))
        )

    def test_assignment2(self):

        road1 = self.curveBuilder.create(
            roadId=1, angleBetweenEndpoints=np.pi / 2, n_lanes=2
        )
        road2 = self.straightbuilder.createRandom(
            roadId=2, minLanePerSide=2, maxLanePerSide=2, length=50
        )
        # road2 = self.curveBuilder.createCurveByLength(2, length=20, curvature=StandardCurvature.Sharp.value)
        road3 = self.curveBuilder.create(
            3, angleBetweenEndpoints=-np.pi / 3, n_lanes=4, curvature=0.1
        )

        road4 = self.curveBuilder.create(
            4, angleBetweenEndpoints=-np.pi / 3, n_lanes=4, curvature=0.1
        )
        road5 = self.curveBuilder.create(
            5, angleBetweenEndpoints=np.pi / 2, n_lanes=4, curvature=0.08
        )
        road6 = self.straightbuilder.createRandom(
            roadId=6, minLanePerSide=2, maxLanePerSide=2, length=50
        )

        # define successor predecessor relationships
        RoadLinker.createExtendedPredSuc(
            predRoad=road1,
            predCp=pyodrx.ContactPoint.end,
            sucRoad=road2,
            sucCP=pyodrx.ContactPoint.start,
        )
        RoadLinker.createExtendedPredSuc(
            predRoad=road2,
            predCp=pyodrx.ContactPoint.end,
            sucRoad=road3,
            sucCP=pyodrx.ContactPoint.start,
        )
        RoadLinker.createExtendedPredSuc(
            predRoad=road3,
            predCp=pyodrx.ContactPoint.end,
            sucRoad=road4,
            sucCP=pyodrx.ContactPoint.start,
        )
        RoadLinker.createExtendedPredSuc(
            predRoad=road4,
            predCp=pyodrx.ContactPoint.end,
            sucRoad=road5,
            sucCP=pyodrx.ContactPoint.start,
        )
        RoadLinker.createExtendedPredSuc(
            predRoad=road5,
            predCp=pyodrx.ContactPoint.end,
            sucRoad=road6,
            sucCP=pyodrx.ContactPoint.start,
        )
        self.laneBuilder.createLanesForConnectionRoad(road2, road1, road3)
        self.laneBuilder.createLanesForConnectionRoad(road3, road2, road4)
        self.laneBuilder.createLanesForConnectionRoad(road4, road3, road5)
        self.laneBuilder.createLanesForConnectionRoad(road5, road4, road6)
        # roads = [road1, road2]
        roads = [road1, road2, road3, road4, road5, road6]

        # 3. place the roads into a map
        odr = extensions.createOdrByPredecessor(
            "First simple road network with one straight road only", roads, [], CountryCodes.US
        )

        xmlPath = f"output/test_assignment1.xodr"
        odr.write_xml(xmlPath)

        extensions.view_road(
            odr, os.path.join("..", self.configuration.get("esminipath"))
        )

    def test_roundabout(self):
        road1 = self.straightbuilder.createRandom(
            roadId=1, minLanePerSide=1, maxLanePerSide=1, length=30
        )
        road2 = self.curveBuilder.create(
            2, angleBetweenEndpoints=np.pi / 1.5, n_lanes=1, curvature=0.07
        )
        road3 = self.curveBuilder.create(
            3, angleBetweenEndpoints=-np.pi / 1.5, n_lanes=1, curvature=0.07
        )

        road4 = self.curveBuilder.create(
            4, angleBetweenEndpoints=np.pi / 3, n_lanes=1, curvature=0.05
        )

        road5 = self.curveBuilder.create(
            5, angleBetweenEndpoints=np.pi / 3, n_lanes=1, curvature=0.05
        )

        RoadLinker.createExtendedPredSuc(
            predRoad=road1,
            predCp=pyodrx.ContactPoint.end,
            sucRoad=road2,
            sucCP=pyodrx.ContactPoint.start,
        )
        RoadLinker.createExtendedPredSuc(
            predRoad=road1,
            predCp=pyodrx.ContactPoint.end,
            sucRoad=road3,
            sucCP=pyodrx.ContactPoint.start,
        )
        RoadLinker.createExtendedPredSuc(
            predRoad=road3,
            predCp=pyodrx.ContactPoint.end,
            sucRoad=road4,
            sucCP=pyodrx.ContactPoint.start,
        )
        RoadLinker.createExtendedPredSuc(
            predRoad=road4,
            predCp=pyodrx.ContactPoint.end,
            sucRoad=road5,
            sucCP=pyodrx.ContactPoint.start,
        )

        roads = [road1, road2, road3, road4, road5]

        odr = extensions.createOdrByPredecessor(
            "First simple road network with one straight road only", roads, [], CountryCodes.US
        )


        road7 = self.roadBuilder.getConnectionRoadBetween(
            7,
            road1=road5,
            road2=road2,
            cp1=pyodrx.ContactPoint.end,
            cp2=pyodrx.ContactPoint.end,
        )

        
        RoadLinker.createExtendedPredSuc(
            predRoad=road5,
            predCp=pyodrx.ContactPoint.end,
            sucRoad=road7,
            sucCP=pyodrx.ContactPoint.start,
        )
        RoadLinker.createExtendedPredSuc(
            predRoad=road7,
            predCp=pyodrx.ContactPoint.end,
            sucRoad=road2,
            sucCP=pyodrx.ContactPoint.end,
        )

        roads.append(road7)

        odr.updateRoads(roads)
        odr.resetAndReadjust(byPredecessor=True)

        road6 = self.roadBuilder.getConnectionRoadBetween(
            6,
            road1=road7,
            road2=road4,
            cp1=pyodrx.ContactPoint.end,
            cp2=pyodrx.ContactPoint.start,
        )
        RoadLinker.createExtendedPredSuc(
            predRoad=road7,
            predCp=pyodrx.ContactPoint.end,
            sucRoad=road6,
            sucCP=pyodrx.ContactPoint.start,
        )
        RoadLinker.createExtendedPredSuc(
            predRoad=road6,
            predCp=pyodrx.ContactPoint.end,
            sucRoad=road4,
            sucCP=pyodrx.ContactPoint.start,
        )
        roads.append(road6)
        odr.updateRoads(roads)
        odr.resetAndReadjust(byPredecessor=True)
        xmlPath = f"output/test_assignment1.xodr"
        odr.write_xml(xmlPath)

        extensions.view_road(
            odr, os.path.join("..", self.configuration.get("esminipath"))
        )

    def test_MakeRandomCircularRoad(self):
        nRoads = random.randint(12, 80)
        radius = 44#random.randint(20, 30)
        incidentRoadEvery = random.randint(4, 12)
        nRoads = 16
        incidentRoadEvery = 4
        roadCurvature = 1 / radius
        roadLength = 2 * np.pi * radius / nRoads
        firstRoad = self.curveBuilder.createCurveByLength(
            roadId=1, length=roadLength, curvature=roadCurvature
        )

        previousRoad = firstRoad
        roads = []
        choseRoad = []
        straightRoads = []
        curveRoads = []
        roads.append(previousRoad)
        curveRoads.append(previousRoad)
        roadCount = 2
        for roadId in range(2, nRoads + 1):
            currentRoad = self.curveBuilder.createCurveByLength(
                roadId=roadCount, length=roadLength, curvature=roadCurvature
            )
            
            curveRoads.append(currentRoad)
            roadCount += 1
            RoadLinker.createExtendedPredSuc(
                predRoad=previousRoad,
                predCp=pyodrx.ContactPoint.end,
                sucRoad=currentRoad,
                sucCP=pyodrx.ContactPoint.start,
            )
            roads.append(currentRoad)
            previousRoad = currentRoad
            if roadId % incidentRoadEvery != 2:
                continue

            if random.randint(0, 1) == 0:
                choseRoad.append(False)
                straightRoads.append(0)
                continue

            choseRoad.append(True)
            road = self.curveBuilder.create(
                roadCount,
                angleBetweenEndpoints=-np.pi / 1.8,
                n_lanes=1,
                curvature=5 * roadCurvature,
            )
            roadCount += 1
            straightRoad = self.straightbuilder.createRandom(
                roadId=roadCount, minLanePerSide=1, maxLanePerSide=1, length=40
            )
            roadCount += 1
            RoadLinker.createExtendedPredSuc(
                predRoad=previousRoad,
                predCp=pyodrx.ContactPoint.end,
                sucRoad=road,
                sucCP=pyodrx.ContactPoint.start,
            )
            RoadLinker.createExtendedPredSuc(
                predRoad=road,
                predCp=pyodrx.ContactPoint.end,
                sucRoad=straightRoad,
                sucCP=pyodrx.ContactPoint.start,
            )
            roads.append(road)
            roads.append(straightRoad)
            straightRoads.append(straightRoad)

        odr = extensions.createOdrByPredecessor(
            "First simple road network with one straight road only", roads, [], CountryCodes.US
        )

        for roadId in range(len(straightRoads)):
            if choseRoad[roadId] == False:
                continue

            road2Id = incidentRoadEvery * roadId + 7 * nRoads // 35
            if road2Id >= len(curveRoads):
                road2Id = road2Id - len(curveRoads)
            connectionRoad = self.roadBuilder.getConnectionRoadBetween(
                newRoadId=roadCount,
                road1=straightRoads[roadId],
                road2=curveRoads[road2Id],
                cp1=pyodrx.ContactPoint.start,
                cp2=pyodrx.ContactPoint.start,
            )
            roadCount += 1
            RoadLinker.createExtendedPredSuc(
                predRoad=straightRoads[roadId],
                predCp=pyodrx.ContactPoint.start,
                sucRoad=connectionRoad,
                sucCP=pyodrx.ContactPoint.start,
            )
            RoadLinker.createExtendedPredSuc(
                predRoad=connectionRoad,
                predCp=pyodrx.ContactPoint.end,
                sucRoad=curveRoads[road2Id],
                sucCP=pyodrx.ContactPoint.start,
            )
            roads.append(connectionRoad)

        odr.updateRoads(roads)
        odr.resetAndReadjust(byPredecessor=True)
        connectionRoad = self.roadBuilder.getConnectionRoadBetween(
            newRoadId=roadCount,
            road1=roads[0],
            road2=roads[-1],
            cp1=pyodrx.ContactPoint.start,
            cp2=pyodrx.ContactPoint.end,
        )

        RoadLinker.createExtendedPredSuc(
            predRoad=roads[0],
            predCp=pyodrx.ContactPoint.start,
            sucRoad=connectionRoad,
            sucCP=pyodrx.ContactPoint.start,
        )
        RoadLinker.createExtendedPredSuc(
            predRoad=connectionRoad,
            predCp=pyodrx.ContactPoint.end,
            sucRoad=previousRoad,
            sucCP=pyodrx.ContactPoint.end,
        )

        roads.append(connectionRoad)
        
        odr.updateRoads(roads)
        odr.resetAndReadjust(byPredecessor=True)
        odr = ODRHelper.transform(odr=odr, startX=130, startY=10, heading=0)

        xmlPath = f"output/test_assignment1.xodr"
        odr.write_xml(xmlPath)

        extensions.view_road(
            odr, os.path.join("..", self.configuration.get("esminipath"))
        )