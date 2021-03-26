import unittest
from junctions.SequentialJunctionBuilder import SequentialJunctionBuilder
import extensions, os
import numpy as np
from library.Configuration import Configuration
from junctions.LaneConfiguration import LaneConfigurationStrategies
import pyodrx
import logging
logging.basicConfig(level=logging.INFO)

class test_SequentialJunctionBuilder(unittest.TestCase):

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
                            internalLinkStrategy = LaneConfigurationStrategies.SPLIT_ANY,
                            restrictedLanes=1)

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
                            restrictedLanes=1,
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

    def test_4WayJunctions(self):

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
                                internalLinkStrategy = LaneConfigurationStrategies.SPLIT_ANY)

            # xmlPath = f"output/test_createWithRandomLaneConfigurations-split-any-{maxNumberOfRoadsPerJunction}-{sl}.xodr"
            xmlPath = f"output/seed-{self.seed}-{maxNumberOfRoadsPerJunction}-way-{sl}.xodr"
            odr.write_xml(xmlPath)
            
            extensions.view_road(odr,os.path.join('..',self.configuration.get("esminipath")))
            extensions.saveRoadImageFromFile(xmlPath, self.configuration.get("esminipath"))


    def test_5WayJunctions(self):

        maxNumberOfRoadsPerJunction = 5
        maxLanePerSide = 3
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

    def test_6WayJunctions(self):

        maxNumberOfRoadsPerJunction = 6
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


    def test_7WayJunctions(self):

        maxNumberOfRoadsPerJunction = 7
        maxLanePerSide = 2
        minLanePerSide = 0
        
        for sl in range(20):
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

    def test_7WayJunctionsEQA(self):

        maxNumberOfRoadsPerJunction = 7
        maxLanePerSide = 2
        minLanePerSide = 0
        
        for sl in range(20):
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
            xmlPath = f"output/seed-{self.seed}-{maxNumberOfRoadsPerJunction}-way-{sl}.xodr"
            odr.write_xml(xmlPath)
            
            # extensions.view_road(odr,os.path.join('..',self.configuration.get("esminipath")))
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
