import unittest
import extensions, os
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
logging.basicConfig(level=logging.INFO)


class test_MetricManager(unittest.TestCase):

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
        Histogram.plotNormalizedConnectionRoadDF(metricManager.connectionRoadDF, 'turnComplexities', 'turn complexity', bins=bins)
        Histogram.plot2ConnectionRoadDF(metricManager.connectionRoadDF, 'turnComplexities', 'numberOfIncidentRoads', bins=bins)
        Histogram.plot2StackedConnectionRoadDF(metricManager.connectionRoadDF, 'turnComplexities', 'numberOfIncidentRoads', bins=bins)
        Histogram.plot2ConnectionRoadDFSep(metricManager.connectionRoadDF, 'turnComplexities', 'numberOfIncidentRoads', bins=bins)


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