import unittest
import os
from analysis.core.MetricsPlotter import MetricsPlotter

class test_MetricsPlotter(unittest.TestCase):

    def setUp(self) -> None:
        
        path= os.path.join(os.getcwd(), 'analysis/output')

        incidentPath = f"{path}/2021-08-14-incidentRoadDF.csv"
        connectionPath = f"{path}/2021-08-14-connectionRoadDF.csv"
        intersectionPath = f"{path}/2021-08-14-intersectionDF.csv"

        self.plotter = MetricsPlotter(incidentPath=incidentPath, connectionPath=connectionPath, intersectionPath=intersectionPath)
    

    def test_Incident_Histo(self):
        self.plotter.plotIncidentHist(subplots=True)

    def test_IncidentDistribution(self):
        self.plotter.plotIncidentDistributions(subplots=True)

    def test_Incident_Complexity(self):
        self.plotter.plotIncidentComplexity(subplots=True)

    def test_Incident_HeatMaps(self):
        self.plotter.plotIncidentHeatMaps()
    def test_Incident_ComplexityRelation(self):
        self.plotter.plotIncidentComplexityVs()