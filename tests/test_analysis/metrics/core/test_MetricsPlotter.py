import unittest
import os
from analysis.core.MetricsPlotter import MetricsPlotter
import seaborn as sns

class test_MetricsPlotter(unittest.TestCase):

    def setUp(self) -> None:
        
        path= os.path.join(os.getcwd(), 'analysis/output')

        date = "randlane/2021-08-21"

        incidentPath = f"{path}/{date}-incidentRoadDF.csv"
        connectionPath = f"{path}/{date}-connectionRoadDF.csv"
        intersectionPath = f"{path}/{date}-intersectionDF.csv"

        self.plotter = MetricsPlotter(incidentPath=incidentPath, connectionPath=connectionPath, intersectionPath=intersectionPath)
    

    def test_Incident_Histo(self):
        self.plotter.plotIncidentHist(subplots=True)

    def test_IncidentDistribution(self):
        self.plotter.plotIncidentDistributions(subplots=True)

    # def test_Incident_Complexity(self):
    #     self.plotter.plotIncidentComplexity(subplots=True)

    def test_Incident_HeatMaps_Complexity(self):
        sns.set_context("talk")
        self.plotter.plotIncidentHeatMapsComplexity()

    def test_Incident_HeatMaps_ComplexityMax(self):
        sns.set_context("talk")
        self.plotter.plotIncidentHeatMapsComplexityMax()


    def test_plotIncidentHeatMapsCurvatureFov(self):
        # sns.set_context("talk")
        self.plotter.plotIncidentHeatMapsCurvatureFov()
    def test_Incident_ComplexityRelation(self):
        self.plotter.plotIncidentComplexityVs()

    
    def test_Connection_Curvature(self):
        # sns.color_palette("Paired")
        sns.set_context("talk")
        self.plotter.plotConnectionPropertyHistGroupedByLegs("turnCurvature")

    def test_Incident_Curvature(self):
        # sns.color_palette("viridis", as_cmap=True)
        sns.set_context("talk")
        self.plotter.plotIncidentPropertyHistGroupedByLegs("maxCurvature")

    def test_Incident_Complexity(self):
        # sns.color_palette("viridis", as_cmap=True)
        sns.set_context("talk")
        self.plotter.plotIncidentPropertyHistGroupedByLegs("complexity_avg")

    def test_Incident_FOV(self):
        # sns.color_palette("viridis", as_cmap=True)
        sns.set_context("talk")
        self.plotter.plotIncidentPropertyHistGroupedByLegs("fov")

    def test_Incident_Deviation(self):
        # sns.color_palette("viridis", as_cmap=True)
        sns.set_context("talk")
        self.plotter.plotIncidentPropertyHistGroupedByLegs("cornerDeviation")

    
    def test_plotIntersectionPropertyHistGroupedByLegs(self):
        sns.set_context("talk")
        self.plotter.plotIntersectionPropertyHist("numberOfIncidentRoads", xlabel="nIncidentRoads", kde=False)
        self.plotter.plotIntersectionPropertyHistGroupedByLegs("numberOfConnectionRoads", xlabel="nConnectionRoads")
        self.plotter.plotIntersectionPropertyHistGroupedByLegs("area")
        self.plotter.plotIntersectionPropertyHistGroupedByLegs("conflictArea")
        self.plotter.plotIntersectionPropertyHistGroupedByLegs("conflictRatio")
        # sns.plotIntersectionPropertyHistGroupedByLegs("conflictArea")

    
    
    def test_plotIntersectionHeatmaps(self):
        # sns.set_context("talk")
        self.plotter.plotIntersectionHeatMaps(scale=10)

    
    def test_printIntersectionHead(self):
        self.plotter.printIntersectionHead()
