import unittest
from junctions.Intersection import Intersection
from junctions.SequentialJunctionBuilder import SequentialJunctionBuilder
import extensions, os
import numpy as np
from library.Configuration import Configuration
from junctions.LaneConfiguration import LaneConfigurationStrategies
import pyodrx
import logging

from roadgen.layout.IntersectionAdapter import IntersectionAdapter
logging.basicConfig(level=logging.INFO)


class test_IntersectionAdapter(unittest.TestCase):

    def setUp(self):
        
        self.configuration = Configuration()
        outputDir= os.path.join(os.getcwd(), 'output')
        lastId = 0
        self.seed = 2
        self.builder = SequentialJunctionBuilder(
                                                    minAngle=np.pi/4, 
                                                    maxAngle=np.pi * .75,
                                                    straightRoadLen=10, 
                                                    probLongConnection=0.5,
                                                    probMinAngle=0.5,
                                                    probRestrictedLane=0.2,
                                                    maxConnectionLength=30,
                                                    minConnectionLength=12,
                                                    random_seed=self.seed)
        
        self.randomState =self.configuration.get("random_state")

        self.adapter = IntersectionAdapter()

        pass
    


    
    def test_getIncidentPoints(self):

        maxNumberOfRoadsPerJunction = 4
        path = self.configuration.get("harvested_straight_roads")
        intersection = self.builder.createWithRandomLaneConfigurations(path, 
                            0, 
                            maxNumberOfRoadsPerJunction=maxNumberOfRoadsPerJunction, 
                            maxLanePerSide=2, minLanePerSide=0, 
                            internalConnections=True, 
                            cp1=pyodrx.ContactPoint.end,
                            internalLinkStrategy = LaneConfigurationStrategies.SPLIT_FIRST,
                            getAsOdr=False)

        odr = intersection.odr

        xmlPath = f"output/test_getIncidentPoints-split-first-{maxNumberOfRoadsPerJunction}.xodr"
        odr.write_xml(xmlPath)

        incidentPoints = intersection.getIncidentPoints()
        translatedPoints = intersection.getIncidentPointsTranslatedToCenter()
        print(f"width and height: {intersection.getWH()}")
        print(incidentPoints)
        print(translatedPoints)

        # extensions.printRoadPositions(odr)

        directionIntersection = self.adapter.intersectionTo4DirectionIntersection(intersection)
        print(directionIntersection)

        extensions.view_road(odr, os.path.join('..',self.configuration.get("esminipath")))

    
    def test_intersectionToDirectionIntersection(self):
        
        maxNumberOfRoadsPerJunction = 5
        maxLanePerSide = 3
        minLanePerSide = 0
        
        for sl in range(5):
            
            intersection = self.builder.createWithRandomLaneConfigurations("", 
                                0, 
                                maxNumberOfRoadsPerJunction=maxNumberOfRoadsPerJunction, 
                                maxLanePerSide=maxLanePerSide, 
                                minLanePerSide=minLanePerSide, 
                                internalConnections=True, 
                                cp1=pyodrx.ContactPoint.end,
                                internalLinkStrategy = LaneConfigurationStrategies.SPLIT_ANY,
                                getAsOdr=False)
            odr = intersection.odr
            # xmlPath = f"output/test_intersectionToDirectionIntersection-split-any-{maxNumberOfRoadsPerJunction}-{sl}.xodr"
            xmlPath = f"output/seed-{self.seed}-{maxNumberOfRoadsPerJunction}-way-{sl}.xodr"
            odr.write_xml(xmlPath)
            
            directionIntersection = self.adapter.intersectionTo4DirectionIntersection(intersection)
            print(directionIntersection)
            # extensions.view_road(odr,os.path.join('..',self.configuration.get("esminipath")))
            extensions.view_road(odr, os.path.join('..',self.configuration.get("esminipath")))
