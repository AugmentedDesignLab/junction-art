import unittest
import matplotlib.pyplot as plt
from analysis.metrics.travel.ConnectionRoadComplexity import ConnectionRoadComplexity
from junctions.SequentialJunctionBuilder import SequentialJunctionBuilder
import extensions, os
import numpy as np
from library.Configuration import Configuration
from junctions.LaneConfiguration import LaneConfigurationStrategies
from junctions.IntersectionValidator import IntersectionValidator
import pyodrx
import logging
logging.basicConfig(level=logging.INFO)


class test_ConnectionRoadComplexity(unittest.TestCase):

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

    def test_Creation(self):

        maxNumberOfRoadsPerJunction = 3
        minLanePerSide = 1
        maxLanePerSide = 2
        
        for sl in range(1):
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


            odr = intersection.odr
            # xmlPath = f"output/test_createWithRandomLaneConfigurations-split-any-{maxNumberOfRoadsPerJunction}-{sl}.xodr"
            xmlPath = f"output/seed-{self.seed}-{maxNumberOfRoadsPerJunction}-way-{sl}.xodr"
            odr.write_xml(xmlPath)
            # isValid = self.validator.validateIncidentPoints(intersection, self.builder.minConnectionLength)
            # if isValid == False:
            #     print(f"{sl} is an invalid intersection")

            connectionRoadComplexity = ConnectionRoadComplexity(intersection, minPathLengthIntersection=10)

            connectionRoadComplexity.measureTurnComplexities()

            connectionRoadComplexity.printTurnComplexities()
            print(f"\n max complexity is ", connectionRoadComplexity.getMaxTurnComplexity())
            # plt = extensions.view_road(odr,os.path.join('..',self.configuration.get("esminipath")), returnPlt=True)
            # if isValid == False:
            #     plt.title("Invalid")
            # else:
            #     plt.title("Valid")
            # extensions.saveRoadImageFromFile(xmlPath, self.configuration.get("esminipath"))
            # plt.show()
            connectionRoadComplexity.connectRoadDf.plot()
            plt.show()