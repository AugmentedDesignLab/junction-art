import unittest
# from junctionart.junctions.SequentialJunctionBuilder import SequentialJunctionBuilder

import os
import numpy as np
from junctionart.library.Configuration import Configuration
from junctionart.junctions.LaneConfigurationStrategies import LaneConfigurationStrategies
from junctionart.junctions.IntersectionValidator import IntersectionValidator
from junctionart.junctions.SequentialJunctionBuilder import SequentialJunctionBuilder
import junctionart.extensions as extensions
import pyodrx as pyodrx
import logging
from tqdm import tqdm
logging.basicConfig(level=logging.INFO)

class test_SequentialJunctionBuilder(unittest.TestCase):

    def setUp(self):
        
        self.configuration = Configuration()
        outputDir= os.path.join(os.getcwd(), 'output')
        lastId = 0
        self.seed = 2
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

    def test_Hello(self):
        pass

    def test_drawLikeAPainter2L(self):
        maxNumberOfRoadsPerJunction = 3
        odr = self.builder.drawLikeAPainter2L(odrId=0, maxNumberOfRoadsPerJunction=maxNumberOfRoadsPerJunction)
        extensions.printRoadPositions(odr)
        extensions.view_road(odr,os.path.join('..',self.configuration.get("esminipath")))
        
        xmlPath = f"output/test_drawLikeAPainter2L-{maxNumberOfRoadsPerJunction}.xodr"
        odr.write_xml(xmlPath)

        maxNumberOfRoadsPerJunction = 4
        odr = self.builder.drawLikeAPainter2L(odrId=0, maxNumberOfRoadsPerJunction=maxNumberOfRoadsPerJunction)
        extensions.printRoadPositions(odr)
        extensions.view_road(odr,os.path.join('..',self.configuration.get("esminipath")))
        
        xmlPath = f"output/test_drawLikeAPainter2L-{maxNumberOfRoadsPerJunction}.xodr"
        odr.write_xml(xmlPath)

        maxNumberOfRoadsPerJunction = 5
        odr = self.builder.drawLikeAPainter2L(odrId=0, maxNumberOfRoadsPerJunction=maxNumberOfRoadsPerJunction)
        extensions.printRoadPositions(odr)
        extensions.view_road(odr,os.path.join('..',self.configuration.get("esminipath")))
        
        xmlPath = f"output/test_drawLikeAPainter2L-{maxNumberOfRoadsPerJunction}.xodr"
        odr.write_xml(xmlPath)

        maxNumberOfRoadsPerJunction = 6
        odr = self.builder.drawLikeAPainter2L(odrId=0, maxNumberOfRoadsPerJunction=maxNumberOfRoadsPerJunction)
        extensions.printRoadPositions(odr)
        extensions.view_road(odr,os.path.join('..',self.configuration.get("esminipath")))
        
        xmlPath = f"output/test_drawLikeAPainter2L-{maxNumberOfRoadsPerJunction}.xodr"
        odr.write_xml(xmlPath)

    def test_drawLikeAPainter2LWihtoutInternalConnections(self):
        maxNumberOfRoadsPerJunction = 5
        odr = self.builder.drawLikeAPainter2L(odrId=0, maxNumberOfRoadsPerJunction=maxNumberOfRoadsPerJunction, internalConnections=False)
        extensions.printRoadPositions(odr)
        extensions.view_road(odr,os.path.join('..',self.configuration.get("esminipath")))
        xmlPath = f"output/test_drawLikeAPainter2LWihtoutInternalConnections.xodr"
        odr.write_xml(xmlPath)


    def test_createWithRandomLaneConfigurations(self):

        maxNumberOfRoadsPerJunction = 4
        path = self.configuration.get("harvested_straight_roads")
        odr = self.builder.createWithRandomLaneConfigurations(path, 
                            0, 
                            maxNumberOfRoadsPerJunction=maxNumberOfRoadsPerJunction, 
                            maxLanePerSide=2, minLanePerSide=0, 
                            internalConnections=True, 
                            cp1=pyodrx.ContactPoint.end,
                            internalLinkStrategy = LaneConfigurationStrategies.SPLIT_FIRST,
                            restrictedLanes=True)

        xmlPath = f"output/test_createWithRandomLaneConfigurations-split-first-{maxNumberOfRoadsPerJunction}.xodr"
        odr.write_xml(xmlPath)

        extensions.view_road(odr,os.path.join('..',self.configuration.get("esminipath")))

        maxNumberOfRoadsPerJunction = 3
        path = self.configuration.get("harvested_straight_roads")
        odr = self.builder.createWithRandomLaneConfigurations(path, 
                            0, 
                            maxNumberOfRoadsPerJunction=maxNumberOfRoadsPerJunction, 
                            maxLanePerSide=2, minLanePerSide=0, 
                            internalConnections=True, 
                            cp1=pyodrx.ContactPoint.end,
                            internalLinkStrategy = LaneConfigurationStrategies.SPLIT_LAST,
                            uTurnLanes=1,
                            restrictedLanes=True)

        extensions.view_road(odr,os.path.join('..',self.configuration.get("esminipath")))
        xmlPath = f"output/test_createWithRandomLaneConfigurations-split-last-{maxNumberOfRoadsPerJunction}.xodr"
        odr.write_xml(xmlPath)


        maxNumberOfRoadsPerJunction = 5
        path = self.configuration.get("harvested_straight_roads")
        odr = self.builder.createWithRandomLaneConfigurations(path, 
                            0, 
                            maxNumberOfRoadsPerJunction=maxNumberOfRoadsPerJunction, 
                            maxLanePerSide=2, minLanePerSide=0, 
                            internalConnections=True, 
                            cp1=pyodrx.ContactPoint.end,
                            internalLinkStrategy = LaneConfigurationStrategies.SPLIT_ANY,
                            restrictedLanes=True)

        extensions.view_road(odr,os.path.join('..',self.configuration.get("esminipath")))
        xmlPath = f"output/test_createWithRandomLaneConfigurations-split-any-{maxNumberOfRoadsPerJunction}.xodr"
        odr.write_xml(xmlPath)


        maxNumberOfRoadsPerJunction = 6
        path = self.configuration.get("harvested_straight_roads")
        odr = self.builder.createWithRandomLaneConfigurations(path, 
                            0, 
                            maxNumberOfRoadsPerJunction=maxNumberOfRoadsPerJunction, 
                            maxLanePerSide=2, minLanePerSide=0, 
                            internalConnections=True, 
                            cp1=pyodrx.ContactPoint.end,
                            internalLinkStrategy = LaneConfigurationStrategies.SPLIT_ANY)

        extensions.view_road(odr,os.path.join('..',self.configuration.get("esminipath")))
        xmlPath = f"output/test_createWithRandomLaneConfigurations-split-any-{maxNumberOfRoadsPerJunction}.xodr"
        odr.write_xml(xmlPath)


        maxNumberOfRoadsPerJunction = 8
        path = self.configuration.get("harvested_straight_roads")
        odr = self.builder.createWithRandomLaneConfigurations(path, 
                            0, 
                            maxNumberOfRoadsPerJunction=maxNumberOfRoadsPerJunction, 
                            maxLanePerSide=2, minLanePerSide=0, 
                            internalConnections=True, 
                            cp1=pyodrx.ContactPoint.end,
                            internalLinkStrategy = LaneConfigurationStrategies.SPLIT_ANY)

        extensions.view_road(odr,os.path.join('..',self.configuration.get("esminipath")))
        xmlPath = f"output/test_createWithRandomLaneConfigurations-split-any-{maxNumberOfRoadsPerJunction}.xodr"
        odr.write_xml(xmlPath)

    
    def test_equalAngles(self):

        maxNumberOfRoadsPerJunction = 4
        path = self.configuration.get("harvested_straight_roads")
        odr = self.builder.createWithRandomLaneConfigurations(path, 
                            0, 
                            maxNumberOfRoadsPerJunction=maxNumberOfRoadsPerJunction, 
                            maxLanePerSide=2, minLanePerSide=0, 
                            internalConnections=True, 
                            cp1=pyodrx.ContactPoint.end,
                            internalLinkStrategy = LaneConfigurationStrategies.SPLIT_ANY,
                            equalAngles=True)

        extensions.view_road(odr,os.path.join('..',self.configuration.get("esminipath")))
        xmlPath = f"output/test_createWithRandomLaneConfigurations-split-any-{maxNumberOfRoadsPerJunction}.xodr"
        odr.write_xml(xmlPath)

        
        maxNumberOfRoadsPerJunction = 4
        path = self.configuration.get("harvested_straight_roads")
        odr = self.builder.createWithRandomLaneConfigurations(path, 
                            0, 
                            maxNumberOfRoadsPerJunction=maxNumberOfRoadsPerJunction, 
                            maxLanePerSide=2, minLanePerSide=0, 
                            internalConnections=True, 
                            cp1=pyodrx.ContactPoint.end,
                            internalLinkStrategy = LaneConfigurationStrategies.SPLIT_ANY,
                            equalAngles=True)

        extensions.view_road(odr,os.path.join('..',self.configuration.get("esminipath")))
        xmlPath = f"output/test_createWithRandomLaneConfigurations-split-any-{maxNumberOfRoadsPerJunction}.xodr"
        odr.write_xml(xmlPath)
        
        maxNumberOfRoadsPerJunction = 3
        path = self.configuration.get("harvested_straight_roads")
        odr = self.builder.createWithRandomLaneConfigurations(path, 
                            0, 
                            maxNumberOfRoadsPerJunction=maxNumberOfRoadsPerJunction, 
                            maxLanePerSide=2, minLanePerSide=0, 
                            internalConnections=True, 
                            cp1=pyodrx.ContactPoint.end,
                            internalLinkStrategy = LaneConfigurationStrategies.SPLIT_ANY,
                            equalAngles=True)

        extensions.view_road(odr,os.path.join('..',self.configuration.get("esminipath")))
        xmlPath = f"output/test_createWithRandomLaneConfigurations-split-any-{maxNumberOfRoadsPerJunction}.xodr"
        odr.write_xml(xmlPath)
        
        maxNumberOfRoadsPerJunction = 5
        path = self.configuration.get("harvested_straight_roads")
        odr = self.builder.createWithRandomLaneConfigurations(path, 
                            0, 
                            maxNumberOfRoadsPerJunction=maxNumberOfRoadsPerJunction, 
                            maxLanePerSide=2, minLanePerSide=0, 
                            internalConnections=True, 
                            cp1=pyodrx.ContactPoint.end,
                            internalLinkStrategy = LaneConfigurationStrategies.SPLIT_ANY,
                            equalAngles=True)

        extensions.view_road(odr,os.path.join('..',self.configuration.get("esminipath")))
        xmlPath = f"output/test_createWithRandomLaneConfigurations-split-any-{maxNumberOfRoadsPerJunction}.xodr"
        odr.write_xml(xmlPath)

        maxNumberOfRoadsPerJunction = 6
        path = self.configuration.get("harvested_straight_roads")
        odr = self.builder.createWithRandomLaneConfigurations(path, 
                            0, 
                            maxNumberOfRoadsPerJunction=maxNumberOfRoadsPerJunction, 
                            maxLanePerSide=2, minLanePerSide=0, 
                            internalConnections=True, 
                            cp1=pyodrx.ContactPoint.end,
                            internalLinkStrategy = LaneConfigurationStrategies.SPLIT_ANY,
                            equalAngles=True)

        extensions.view_road(odr,os.path.join('..',self.configuration.get("esminipath")))
        xmlPath = f"output/test_createWithRandomLaneConfigurations-split-any-{maxNumberOfRoadsPerJunction}.xodr"
        odr.write_xml(xmlPath)

    
    def test_6PlusLanes(self):


        maxNumberOfRoadsPerJunction = 7
        path = self.configuration.get("harvested_straight_roads")
        odr = self.builder.createWithRandomLaneConfigurations(path, 
                            0, 
                            maxNumberOfRoadsPerJunction=maxNumberOfRoadsPerJunction, 
                            maxLanePerSide=2, minLanePerSide=0, 
                            internalConnections=True, 
                            cp1=pyodrx.ContactPoint.end,
                            internalLinkStrategy = LaneConfigurationStrategies.SPLIT_ANY)

        extensions.view_road(odr,os.path.join('..',self.configuration.get("esminipath")))
        xmlPath = f"output/test_createWithRandomLaneConfigurations-split-any-{maxNumberOfRoadsPerJunction}.xodr"
        odr.write_xml(xmlPath)

        maxNumberOfRoadsPerJunction = 8
        path = self.configuration.get("harvested_straight_roads")
        odr = self.builder.createWithRandomLaneConfigurations(path, 
                            0, 
                            maxNumberOfRoadsPerJunction=maxNumberOfRoadsPerJunction, 
                            maxLanePerSide=2, minLanePerSide=0, 
                            internalConnections=True, 
                            cp1=pyodrx.ContactPoint.end,
                            internalLinkStrategy = LaneConfigurationStrategies.SPLIT_ANY)

        extensions.view_road(odr,os.path.join('..',self.configuration.get("esminipath")))
        xmlPath = f"output/test_createWithRandomLaneConfigurations-split-any-{maxNumberOfRoadsPerJunction}.xodr"
        odr.write_xml(xmlPath)
        
        maxNumberOfRoadsPerJunction = 8
        path = self.configuration.get("harvested_straight_roads")
        odr = self.builder.createWithRandomLaneConfigurations(path, 
                            0, 
                            maxNumberOfRoadsPerJunction=maxNumberOfRoadsPerJunction, 
                            maxLanePerSide=2, minLanePerSide=0, 
                            internalConnections=True, 
                            cp1=pyodrx.ContactPoint.end,
                            internalLinkStrategy = LaneConfigurationStrategies.SPLIT_ANY,
                            equalAngles=True)

        extensions.view_road(odr,os.path.join('..',self.configuration.get("esminipath")))
        xmlPath = f"output/test_createWithRandomLaneConfigurations-split-any-{maxNumberOfRoadsPerJunction}.xodr"
        odr.write_xml(xmlPath)

        maxNumberOfRoadsPerJunction = 8
        path = self.configuration.get("harvested_straight_roads")
        odr = self.builder.createWithRandomLaneConfigurations(path, 
                            0, 
                            maxNumberOfRoadsPerJunction=maxNumberOfRoadsPerJunction, 
                            maxLanePerSide=2, minLanePerSide=0, 
                            internalConnections=True, 
                            cp1=pyodrx.ContactPoint.end,
                            internalLinkStrategy = LaneConfigurationStrategies.SPLIT_ANY)

        extensions.view_road(odr,os.path.join('..',self.configuration.get("esminipath")))
        xmlPath = f"output/test_createWithRandomLaneConfigurations-split-any-{maxNumberOfRoadsPerJunction}.xodr"
        odr.write_xml(xmlPath)

        maxNumberOfRoadsPerJunction = 9
        path = self.configuration.get("harvested_straight_roads")
        odr = self.builder.createWithRandomLaneConfigurations(path, 
                            0, 
                            maxNumberOfRoadsPerJunction=maxNumberOfRoadsPerJunction, 
                            maxLanePerSide=2, minLanePerSide=0, 
                            internalConnections=True, 
                            cp1=pyodrx.ContactPoint.end,
                            internalLinkStrategy = LaneConfigurationStrategies.SPLIT_ANY)

        extensions.view_road(odr,os.path.join('..',self.configuration.get("esminipath")))
        xmlPath = f"output/test_createWithRandomLaneConfigurations-split-any-{maxNumberOfRoadsPerJunction}.xodr"
        odr.write_xml(xmlPath)

    
    def test_TJunctions(self):

        maxNumberOfRoadsPerJunction = 3
        maxLanePerSide = 1
        minLanePerSide = 1
        
        for sl in range(5):
            path = self.configuration.get("harvested_straight_roads")
            odr = self.builder.createWithRandomLaneConfigurations(path, 
                                0, 
                                maxNumberOfRoadsPerJunction=maxNumberOfRoadsPerJunction, 
                                maxLanePerSide=maxLanePerSide, 
                                minLanePerSide=minLanePerSide, 
                                internalConnections=True, 
                                cp1=pyodrx.ContactPoint.end,
                                internalLinkStrategy = LaneConfigurationStrategies.SPLIT_ANY,
                                uTurnLanes=0)

            # xmlPath = f"output/test_createWithRandomLaneConfigurations-split-any-{maxNumberOfRoadsPerJunction}-{sl}.xodr"
            xmlPath = f"output/seed-{self.seed}-{maxNumberOfRoadsPerJunction}-way-{sl}.xodr"
            odr.write_xml(xmlPath)
            
            extensions.view_road(odr,os.path.join('..',self.configuration.get("esminipath")))
            extensions.saveRoadImageFromFile(xmlPath, self.configuration.get("esminipath"))
    
    def test_export2LaneIntersections(self):
        
        maxNumberOfRoadsPerJunction = 3
        minLanePerSide = 1
        maxLanePerSide = 2
        numberOfIntersections = 10
        
        created = 0
        # create 
        with tqdm(total=numberOfIntersections) as pbar:
            while created < numberOfIntersections:
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
                isValid = self.validator.validateIncidentPoints(intersection, self.builder.minConnectionLength)
                if isValid:
                    pbar.update(1)
                    
                if created % 100 == 0:
                    print(f"generated {created}")




    def test_3WayJunctions(self):

        maxNumberOfRoadsPerJunction = 3
        minLanePerSide = 1
        maxLanePerSide = 2
        
        for sl in range(3):
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
            isValid = self.validator.validateIncidentPoints(intersection, self.builder.minConnectionLength)
            # if isValid == False:
            #     print(f"{sl} is an invalid intersection")
            plt = extensions.view_road(odr,os.path.join('..',self.configuration.get("esminipath")), returnPlt=True)
            if isValid == False:
                plt.title("Invalid")
            else:
                plt.title("Valid")
            plt.show()
            extensions.saveRoadImageFromFile(xmlPath, self.configuration.get("esminipath"))

    def test_4WayJunctions(self):

        maxNumberOfRoadsPerJunction = 4
        maxLanePerSide = 1
        minLanePerSide = 1
        
        for sl in range(5):
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
            isValid = self.validator.validateIncidentPoints(intersection, self.builder.minConnectionLength)
            # if isValid == False:
            #     print(f"{sl} is an invalid intersection")
            plt = extensions.view_road(odr,os.path.join('..',self.configuration.get("esminipath")), returnPlt=True)
            if isValid == False:
                plt.title("Invalid")
            else:
                plt.title("Valid")
            plt.show()
            extensions.saveRoadImageFromFile(xmlPath, self.configuration.get("esminipath"))


    def test_5WayJunctions(self):

        maxNumberOfRoadsPerJunction = 5
        maxLanePerSide = 3
        minLanePerSide = 0
        
        for sl in range(5):
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
            isValid = self.validator.validateIncidentPoints(intersection, self.builder.minConnectionLength)
            # if isValid == False:
            #     print(f"{sl} is an invalid intersection")
            plt = extensions.view_road(odr,os.path.join('..',self.configuration.get("esminipath")), returnPlt=True)
            if isValid == False:
                plt.title("Invalid")
            else:
                plt.title("Valid")
            plt.show()
            extensions.saveRoadImageFromFile(xmlPath, self.configuration.get("esminipath"))

    def test_6WayJunctions(self):

        maxNumberOfRoadsPerJunction = 6
        maxLanePerSide = 2
        minLanePerSide = 0
        
        for sl in range(5):
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
            extensions.printRoadPositions(odr)
            isValid = self.validator.validateIncidentPoints(intersection, self.builder.minConnectionLength)
            # if isValid == False:
            #     print(f"{sl} is an invalid intersection")
            plt = extensions.view_road(odr,os.path.join('..',self.configuration.get("esminipath")), returnPlt=True)
            if isValid == False:
                plt.title(f"Invalid - {xmlPath}")
            else:
                plt.title(f"Valid - {xmlPath}")
            plt.show()
            extensions.saveRoadImageFromFile(xmlPath, self.configuration.get("esminipath"))


    def test_7WayJunctions(self):

        maxNumberOfRoadsPerJunction = 7
        maxLanePerSide = 2
        minLanePerSide = 0
        
        for sl in range(5):
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
            extensions.printRoadPositions(odr)
            isValid = self.validator.validateIncidentPoints(intersection, self.builder.minConnectionLength)
            # if isValid == False:
            #     print(f"{sl} is an invalid intersection")
            plt = extensions.view_road(odr,os.path.join('..',self.configuration.get("esminipath")), returnPlt=True)
            if isValid == False:
                plt.title(f"Invalid - {xmlPath}")
            else:
                plt.title(f"Valid - {xmlPath}")
            plt.show()
            extensions.saveRoadImageFromFile(xmlPath, self.configuration.get("esminipath"))

    def test_7WayJunctionsEQA(self):

        maxNumberOfRoadsPerJunction = 7
        maxLanePerSide = 2
        minLanePerSide = 0
        
        for sl in range(5):
            path = self.configuration.get("harvested_straight_roads")
            intersection = self.builder.createWithRandomLaneConfigurations(path, 
                                sl, 
                                maxNumberOfRoadsPerJunction=maxNumberOfRoadsPerJunction, 
                                maxLanePerSide=maxLanePerSide, 
                                minLanePerSide=minLanePerSide, 
                                internalConnections=True, 
                                cp1=pyodrx.ContactPoint.end,
                                internalLinkStrategy = LaneConfigurationStrategies.SPLIT_ANY,
                                equalAngles=True,
                                getAsOdr=False)


            odr = intersection.odr
            # xmlPath = f"output/test_createWithRandomLaneConfigurations-split-any-{maxNumberOfRoadsPerJunction}-{sl}.xodr"
            xmlPath = f"output/seed-{self.seed}-{maxNumberOfRoadsPerJunction}-way-{sl}.xodr"
            odr.write_xml(xmlPath)
            extensions.printRoadPositions(odr)
            isValid = self.validator.validateIncidentPoints(intersection, self.builder.minConnectionLength)
            # if isValid == False:
            #     print(f"{sl} is an invalid intersection")
            plt = extensions.view_road(odr,os.path.join('..',self.configuration.get("esminipath")), returnPlt=True)
            if isValid == False:
                plt.title(f"Invalid - {xmlPath}")
            else:
                plt.title(f"Valid - {xmlPath}")
            plt.show()
            extensions.saveRoadImageFromFile(xmlPath, self.configuration.get("esminipath"))

            
    def test_8PlusWayJunctions(self):

        maxNumberOfRoadsPerJunction = 20
        maxLanePerSide = 2
        minLanePerSide = 0
        
        for sl in range(5):
            path = self.configuration.get("harvested_straight_roads")
            odr = self.builder.createWithRandomLaneConfigurations(path, 
                                0, 
                                maxNumberOfRoadsPerJunction=maxNumberOfRoadsPerJunction, 
                                maxLanePerSide=maxLanePerSide, 
                                minLanePerSide=minLanePerSide, 
                                internalConnections=True, 
                                cp1=pyodrx.ContactPoint.end,
                                internalLinkStrategy = LaneConfigurationStrategies.SPLIT_ANY)

            # xmlPath = f"output/test_createWithRandomLaneConfigurations-split-any-{maxNumberOfRoadsPerJunction}-{sl}.xodr"
            xmlPath = f"output/seed-{self.seed}-{maxNumberOfRoadsPerJunction}-way-{sl}.xodr"
            odr.write_xml(xmlPath)
            
            # extensions.view_road(odr,os.path.join('..',self.configuration.get("esminipath")))
            extensions.saveRoadImageFromFile(xmlPath, self.configuration.get("esminipath"))
            maxNumberOfRoadsPerJunction += 1

    def test_4WayJunctionsEqualAngles(self):

        maxNumberOfRoadsPerJunction = 4
        maxLanePerSide = 1
        minLanePerSide = 1
        
        for sl in range(5):
            path = self.configuration.get("harvested_straight_roads")
            odr = self.builder.createWithRandomLaneConfigurations(path, 
                                0, 
                                maxNumberOfRoadsPerJunction=maxNumberOfRoadsPerJunction, 
                                maxLanePerSide=maxLanePerSide, 
                                minLanePerSide=minLanePerSide, 
                                internalConnections=True, 
                                cp1=pyodrx.ContactPoint.end,
                                internalLinkStrategy = LaneConfigurationStrategies.SPLIT_ANY,
                                equalAngles=True)

            # xmlPath = f"output/test_createWithRandomLaneConfigurations-split-any-{maxNumberOfRoadsPerJunction}-{sl}.xodr"
            xmlPath = f"output/seed-{self.seed}-{maxNumberOfRoadsPerJunction}-way-eq-{sl}.xodr"
            odr.write_xml(xmlPath)
            
            extensions.view_road(odr,os.path.join('..',self.configuration.get("esminipath")))
            extensions.saveRoadImageFromFile(xmlPath, self.configuration.get("esminipath"))


    def test_SafeMinConnectionLengthForEqualAngle(self):
    
        sl = 0
        
        maxNumberOfRoadsPerJunction = 8
        sl += 1
        path = self.configuration.get("harvested_straight_roads")
        odr = self.builder.createWithRandomLaneConfigurations(path, 
                            0, 
                            maxNumberOfRoadsPerJunction=maxNumberOfRoadsPerJunction, 
                            maxLanePerSide=3, minLanePerSide=0, 
                            internalConnections=True, 
                            cp1=pyodrx.ContactPoint.end,
                            internalLinkStrategy = LaneConfigurationStrategies.SPLIT_ANY,
                            restrictedLanes=1,
                            equalAngles=True)
        extensions.view_road(odr,os.path.join('..',self.configuration.get("esminipath")))
        xmlPath = f"output/test_createWithRandomLaneConfigurations-split-any-{maxNumberOfRoadsPerJunction}-{sl}.xodr"
        odr.write_xml(xmlPath)
        
        maxNumberOfRoadsPerJunction = 8
        sl += 1
        path = self.configuration.get("harvested_straight_roads")
        odr = self.builder.createWithRandomLaneConfigurations(path, 
                            0, 
                            maxNumberOfRoadsPerJunction=maxNumberOfRoadsPerJunction, 
                            maxLanePerSide=2, minLanePerSide=0, 
                            internalConnections=True, 
                            cp1=pyodrx.ContactPoint.end,
                            internalLinkStrategy = LaneConfigurationStrategies.SPLIT_ANY,
                            restrictedLanes=1,
                            equalAngles=True)
        extensions.view_road(odr,os.path.join('..',self.configuration.get("esminipath")))
        xmlPath = f"output/test_createWithRandomLaneConfigurations-split-any-{maxNumberOfRoadsPerJunction}-{sl}.xodr"
        odr.write_xml(xmlPath)
        
        maxNumberOfRoadsPerJunction = 8
        sl += 1
        path = self.configuration.get("harvested_straight_roads")
        odr = self.builder.createWithRandomLaneConfigurations(path, 
                            0, 
                            maxNumberOfRoadsPerJunction=maxNumberOfRoadsPerJunction, 
                            maxLanePerSide=2, minLanePerSide=0, 
                            internalConnections=True, 
                            cp1=pyodrx.ContactPoint.end,
                            internalLinkStrategy = LaneConfigurationStrategies.SPLIT_ANY,
                            restrictedLanes=1,
                            equalAngles=True)
        extensions.view_road(odr,os.path.join('..',self.configuration.get("esminipath")))
        xmlPath = f"output/test_createWithRandomLaneConfigurations-split-any-{maxNumberOfRoadsPerJunction}-{sl}.xodr"
        odr.write_xml(xmlPath)
        
        maxNumberOfRoadsPerJunction = 8
        sl += 1
        path = self.configuration.get("harvested_straight_roads")
        odr = self.builder.createWithRandomLaneConfigurations(path, 
                            0, 
                            maxNumberOfRoadsPerJunction=maxNumberOfRoadsPerJunction, 
                            maxLanePerSide=2, minLanePerSide=0, 
                            internalConnections=True, 
                            cp1=pyodrx.ContactPoint.end,
                            internalLinkStrategy = LaneConfigurationStrategies.SPLIT_ANY,
                            restrictedLanes=1,
                            equalAngles=True)
        extensions.view_road(odr,os.path.join('..',self.configuration.get("esminipath")))
        xmlPath = f"output/test_createWithRandomLaneConfigurations-split-any-{maxNumberOfRoadsPerJunction}-{sl}.xodr"
        odr.write_xml(xmlPath)
