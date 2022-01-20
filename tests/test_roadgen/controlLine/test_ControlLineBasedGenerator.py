import unittest, math, dill
from junctionart.roadgen.controlLine.ControlPointIntersectionAdapter import ControlPointIntersectionAdapter
from junctionart.roadgen.controlLine.ControlPoint import ControlPoint
from junctionart.library.Configuration import Configuration
from junctionart.extensions.CountryCodes import CountryCodes
from junctionart.junctions.JunctionBuilderFromPointsAndHeading import JunctionBuilderFromPointsAndHeading
from junctionart.roadgen.controlLine.ControlLineBasedGenerator import ControlLineBasedGenerator
import junctionart.extensions as extensions, os, logging
import numpy as np
import traceback
import time
from tabulate import tabulate

import psutil

logfile = 'ControlLineBasedGenerator.log'
logging.basicConfig(level=logging.WARNING, filename=logfile)


class test_ControlLineBasedGenerator(unittest.TestCase):


    def setUp(self) -> None:
        self.configuration = Configuration()
        self.outputDir= os.path.join(os.getcwd(), 'output')
        with open(logfile, 'w') as f:
            f.truncate()
        pass
    

    def test_generateWithManualControlLines(self):
        generator = ControlLineBasedGenerator((400, 400), debug=True, seed=3, randomizeDistance=False, nLaneDistributionOnASide=[0.2, 0.7, 0.1, 0])
        odr = generator.generateWithManualControlines("test_generateWithHorizontalControlines")
        # generator.grid.plot()
        # extensions.printRoadPositions(odr)
        xmlPath = f"output/test_generateWithManualControlLines.xodr"
        odr.write_xml(xmlPath)
        extensions.view_road(odr, os.path.join('..',self.configuration.get("esminipath"))) 


    def test_generateWithManualControlLines2(self):
        generator = ControlLineBasedGenerator((400, 400), debug=True, seed=2, randomizeDistance=False, nLaneDistributionOnASide=[0.2, 0.7, 0.1, 0], nLaneDistributionOnControlLines=[0, 0.2, 0.7, 0.1])
        odr = generator.generateWithManualControlines("test_generateWithHorizontalControlines2")
        # generator.grid.plot()
        # extensions.printRoadPositions(odr)
        xmlPath = f"output/test_generateWithManualControlLines2.xodr"
        odr.write_xml(xmlPath)
        # extensions.view_road(odr, os.path.join('..',self.configuration.get("esminipath"))) 


    def test_generateWithHorizontalControlines(self):

        for seed in range(1,20):
            try:
                generator = ControlLineBasedGenerator((600, 600), debug=True, seed=seed, randomizeDistance=False, randomizeHeading=True)
                odr = generator.generateWithHorizontalControlines("test_generateWithHorizontalControlines", 4, plotGrid=False)

                # xmlPath = f"output/test_generateWithHorizontalControlines.xodr"
                # odr.write_xml(xmlPath)
                extensions.view_road(odr, os.path.join('..',self.configuration.get("esminipath"))) 
            except:
                pass

    def test_generateWithHorizontalControlinesCurvy(self):

        generator = ControlLineBasedGenerator((800, 800), debug=True, seed=1, randomizeDistance=True, randomizeHeading=True)
        odr = generator.generateWithHorizontalControlines("test_generateWithHorizontalControlinesCurvy", 5)
        # generator.grid.plot()
        # extensions.printRoadPositions(odr)
        xmlPath = f"output/test_generateWithHorizontalControlinesCurvy.xodr"
        odr.write_xml(xmlPath)
        # extensions.view_road(odr, os.path.join('..',self.configuration.get("esminipath"))) 

    def test_generateWithHorizontalControlinesBig(self):
        generator = ControlLineBasedGenerator((5000, 5000), debug=True, seed=1, randomizeDistance=False, nLaneDistributionOnASide=[0.25, 0.7, 0.05, 0])
        odr = generator.generateWithHorizontalControlines("test_generateWithHorizontalControlinesBig", 20)
        # generator.grid.plot()
        # extensions.printRoadPositions(odr)
        xmlPath = f"output/test_generateWithHorizontalControlinesBig.xodr"
        odr.write_xml(xmlPath)
        extensions.view_road(odr, os.path.join('..',self.configuration.get("esminipath"))) 

    def test_generateWithHorizontalControlinesBig2Lane(self):
        generator = ControlLineBasedGenerator((2000, 2000), debug=True, seed=1, randomizeLanes=False, randomizeDistance=False)
        odr = generator.generateWithHorizontalControlines("test_generateWithHorizontalControlinesBig2Lane", 10)
        # generator.grid.plot()
        # extensions.printRoadPositions(odr)
        xmlPath = f"output/test_generateWithHorizontalControlinesBig2Lane.xodr"
        odr.write_xml(xmlPath)
        # extensions.view_road(odr, os.path.join('..',self.configuration.get("esminipath"))) 

    
    def test_export2LaneIntersections(self):

        intersections = []
        numberOfIntersections = 10000
        outputPath = os.path.join(self.outputDir, f"CL-intersections-2lane-{numberOfIntersections}.dill")

        created = 0
        # create 
        while created < numberOfIntersections:
            try:
                seed = np.random.randint(1, numberOfIntersections * 1000)
                generator = ControlLineBasedGenerator((2000, 2000), debug=True, seed=seed, randomizeLanes=False, randomizeDistance=False)
                generator.generateWithHorizontalControlines("test_generateWithHorizontalControlinesBig2Lane", 10, plotGrid=False, stopAfterCreatingIntersections=True)
                newIntersections = generator.getIntersections()
                intersections += newIntersections
                created += len(newIntersections)
                print(f"generated {created}")
            except Exception as e:
                print(e)
                traceback.print_exc(limit=2)
                pass
        with open(outputPath, 'wb') as handler:
            print(f"writing out {len(intersections)}")
            dill.dump(intersections, handler)

    def test_exportIntersections(self):

        intersections = []
        numberOfIntersections = 100
        outputPath = os.path.join(self.outputDir, f"CL-intersections-{numberOfIntersections}.dill")

        created = 0
        # create 
        while created < numberOfIntersections:
            try:
                seed = np.random.randint(1, numberOfIntersections * 1000)
                generator = ControlLineBasedGenerator((2000, 2000), debug=True, seed=seed, randomizeLanes=True, randomizeDistance=False)
                generator.generateWithHorizontalControlines("test_generateWithHorizontalControlinesBig2Lane", 10, plotGrid=False, stopAfterCreatingIntersections=True)
                newIntersections = generator.getIntersections()
                intersections += newIntersections
                created += len(newIntersections)
                print(f"generated {created}")
            except Exception as e:
                print(e)
                traceback.print_exc(limit=2)
                pass
        with open(outputPath, 'wb') as handler:
            print(f"writing out {len(intersections)}")
            print(dill.dump(intersections, handler))
            
    def test_generateWithA(self):
        generator = ControlLineBasedGenerator((400, 400), debug=True, seed=1, randomizeHeading=True, randomizeDistance=False, nLaneDistributionOnASide=[0.2, 0.7, 0.1, 0], nLaneDistributionOnControlLines=[0, 0.2, 0.7, 0.1])

        for _ in range(2):
            odr = generator.generateWithManualControlines("test_mapA", layout='A', plotGrid=False)

            # xmlPath = f"output/test_generateWithManualControlLines2.xodr"
            # odr.write_xml(xmlPath)
            extensions.view_road(odr, os.path.join('..',self.configuration.get("esminipath"))) 


    def test_running_time(self):

        heading = ["test configuration", "#tries", "#success", "total time (minutes)", "time per map (seconds)", "memory (MB)"]
        stats = []

        # count = 50
        # mapsize=(500, 500)
        # # goal generate count 400x400 maps with 2 lanes
        # tryCount, successCount, durationInMin, averageInSec, memory = self.getRunningTimeStatsFor1000Maps(mapsize=mapsize, randomizeLanes=False, nControlLine=3, count=count)
        # # print(f"tries: {tryCount}, success: {successCount}, time: {durationInMin} Seconds, averageInSec: {averageInSec}")
        # stats.append([f"{count} {mapsize} square meter maps with 2 lanes", tryCount, successCount, durationInMin, averageInSec, memory])

        # # goal generate count 400x400 maps with random lanes
        # tryCount, successCount, durationInMin, averageInSec, memory = self.getRunningTimeStatsFor1000Maps(mapsize=mapsize, randomizeLanes=True, nControlLine=3, count=count)
        # stats.append([f"{count} {mapsize} square meter maps with random lanes", tryCount, successCount, durationInMin, averageInSec, memory])

        # count = 50
        # mapsize=(1000, 1000)
        # # 2 lanes
        # tryCount, successCount, durationInMin, averageInSec, memory= self.getRunningTimeStatsFor1000Maps(mapsize=mapsize, randomizeLanes=False, nControlLine=6, count=count)
        # stats.append([f"{count} {mapsize} square meter maps with 2 lanes", tryCount, successCount, durationInMin, averageInSec, memory])

        # # random lanes
        # tryCount, successCount, durationInMin, averageInSec, memory= self.getRunningTimeStatsFor1000Maps(mapsize=mapsize, randomizeLanes=True, nControlLine=6, count=count)
        # stats.append([f"{count} {mapsize} square meter maps with random lanes", tryCount, successCount, durationInMin, averageInSec, memory])

        count = 50
        mapsize=(5000, 5000)
        # 2 lanes
        tryCount, successCount, durationInMin, averageInSec, memory= self.getRunningTimeStatsFor1000Maps(mapsize=mapsize, randomizeLanes=False, nControlLine=25, count=count)
        stats.append([f"{count} {mapsize} square meter maps with 2 lanes", tryCount, successCount, durationInMin, averageInSec, memory])

        # random lanes
        tryCount, successCount, durationInMin, averageInSec, memory= self.getRunningTimeStatsFor1000Maps(mapsize=mapsize, randomizeLanes=True, nControlLine=25, count=count)
        stats.append([f"{count} {mapsize} square meter maps with random lanes", tryCount, successCount, durationInMin, averageInSec, memory])

        # # count = 4
        # # mapsize=(10000, 10000)
        # # # 2 lanes
        # # tryCount, successCount, durationInMin, averageInSec, memory= self.getRunningTimeStatsFor1000Maps(mapsize=mapsize, randomizeLanes=False, nControlLine=50, count=count)
        # # stats.append([f"{count} {mapsize} square meter maps with 2 lanes", tryCount, successCount, durationInMin, averageInSec, memory])

        # # # random lanes
        # # tryCount, successCount, durationInMin, averageInSec, memory= self.getRunningTimeStatsFor1000Maps(mapsize=mapsize, randomizeLanes=True, nControlLine=50, count=count)
        # # stats.append([f"{count} {mapsize} square meter maps with random lanes", tryCount, successCount, durationInMin, averageInSec, memory])

        # # test with manual
        # count = 50
        # mapsize=(1200, 1400)
        # # goal generate count 400x400 maps with 2 lanes
        # tryCount, successCount, durationInMin, averageInSec, memory = self.getRunningTimeStatsFor1000ManualMaps(mapsize=mapsize, randomizeLanes=False, nControlLine=3, count=count)
        # # print(f"tries: {tryCount}, success: {successCount}, time: {durationInMin} Seconds, averageInSec: {averageInSec}")
        # stats.append([f"{count} {mapsize} manual control-line maps with 2 lanes", tryCount, successCount, durationInMin, averageInSec, memory])

        # # goal generate count 400x400 maps with random lanes
        # tryCount, successCount, durationInMin, averageInSec, memory = self.getRunningTimeStatsFor1000ManualMaps(mapsize=mapsize, randomizeLanes=True, nControlLine=3, count=count)
        # stats.append([f"{count} {mapsize} manual control-line maps with random lanes", tryCount, successCount, durationInMin, averageInSec, memory])

        # # test with A
        # count = 50
        # mapsize=(1000, 1600)
        # # goal generate count 400x400 maps with 2 lanes
        # tryCount, successCount, durationInMin, averageInSec, memory = self.getRunningTimeStatsFor1000AMaps(mapsize=mapsize, randomizeLanes=False, nControlLine=3, count=count)
        # # print(f"tries: {tryCount}, success: {successCount}, time: {durationInMin} Seconds, averageInSec: {averageInSec}")
        # stats.append([f"{count} {mapsize} A-shaped maps with 2 lanes", tryCount, successCount, durationInMin, averageInSec, memory])

        # # goal generate count 400x400 maps with random lanes
        # tryCount, successCount, durationInMin, averageInSec, memory = self.getRunningTimeStatsFor1000AMaps(mapsize=mapsize, randomizeLanes=True, nControlLine=3, count=count)
        # stats.append([f"{count} {mapsize} A-shaped maps with random lanes", tryCount, successCount, durationInMin, averageInSec, memory])


        print("\n")
        print(tabulate(stats, headers=heading))
        print("\n")


        pass

    

    def getRunningTimeStatsFor1000Maps(self, mapsize, randomizeLanes, nControlLine, count = 100):

        tryCount = 0
        successCount = 0
        startNS = time.process_time_ns()
        for seed in range(1, count * 20):
            tryCount += 1
            try:
                generator = ControlLineBasedGenerator(mapsize, debug=False, seed=seed, randomizeLanes=randomizeLanes, randomizeDistance=False, randomizeHeading=False)
                odr = generator.generateWithHorizontalControlines("test_generateWithHorizontalControlines", nControlLine, plotGrid=False)

                # xmlPath = f"output/test_generateWithHorizontalControlines.xodr"
                # odr.write_xml(xmlPath)
                # extensions.view_road(odr, os.path.join('..',self.configuration.get("esminipath"))) 
                successCount += 1

                print(f"success {successCount}/{tryCount}")
                if successCount == count:
                    break
            except:
                pass

        endNS = time.process_time_ns()

        # memory stats
        process = psutil.Process(os.getpid())
        memory = round(process.memory_info().rss / (1024 * 1024), 2) # MB
        # extensions.view_road(odr, os.path.join('..',self.configuration.get("esminipath"))) 

        # durationInSec = round((endNS - startNS) / 1_000_000_000, 2)
        durationInMin = round((endNS - startNS) / 60_000_000_000, 2)
        averageInSec = round((endNS - startNS)  / (successCount * 1_000_000_000), 2)

        # print(f"memory1 : {memory1}")

        return tryCount, successCount, durationInMin, averageInSec, memory


    def getRunningTimeStatsFor1000ManualMaps(self, mapsize, randomizeLanes, nControlLine, count = 100):

        tryCount = 0
        successCount = 0
        startNS = time.process_time_ns()
        for seed in range(1, count * 2):
            tryCount += 1
            try:
                generator = ControlLineBasedGenerator(mapsize, debug=False, seed=seed, randomizeLanes=randomizeLanes, randomizeDistance=False, randomizeHeading=False)
                odr = generator.generateWithManualControlines("test_generateWithHorizontalControlines", plotGrid = False)

                # xmlPath = f"output/test_generateWithHorizontalControlines.xodr"
                # odr.write_xml(xmlPath)
                # extensions.view_road(odr, os.path.join('..',self.configuration.get("esminipath"))) 
                successCount += 1
                if successCount == count:
                    break
            except:
                pass

        endNS = time.process_time_ns()

        # memory stats
        process = psutil.Process(os.getpid())
        memory = round(process.memory_info().rss / (1024 * 1024), 2) # MB
        # extensions.view_road(odr, os.path.join('..',self.configuration.get("esminipath"))) 

        # durationInSec = round((endNS - startNS) / 1_000_000_000, 2)
        durationInMin = round((endNS - startNS) / 60_000_000_000, 2)
        averageInSec = round((endNS - startNS)  / (successCount * 1_000_000_000), 2)

        # print(f"memory1 : {memory1}")

        return tryCount, successCount, durationInMin, averageInSec, memory

        
    def getRunningTimeStatsFor1000AMaps(self, mapsize, randomizeLanes, nControlLine, count = 100):

        tryCount = 0
        successCount = 0
        startNS = time.process_time_ns()
        for seed in range(1, count * 2):
            tryCount += 1
            try:
                generator = ControlLineBasedGenerator(mapsize, debug=False, seed=seed, randomizeLanes=randomizeLanes, randomizeDistance=False, randomizeHeading=False)
                odr = generator.generateWithManualControlines("test_mapA", layout='A', plotGrid=False)

                # xmlPath = f"output/test_generateWithHorizontalControlines.xodr"
                # odr.write_xml(xmlPath)
                # extensions.view_road(odr, os.path.join('..',self.configuration.get("esminipath"))) 
                successCount += 1
                if successCount == count:
                    break
            except:
                pass

        endNS = time.process_time_ns()

        # memory stats
        process = psutil.Process(os.getpid())
        memory = round(process.memory_info().rss / (1024 * 1024), 2) # MB
        # extensions.view_road(odr, os.path.join('..',self.configuration.get("esminipath"))) 

        # durationInSec = round((endNS - startNS) / 1_000_000_000, 2)
        durationInMin = round((endNS - startNS) / 60_000_000_000, 2)
        averageInSec = round((endNS - startNS)  / (successCount * 1_000_000_000), 2)

        # print(f"memory1 : {memory1}")

        return tryCount, successCount, durationInMin, averageInSec, memory