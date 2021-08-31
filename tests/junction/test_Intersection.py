from junctions.Intersection import Intersection
import unittest
from junctions.SequentialJunctionBuilder import SequentialJunctionBuilder
import junctionart.extensions as extensions, os
import numpy as np
from library.Configuration import Configuration
from junctions.LaneConfiguration import LaneConfigurationStrategies
import pyodrx
import logging
logging.basicConfig(level=logging.INFO)


class test_Intersection(unittest.TestCase):

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

        extensions.printRoadPositions(odr)

        extensions.view_road(odr, os.path.join('..',self.configuration.get("esminipath")))
