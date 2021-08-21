import unittest, math, dill
from roadgen.controlLine.ControlPointIntersectionAdapter import ControlPointIntersectionAdapter
from roadgen.controlLine.ControlPoint import ControlPoint
from library.Configuration import Configuration
from extensions.CountryCodes import CountryCodes
from junctions.JunctionBuilderFromPointsAndHeading import JunctionBuilderFromPointsAndHeading
from roadgen.controlLine.ControlLineBasedGenerator import ControlLineBasedGenerator
import extensions, os, logging
import numpy as np
import traceback
logfile = 'ControlLineBasedGenerator.log'
logging.basicConfig(level=logging.INFO, filename=logfile)


class test_ControlLineBasedGenerator(unittest.TestCase):


    def setUp(self) -> None:
        self.configuration = Configuration()
        self.outputDir= os.path.join(os.getcwd(), 'output')
        with open(logfile, 'w') as f:
            f.truncate()
        pass
    

    def test_generateWithManualControlLines(self):
        generator = ControlLineBasedGenerator((400, 400), debug=True, seed=10, randomizeDistance=False, nLaneDistributionOnASide=[0.2, 0.7, 0.1, 0])
        odr = generator.generateWithManualControlines("test_generateWithHorizontalControlines")
        # generator.grid.plot()
        # extensions.printRoadPositions(odr)
        xmlPath = f"output/test_generateWithManualControlLines.xodr"
        odr.write_xml(xmlPath)
        # extensions.view_road(odr, os.path.join('..',self.configuration.get("esminipath"))) 


    def test_generateWithManualControlLines2(self):
        generator = ControlLineBasedGenerator((400, 400), debug=True, seed=10, randomizeDistance=False, nLaneDistributionOnASide=[0.2, 0.7, 0.1, 0], nLaneDistributionOnControlLines=[0, 0.2, 0.7, 0.1])
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
        odr = generator.generateWithManualControlines("test_mapA", layout='A')

        # xmlPath = f"output/test_generateWithManualControlLines2.xodr"
        # odr.write_xml(xmlPath)
        extensions.view_road(odr, os.path.join('..',self.configuration.get("esminipath"))) 
