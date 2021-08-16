import unittest
import extensions, os, dill
import numpy as np
import pyodrx
import logging
from library.Configuration import Configuration
from junctions.SequentialJunctionBuilder import SequentialJunctionBuilder
from junctions.LaneConfiguration import LaneConfigurationStrategies
from junctions.IntersectionValidator import IntersectionValidator
from analysis.metrics.travel.ConnectionRoadComplexity import ConnectionRoadComplexity
from analysis.metrics.MetricManager import MetricManager

from analysis.core.Histogram import Histogram
from analysis.core.ScatterPlot import ScatterPlot
logging.basicConfig(level=logging.ERROR)


class test_MetricManager(unittest.TestCase):

    def setUp(self):
        
        self.configuration = Configuration()
        self.outputDir= os.path.join(os.getcwd(), 'analysis/output')
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
    
    def getNwayOnly(self, intersections, n):
        filtered = []
        for intersection in intersections:
            if len(intersection.incidentRoads) == n:
                filtered.append(intersection)
        return filtered

    def loadIntersections(self, path):
        intersections = None
        with open(path, 'rb') as handler:
            intersections = dill.load(handler)
        return intersections

    def createIntersections(self, maxN=3):

        minLanePerSide = 1
        maxLanePerSide = 2

        intersections = []
        
        for sl in range(maxN):
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

            isValid = self.validator.validateIncidentPoints(intersection, self.builder.minConnectionLength)
            if isValid:
                intersections.append(intersection)
            print(f"Created {len(intersections)} intersections")

        return intersections


    
    def test_export(self):
        # intersections = self.createIntersections(50)
        intersections = self.loadIntersections("output/CL-intersections-10000.dill")
        # intersections = intersections[:50]
        print(f"Created {len(intersections)} intersections")
        metricManager = MetricManager(intersections)
        metricManager.exportDataframes(path=self.outputDir)

        
    def test_export2Lane(self):
        # intersections = self.createIntersections(50)
        intersections = self.loadIntersections("output/CL-intersections-2lane-10000.dill")
        # intersections = intersections[:50]
        print(f"Created {len(intersections)} intersections")
        metricManager = MetricManager(intersections)
        metricManager.exportDataframes(path=self.outputDir)


    def test_TurnHisto(self):

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
            # extensions.view_road(intersection.odr,os.path.join('..',self.configuration.get("esminipath")))

        metricManager = MetricManager(intersections)

        turnComplexities = metricManager.getNormalizedTurnComplexities()
        print(turnComplexities)
        # Histogram.plotNormalizedMetrics(turnComplexities, 'turn complexity')
        bins = 10
        print(metricManager.connectionRoadDF.head())
        Histogram.plotNormalizedMetricsDF(metricManager.connectionRoadDF, 'turnCurvature', 'turn Curvature', bins=bins)
        Histogram.plot2MetricsDF(metricManager.connectionRoadDF, 'turnCurvature', 'legs', bins=bins)
        Histogram.plot2StackedMetricsDF(metricManager.connectionRoadDF, 'turnCurvature', 'legs', bins=bins)
        Histogram.plot2MetricsDFSep(metricManager.connectionRoadDF, 'turnCurvature', 'legs', bins=bins)


    def test_TurnScatter(self):

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
        
        metricManager = MetricManager(intersections)

        turnComplexities = metricManager.getNormalizedTurnComplexities()
        print(turnComplexities)
        # Histogram.plotNormalizedMetrics(turnComplexities, 'turn complexity')
        
        ScatterPlot.plot2MetricsDF(metricManager.connectionRoadDF, 'turnComplexities', 'numberOfIncidentRoads')