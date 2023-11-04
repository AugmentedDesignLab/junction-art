from junctionart.extensions.ExtendedLane import ExtendedLane
from junctionart.junctions.Geometry import Geometry
from junctionart.junctions.LaneSides import LaneSides
import pyodrx as pyodrx
from junctionart.extensions.CountryCodes import CountryCodes
import unittest
from junctionart.library.Configuration import Configuration
import junctionart.extensions as extensions, os
import math
from junctionart.roundabout.ClassicGenerator import ClassicGenerator
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
import pickle
from pyodrx.lane import LaneSection
import sys
import pprofile

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
        self.profiler = pprofile.Profile()
        pass


    def test_createRoundAboutFromIncidentPoints1(self):

        threePoints = [
            {"x": 80, "y": 20, "heading": math.radians(45),'leftLane': 1, 'rightLane': 1, 'medianType': None, 'skipEndpoint': None},
            {"x": 210, "y": 20, "heading": math.radians(115),'leftLane': 1, 'rightLane': 1, 'medianType': None, 'skipEndpoint': None},
            {"x": 100, "y": 100, "heading": math.radians(300),'leftLane': 1, 'rightLane': 1, 'medianType': None, 'skipEndpoint': None},
            # {"x": 160, "y": 49, "heading": math.radians(300),'leftLane': 1, 'rightLane': 1, 'medianType': None, 'skipEndpoint': None},
            # {"x": 160, "y": 100, "heading": math.radians(220),'leftLane': 1, 'rightLane': 1, 'medianType': None, 'skipEndpoint': None},
        ]
        with self.profiler:
            odr = self.builder.generateWithRoadDefinition(
                threePoints,
                outgoingLanesMerge=False
            )

        self.profiler.print_stats()
        extensions.printRoadPositions(odr)
        extensions.view_road(
            odr, os.path.join("..", self.configuration.get("esminipath"))
        )

    def test_createRoundAboutFromIncidentPoints3(self):

        threePoints = [
            # {"x": 600, "y": 200, "heading": math.radians(15),'leftLane': 2, 'rightLane': 3, 'medianType': None, 'skipEndpoint': None},
            {"x": 100, "y": 500, "heading": math.radians(340),'leftLane': 2, 'rightLane': 4, 'medianType': None, 'skipEndpoint': None},
            {"x": 440, "y": 500, "heading": math.radians(270),'leftLane': 2, 'rightLane': 2, 'medianType': None, 'skipEndpoint': None}, 
            {"x": 460, "y": 50, "heading": math.radians(90),'leftLane': 2, 'rightLane': 1, 'medianType': None, 'skipEndpoint': None},
            {"x": 160, "y": 100, "heading": math.radians(20),'leftLane': 1, 'rightLane': 1, 'medianType': None, 'skipEndpoint': None},
        ]
        odr = self.builder.generateWithRoadDefinition(
            threePoints,
            outgoingLanesMerge=False
        )
        extensions.printRoadPositions(odr)
        extensions.view_road(
            odr, os.path.join("..", self.configuration.get("esminipath"))
        )

    def test_createRoundAboutFromIncidentPoints4(self):
        control = 200
        threePoints = [
            # {"x": random.random()*control, "y": random.random()*control, "heading": math.radians(random.random()*control % 100),'leftLane': 3, 'rightLane': 2, 'medianType': None, 'skipEndpoint': None},
            {"x": -100, "y": 200, "heading": math.radians(15),'leftLane': 2, 'rightLane': 3, 'medianType': None, 'skipEndpoint': None},
            {"x": random.random()*control, "y": random.random()*control, "heading": math.radians((random.random()*control % 100) + 50),'leftLane': 3, 'rightLane': 4, 'medianType': None, 'skipEndpoint': None},
            {"x": random.random()*control, "y": random.random()*control, "heading": math.radians((random.random()*control % 100) + 100),'leftLane': 2, 'rightLane': 1, 'medianType': None, 'skipEndpoint': None},
            {"x": 160, "y": 100, "heading": math.radians(200),'leftLane': 1, 'rightLane': 1, 'medianType': None, 'skipEndpoint': None},
        ]
        odr = self.builder.generateWithRoadDefinition(
            threePoints,
            outgoingLanesMerge=True
        )
        extensions.printRoadPositions(odr)
        extensions.view_road(
            odr, os.path.join("..", self.configuration.get("esminipath"))
        )

    def test_createRoundAboutFromIncidentPoints2(self):

        threePoints = [ 
            {"x": 0, "y": 50, "heading": math.radians(0),'leftLane': 1, 'rightLane': 1, 'medianType': None, 'skipEndpoint': None},
            {"x": 1, "y": 1, "heading": math.radians(45),'leftLane': 1, 'rightLane': 1, 'medianType': None, 'skipEndpoint': None},
            {"x": 100, "y": 100, "heading": math.radians(250),'leftLane': 1, 'rightLane': 1, 'medianType': None, 'skipEndpoint': None},
            # {"x": -100, "y": 100, "heading": math.radians(20),'leftLane': 1, 'rightLane': 1, 'medianType': None, 'skipEndpoint': None},
        ]
        odr = self.builder.generateWithRoadDefinition(
            threePoints
        )
        extensions.printRoadPositions(odr)
        extensions.view_road(
            odr, os.path.join("..", self.configuration.get("esminipath"))
        )
    
    def test_roadWidening(self):
        road1 = self.straightbuilder.createRandom(roadId=0)
        ls = road1.getLaneSections()
        print(ls[0])
        d, c, b, a = Geometry.cubic_equation_find(3, 20, 1.4)
        lane = ExtendedLane(a= a, b= b , c = c , d = d)
        ls[0].add_right_lane(lane)
        # ls.add_left_lane(lane)
        print(type(lane).__name__)
        roads = []

        # ls[0].prependLaneToRightLanes(lane)

        
        roads.append(road1)
        odrName = "TempCircularRoads" 
        odr = extensions.createOdrByPredecessor(
            odrName, roads, [], countryCode=CountryCodes.US
        )
        extensions.view_road(
            odr, os.path.join("..", self.configuration.get("esminipath"))
        )

    def get_random_circle(self):
        radius = random.randint(35, 45) #50, 200 chhilo
        center_x = random.randint(0, 200)
        center_y = random.randint(0, 200)
        return center_x, center_y, radius

    def get_random_point(self, center_x, center_y, radius):
        angle = random.random()*math.pi*2
        random_x = center_x + radius * math.cos(angle)
        random_y = center_y + radius * math.sin(angle)
        # random_x = random.randint(center_x - radius, center_x + radius)
        # random_y = center_y + (-1)**random.randint(0,1)*math.sqrt(radius**2 - (center_x - random_x)**2)
        return random_x, random_y

    def get_angle(self, center_x, center_y, x, y):
        angle = math.atan2(center_y - y, center_x - x)
        return (math.degrees(angle))

    def random_gradient_tranlation(self, angle, start_x, start_y):
        distance = random.randint(30, 100)
        end_x = start_x + distance * math.cos(math.radians(angle))
        end_y = start_y + distance * math.sin(math.radians(angle))
        return end_x, end_y

    def get_random_points(self, center_x, center_y, radius, nPoints):
        points = []
        for i in range(nPoints):
            x, y = self.get_random_point(center_x, center_y, radius)
            angle = self.get_angle(center_x, center_y, x, y)
            modified_angle = angle + random.randint(-30, 30)
            modified_x, modified_y = self.random_gradient_tranlation(modified_angle, x, y)
            points.append((modified_x, modified_y, modified_angle - 180 if modified_angle > 180 else modified_angle + 180))
            
        return sorted(points, key = lambda x : x[2])

    def get_fixed_points(self, center_x, center_y, radius, nPoints):
        points = []
        for i in range(nPoints):
            x, y = self.get_random_point(center_x, center_y, radius)
            angle = self.get_angle(center_x, center_y, x, y)
            modified_angle = angle + random.randint(-30, 30)
            # modified_x, modified_y = self.random_gradient_tranlation(modified_angle, x, y)
            points.append((x, y, modified_angle))
            
        return sorted(points, key = lambda x : x[2])

    def get_fixed_points2(self, center_x, center_y, radius, nPoints):
        points = []
        randomAngle = 2*np.pi*random.random()
        angles = [randomAngle + i*2*np.pi/nPoints for i in range(nPoints)]
        for angle in angles:
            angle = angle + random.randint(-5*(6-nPoints), 5*(6-nPoints))
            x = center_x + radius * math.cos(angle)
            y = center_y + radius * math.sin(angle)
            angle = self.get_angle(center_x, center_y, x, y)
            modified_angle = angle + random.randint(-30, 30)
            # modified_x, modified_y = self.random_gradient_tranlation(modified_angle, x, y)
            points.append((x, y, modified_angle))
            
        return sorted(points, key = lambda x : x[2])
    def test_random_point_genration(self):
        sys.setrecursionlimit(100000)
        for i in range(3, 6): # from 2 - 6 ways
            roundabouts = []
            for j in range(20): #make 100 roundabouts for each way
                center_x, center_y, radius = self.get_random_circle()
                points = self.get_fixed_points(center_x, center_y, radius, i)
                # print(points)
                road_definitions = [{"x": point[0], "y": point[1], "heading": math.radians(point[2]),'leftLane': 2, 'rightLane': 2, 'medianType': None, 'skipEndpoint': None} for point in points]
                generator = ClassicGenerator(country=CountryCodes.US, laneWidth=3)
                odr = generator.generateWithRoadDefinition(
                    road_definitions,
                    outgoingLanesMerge=False
                )

                roundabout = generator.getRoundabout()
                roundabouts.append(roundabout)

            with open(f"_roundabout{i}ways.pickle", "wb") as f:
                pickle.dump(roundabouts, f)

    def test_same_point_genration(self):
        sys.setrecursionlimit(100000)
        roundabouts = []
        for j in range(30): #make 100 roundabouts for each way
            center_x, center_y, radius = 5, 5, 40
            points = self.get_fixed_points(center_x, center_y, radius, 3)
            road_definitions = [{"x": point[0], "y": point[1], "heading": math.radians(point[2]),'leftLane': 2, 'rightLane': 2, 'medianType': None, 'skipEndpoint': None} for point in points]
            generator = ClassicGenerator(country=CountryCodes.US, laneWidth=3)
            odr = generator.generateWithRoadDefinition(
                road_definitions,
                outgoingLanesMerge=False
            )

            roundabout = generator.getRoundabout()
            roundabouts.append(roundabout)

            with open(f"_roundabout{3}ways_fixed.pickle", "wb") as f:
                pickle.dump(roundabouts, f)

    def test_case_genration(self):
        sys.setrecursionlimit(100000)
        roadDefs = []
        nPoints = 4
        for j in range(20): #make 100 roundabouts for each way
            center_x, center_y, radius = 5, 5, 40
            points = self.get_fixed_points(center_x, center_y, radius, nPoints)
            road_definition = [{"x": point[0], "y": point[1], "heading": math.radians(point[2]),'leftLane': 1, 'rightLane': 1, 'medianType': None, 'skipEndpoint': None} for point in points]
            
            roadDefs.append(road_definition)

            with open(f"inputTestCases/_input{nPoints}ways_n=8_.pickle", "wb") as f:
                pickle.dump(roadDefs, f)

    def test_random_roundabout(self):
        i = 4
        center_x, center_y, radius = self.get_random_circle()
        radius = 40
        points = self.get_fixed_points2(center_x, center_y, radius, i)
        road_definitions = [{"x": point[0], "y": point[1], "heading": math.radians(point[2]),'leftLane': random.randint(1, 1), 'rightLane': random.randint(1, 1), 'medianType': None, 'skipEndpoint': None} for point in points]
        print(road_definitions)
        generator = ClassicGenerator(country=CountryCodes.US, laneWidth=3)
        odr = generator.generateWithRoadDefinition(
            road_definitions,
            outgoingLanesMerge=False
        )

        extensions.view_road(
            odr, os.path.join("..", self.configuration.get("esminipath"))
        )

    def test_turbo_circle(self):
        radius = 6
        segment = 4
        roadLength = 2 * np.pi * radius / segment
        roads = []
        r1 = self.curveBuilder.createCurveByLength(
                roadId= 1,
                length=roadLength,
                laneSides=LaneSides.RIGHT,
                curvature=1/radius,
                n_lanes=2,
                # isRightTurnLane= True
            )
        r2 = self.curveBuilder.createCurveByLength(
                roadId= 2,
                length=roadLength,
                laneSides=LaneSides.RIGHT,
                curvature=1/radius,
                n_lanes=2,
                # isRightTurnLane= True
            )
        r3 = self.curveBuilder.createCurveByLength(
                roadId= 4,
                length=roadLength,
                laneSides=LaneSides.RIGHT,
                curvature=1/radius,
                n_lanes=2,
                # isRightTurnLane= True
                # isRightMergeLane= True
            )
        
        r4 = self.curveBuilder.createCurveByLength(
                roadId= 5,
                length=roadLength,
                laneSides=LaneSides.RIGHT,
                curvature=1/radius,
                n_lanes=1,
                isRightTurnLane= True
            )
        
        roads = [r1, r2]


        for i in range(len(roads) - 1):
            RoadLinker.createExtendedPredSuc(
                predRoad=roads[i],
                predCp=pyodrx.ContactPoint.end,
                sucRoad=roads[i + 1],
                sucCP=pyodrx.ContactPoint.start,
            )
        odr = extensions.createOdrByPredecessor(
            'TurboTest', roads, [], countryCode=CountryCodes.US
        )
        # odr.resetAndReadjust(byPredecessor=True)
        odrName = "tempODR_CircleRoad" + str(1)
        odrStraightRoad = extensions.createOdrByPredecessor(
            odrName, [r3], [], countryCode=CountryCodes.US
        )
        ODRHelper.transform(
                odrStraightRoad, 0, 2*radius - 3, np.pi
        )
        circularRoadsJoint = self.junctionBuilder.createConnectionFor2Roads(
            nextRoadId=3,
            road1=r2,
            road2=r3,
            n_lanes= 1,
            laneSides=LaneSides.RIGHT,
            junction=None,
            cp1=pyodrx.ContactPoint.end,
            cp2=pyodrx.ContactPoint.start,
        )
        roads.append(circularRoadsJoint)
        roads.append(r3)
        roads.append(r4)
        RoadLinker.createExtendedPredSuc(
                predRoad=roads[3],
                predCp=pyodrx.ContactPoint.end,
                sucRoad=roads[4],
                sucCP=pyodrx.ContactPoint.start,
            )
        odr.updateRoads(roads)
        odr.resetAndReadjust(byPredecessor=True)
        circularRoadsJoint2 = self.junctionBuilder.createConnectionFor2Roads(
            nextRoadId=6,
            road1=r4,
            road2=r1,
            n_lanes= 1,
            laneSides=LaneSides.RIGHT,
            junction=None,
            cp1=pyodrx.ContactPoint.end,
            cp2=pyodrx.ContactPoint.start,
        )
        roads.append(circularRoadsJoint2)
        odr.updateRoads(roads)
        odr.resetAndReadjust(byPredecessor=True)
        extensions.view_road(
            odr, os.path.join("..", self.configuration.get("esminipath"))
        )

       

        
        
            
