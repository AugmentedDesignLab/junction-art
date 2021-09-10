import unittest
import math
from analysis.metrics.MetricManager import MetricManager
from junctionart.junctions.SequentialJunctionBuilder import SequentialJunctionBuilder
import junctionart.extensions as extensions, os
import numpy as np
from junctionart.library.Configuration import Configuration
from junctionart.junctions.LaneConfiguration import LaneConfigurationStrategies
from junctionart.junctions.IntersectionValidator import IntersectionValidator
import pyodrx as pyodrx
import logging
from analysis.metrics.fov.IntersectionCorners import IntersectionCorners
from analysis.metrics.fov.Fov import Fov

class test_IntersectionCorners(unittest.TestCase):

    def setUp(self):
        
        self.configuration = Configuration()
        outputDir= os.path.join(os.getcwd(), 'output')
        lastId = 0
        self.seed = 1
        self.builder = SequentialJunctionBuilder(
                                                    minAngle=np.pi/10, 
                                                    maxAngle=np.pi * .75,
                                                    straightRoadLen=5, 
                                                    probLongConnection=0.5,
                                                    probMinAngle=0.5,
                                                    probRestrictedLane=0.2,
                                                    maxConnectionLength=50,
                                                    minConnectionLength=20,
                                                    random_seed=self.seed)
        
        self.randomState =self.configuration.get("random_state")
        self.validator = IntersectionValidator()
        pass


    
    
    def test_Intersections(self):
        minLanePerSide = 1
        maxLanePerSide = 2

        intersections = []
        
        for sl in range(3):
            maxNumberOfRoadsPerJunction = np.random.randint(3, 6)
            path = self.configuration.get("harvested_straight_roads")
            intersection = self.builder.createWithRandomLaneConfigurations(path, 
                                sl, 
                                maxNumberOfRoadsPerJunction=maxNumberOfRoadsPerJunction, 
                                maxLanePerSide=maxLanePerSide, 
                                minLanePerSide=minLanePerSide, 
                                internalConnections=True, 
                                cp1=pyodrx.ContactPoint.end,
                                internalLinkStrategy = LaneConfigurationStrategies.SPLIT_ANY,
                                getAsOdr=False)

            intersections.append(intersection)


            intersectionCorners = IntersectionCorners(intersection)
            minCorner = intersectionCorners.getMinCornerAngle()
            print(f"Min corner for intersection {intersection.id} is {math.degrees(minCorner)} and fov is {math.degrees(Fov.getFovFromMinCorner(minCorner))}")
            extensions.view_road(intersection.odr,os.path.join('..',self.configuration.get("esminipath")))