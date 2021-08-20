import pandas as pd
from analysis.core.Histogram import Histogram
import matplotlib.pyplot as plt
import matplotlib.ticker as ticker
import seaborn as sns
import numpy as np
# Apply the default theme
sns.set_theme()


class MetricsPlotter:

    def __init__(self, incidentPath, connectionPath, intersectionPath) -> None:

        self.incidentRoadDF = pd.read_csv(incidentPath)
        self.connectionRoadDF = pd.read_csv(connectionPath)
        self.intersectionDF = pd.read_csv(intersectionPath)

        self.intersectionDF['legs'] = self.intersectionDF['numberOfIncidentRoads']
        self.intersectionDF['conflictRatio'] = self.intersectionDF['conflictArea'] / self.intersectionDF['area']

        plt.rcParams['font.size'] = '24'

        self.normalize()
        pass

    
    def normalize(self):
        self.incidentRoadDFNormalized = self.normalizeWhole(self.incidentRoadDF)
        self.connectionRoadDFNormalized = self.normalizeWhole(self.connectionRoadDF)
        self.intersectionDFNormalized = self.normalizeWhole(self.intersectionDF)

    
    def normalizeWhole(self, df):
        return (df-df.min())/(df.max()-df.min())

    def plotIncidentHist(self, cols=["fov", "cornerDeviation", 'maxCurvature'], subplots=False):

        fig, ax = plt.subplots()
        self.incidentRoadDFNormalized.plot.hist(bins=10, alpha=0.5, ax=ax, y=cols, subplots=subplots)
        ax.set_xlabel("Normalized Scale 0.0 - 1.0)")
        plt.show()
        
        fig, ax = plt.subplots()
        self.incidentRoadDF.plot.hist(bins=10, alpha=0.5, ax=ax, y=cols, subplots=subplots)
        ax.set_xlabel("Angle in Degrees)")
        plt.show()
        return 

    def plotIncidentDistributions(self, cols=["fov", "cornerDeviationNorm", 'maxCurvatureNorm'], subplots=False):

        ax = self.incidentRoadDF.plot.density(y=cols, subplots=subplots)
        plt.show()
        # return ax
        bins=10
        
        data = self.incidentRoadDFNormalized["fov"]
        g = sns.displot(data=data, kde=True, stat="probability", bins=10)
        g.set_axis_labels("Normalized FOV", "Density")
        g.set_titles(f"Density")
        g.set(xlim=(0, 1))
        plt.show()


        data = self.incidentRoadDF["fov"]
        g = sns.displot(data=data, kde=True, stat="probability", bins=10)
        g.set_axis_labels("FOV in degrees", "Density")
        g.set_titles(f"Density")
        g.set(xlim=(0, 180))
        plt.show()


        
        data = self.incidentRoadDFNormalized["maxCurvature"]
        g = sns.displot(data=data, kde=True, stat="probability", bins=10)
        g.set_axis_labels("Normalized max curvature", "Density")
        g.set_titles(f"Density")
        g.set(xlim=(0, 1))
        plt.show()


        data = self.incidentRoadDF["maxCurvature"]
        g = sns.displot(data=data, kde=True, stat="probability", bins=10)
        g.set_axis_labels("max curvature in degrees", "Density")
        g.set_titles(f"Density")
        g.set(xlim=(0, 36))
        plt.show()

        
        g = sns.displot(data=self.incidentRoadDF, x="fov", y="maxCurvature", bins=bins)
        # g.set_axis_labels(name, "Number of Intersections")
        g.set_titles(f"Fov vs Curvature")
        g.set(xlim=(0, 180), ylim=(0, 36))
        plt.show()
        
        g = sns.displot(data=self.incidentRoadDF, x="fov", y="cornerDeviation", bins=bins)
        # g.set_axis_labels(name, "Number of Intersections")
        g.set_titles(f"Fov vs Departure Angle Deviation")
        g.set(xlim=(0, 180), ylim=(0, 90))
        plt.show()

    
    def plotIncidentComplexity(self, subplots=True):
        bins=20
        
        data = self.incidentRoadDF["complexity"]
        g = sns.displot(data=data, kde=True, stat="probability", bins=bins)
        g.set_axis_labels("Incident road complexity", "Density")
        g.set_titles(f"Incident road complexity")
        g.set(xlim=(0, 1))
        plt.show()

        data = self.incidentRoadDF["complexity_max"]
        g = sns.displot(data=data, kde=True, stat="probability", bins=bins)
        g.set_axis_labels("Incident road complexity max", "Density")
        g.set_titles(f"Incident road complexity max")
        g.set(xlim=(0, 1))
        plt.show()

        
        g = sns.displot(data=self.incidentRoadDF, x="complexity", y="maxCurvature", bins=bins)
        # g.set_axis_labels(name, "Number of Intersections")
        g.set_titles(f"Complexity vs Travel Curvature")
        g.set(xlim=(0, 1), ylim=(0, 36))
        plt.show()


    def discretizeIncidentDf(self, bins = 10):

        complexityBins = np.linspace(0, self.incidentRoadDF['complexity'].max(), bins)
        self.incidentRoadDF['complexity-level'] = pd.cut(self.incidentRoadDF['complexity'], bins=complexityBins, labels=False)

        complexityBins = np.linspace(0, self.incidentRoadDF['complexity_avg'].max(), bins)
        self.incidentRoadDF['complexity_avg-level'] = pd.cut(self.incidentRoadDF['complexity_avg'], bins=complexityBins, labels=False)

        complexityMaxBins = np.linspace(0, self.incidentRoadDF['complexity_max'].max(), bins)
        self.incidentRoadDF['complexity_max-level'] = pd.cut(self.incidentRoadDF['complexity_max'], bins=complexityMaxBins, labels=False)

        # curveBins = np.linspace(0, self.incidentRoadDF['maxCurvature'].max(), bins)
        # self.incidentRoadDF['maxCurvature-level'] = pd.cut(self.incidentRoadDF['maxCurvature'], bins=curveBins, labels=False)
        curveBins = np.linspace(0, 45, 45)
        self.incidentRoadDF['maxCurvature-level'] = pd.cut(self.incidentRoadDF['maxCurvature'], bins=curveBins, labels=False)

        # fovLevels = np.linspace(0, self.incidentRoadDF['fov'].max(), )
        # fobBins = np.linspace(0, self.incidentRoadDF['fov'].max(), bins * 6)
        # self.incidentRoadDF['fov-level'] = pd.cut(self.incidentRoadDF['fov'], bins=fobBins, labels=False)
        fobBins = np.linspace(0, 180, 180)
        self.incidentRoadDF['fov-level'] = pd.cut(self.incidentRoadDF['fov'], bins=fobBins, labels=False)

        # cvBins = np.linspace(0, self.incidentRoadDF['cornerDeviation'].max(), bins * 2)
        # self.incidentRoadDF['cornerDeviation-level'] = pd.cut(self.incidentRoadDF['cornerDeviation'], bins=cvBins, labels=False)
        cvBins = np.linspace(0, 90, 90)
        self.incidentRoadDF['cornerDeviation-level'] = pd.cut(self.incidentRoadDF['cornerDeviation'], bins=cvBins, labels=False)
    
    def plotIncidentHeatMapsComplexity(self):

        bins=25
        self.discretizeIncidentDf(bins)
        annot=False

        heatDf = pd.crosstab(self.incidentRoadDF['complexity-level'], self.incidentRoadDF['maxCurvature-level']).div(len(self.incidentRoadDF))
        ax = sns.heatmap(heatDf, annot=annot)
        ax.set_title("Heatmap Curvature & Complexity")
        ax.set_xlabel("Curvature")
        ax.set_ylabel("Complexity")
        ax.xaxis.set_major_locator(ticker.MultipleLocator(5))
        ax.xaxis.set_major_formatter(ticker.ScalarFormatter())
        plt.show()

        heatDf = pd.crosstab(self.incidentRoadDF['complexity-level'], self.incidentRoadDF['fov-level']).div(len(self.incidentRoadDF))
        ax = sns.heatmap(heatDf, annot=annot)
        ax.set_title("Heatmap FOV & Complexity")
        ax.set_xlabel("FOV")
        ax.set_ylabel("Complexity")
        ax.xaxis.set_major_locator(ticker.MultipleLocator(5))
        ax.xaxis.set_major_formatter(ticker.ScalarFormatter())
        plt.show()

        heatDf = pd.crosstab(self.incidentRoadDF['complexity-level'], self.incidentRoadDF['cornerDeviation-level']).div(len(self.incidentRoadDF))
        ax = sns.heatmap(heatDf, annot=annot)
        ax.set_title("Heatmap Deviation-Sight line & Complexity")
        ax.set_xlabel("Deviation form Sight-line")
        ax.set_ylabel("Complexity")
        ax.xaxis.set_major_locator(ticker.MultipleLocator(5))
        ax.xaxis.set_major_formatter(ticker.ScalarFormatter())
        plt.show()

        
        heatDf = pd.crosstab(self.incidentRoadDF['maxCurvature-level'], self.incidentRoadDF['fov-level']).div(len(self.incidentRoadDF))
        ax = sns.heatmap(heatDf, annot=annot)
        ax.set_title("Heatmap FOV & Curvature")
        ax.set_xlabel("FOV")
        ax.set_ylabel("Curvature")
        ax.xaxis.set_major_locator(ticker.MultipleLocator(5))
        ax.xaxis.set_major_formatter(ticker.ScalarFormatter())
        plt.show()


    def plotIncidentHeatMapsComplexityMax(self):

        bins=10
        self.discretizeIncidentDf(bins)
        annot=False
        tickMulti = 2

        heatDf = pd.crosstab(self.incidentRoadDF['complexity_max-level'], self.incidentRoadDF['maxCurvature-level']).div(len(self.incidentRoadDF))
        ax = sns.heatmap(heatDf, annot=annot)
        ax.set_title("Heatmap Curvature & Complexity")
        ax.set_xlabel("Curvature")
        ax.set_ylabel("Complexity")
        ax.xaxis.set_major_locator(ticker.MultipleLocator(tickMulti))
        ax.xaxis.set_major_formatter(ticker.ScalarFormatter())
        ax.yaxis.set_major_locator(ticker.MultipleLocator(tickMulti))
        ax.yaxis.set_major_formatter(ticker.ScalarFormatter())
        plt.show()

        heatDf = pd.crosstab(self.incidentRoadDF['complexity_max-level'], self.incidentRoadDF['fov-level']).div(len(self.incidentRoadDF))
        ax = sns.heatmap(heatDf, annot=annot)
        ax.set_title("Heatmap FOV & Complexity")
        ax.set_xlabel("FOV")
        ax.set_ylabel("Complexity")
        ax.xaxis.set_major_locator(ticker.MultipleLocator(tickMulti))
        ax.xaxis.set_major_formatter(ticker.ScalarFormatter())
        ax.yaxis.set_major_locator(ticker.MultipleLocator(tickMulti))
        ax.yaxis.set_major_formatter(ticker.ScalarFormatter())
        plt.show()

        heatDf = pd.crosstab(self.incidentRoadDF['complexity_max-level'], self.incidentRoadDF['cornerDeviation-level']).div(len(self.incidentRoadDF))
        ax = sns.heatmap(heatDf, annot=annot)
        ax.set_title("Heatmap Deviation-Sight line & Complexity")
        ax.set_xlabel("Deviation Angle form Sight-line")
        ax.set_ylabel("Complexity")
        ax.xaxis.set_major_locator(ticker.MultipleLocator(tickMulti))
        ax.xaxis.set_major_formatter(ticker.ScalarFormatter())
        ax.yaxis.set_major_locator(ticker.MultipleLocator(tickMulti))
        ax.yaxis.set_major_formatter(ticker.ScalarFormatter())
        plt.show()

        
        heatDf = pd.crosstab(self.incidentRoadDF['maxCurvature-level'], self.incidentRoadDF['fov-level']).div(len(self.incidentRoadDF))
        ax = sns.heatmap(heatDf, annot=annot)
        ax.set_title("Heatmap FOV & Curvature")
        ax.set_xlabel("FOV")
        ax.set_ylabel("Curvature")
        ax.xaxis.set_major_locator(ticker.MultipleLocator(tickMulti))
        ax.xaxis.set_major_formatter(ticker.ScalarFormatter())
        ax.yaxis.set_major_locator(ticker.MultipleLocator(tickMulti))
        ax.yaxis.set_major_formatter(ticker.ScalarFormatter())
        plt.show()

    def plotIncidentHeatMapsCurvatureFov(self):

        bins=50
        self.discretizeIncidentDf(bins)
        annot=False
        tickMulti = 5
        
        heatDf = pd.crosstab(self.incidentRoadDF['maxCurvature-level'], self.incidentRoadDF['fov-level']).div(len(self.incidentRoadDF))
        ax = sns.heatmap(heatDf, annot=annot)
        ax.set_title("Heatmap FOV & maxCurvature")
        ax.set_xlabel("FOV")
        ax.set_ylabel("maxCurvature")
        ax.xaxis.set_major_locator(ticker.MultipleLocator(20))
        ax.xaxis.set_major_formatter(ticker.ScalarFormatter())
        ax.yaxis.set_major_locator(ticker.MultipleLocator(5))
        ax.yaxis.set_major_formatter(ticker.ScalarFormatter())
        plt.show()

        heatDf = pd.crosstab(self.incidentRoadDF['maxCurvature-level'], self.incidentRoadDF['cornerDeviation-level']).div(len(self.incidentRoadDF))
        ax = sns.heatmap(heatDf, annot=annot)
        ax.set_title("Heatmap cornerDeviation & maxCurvature")
        ax.set_xlabel("cornerDeviation")
        ax.set_ylabel("maxCurvature")
        ax.xaxis.set_major_locator(ticker.MultipleLocator(20))
        ax.xaxis.set_major_formatter(ticker.ScalarFormatter())
        ax.yaxis.set_major_locator(ticker.MultipleLocator(5))
        ax.yaxis.set_major_formatter(ticker.ScalarFormatter())
        plt.show()

        heatDf = pd.crosstab(self.incidentRoadDF['cornerDeviation-level'], self.incidentRoadDF['fov-level']).div(len(self.incidentRoadDF))
        ax = sns.heatmap(heatDf, annot=annot)
        ax.set_title("Heatmap FOV & cornerDeviation")
        ax.set_xlabel("FOV")
        ax.set_ylabel("cornerDeviation")
        ax.xaxis.set_major_locator(ticker.MultipleLocator(20))
        ax.xaxis.set_major_formatter(ticker.ScalarFormatter())
        ax.yaxis.set_major_locator(ticker.MultipleLocator(10))
        ax.yaxis.set_major_formatter(ticker.ScalarFormatter())
        plt.show()


    
    def plotIncidentComplexityVs(self):
        self.incidentRoadDFNormalized.plot(y=["complexity", "fov", "cornerDeviation", "maxCurvature"])
        plt.show()


    
    def plotConnectionPropertyHistGroupedByLegs(self, property, bins=10, norm=False):
        
        Histogram.plot2MetricsDF(self.connectionRoadDF, property, 'legs', bins=bins, title="Connection road distribution")
        # Histogram.plot2StackedMetricsDF(self.connectionRoadDF, property, 'legs', bins=bins, title="Connection road distribution")
        Histogram.plot2MetricsDFSep(self.connectionRoadDF, property, 'legs', bins=bins)



    
    def plotIncidentPropertyHistGroupedByLegs(self, property, bins=10, norm=False):
        
        Histogram.plot2MetricsDF(self.incidentRoadDF, property, 'legs', bins=bins, title="Incident road distribution")
        Histogram.plot2StackedMetricsDF(self.incidentRoadDF, property, 'legs', bins=bins, title="Incident road distribution")
        Histogram.plot2MetricsDFSep(self.incidentRoadDF, property, 'legs', bins=bins)

    

    def plotIntersectionPropertyHistGroupedByLegs(self, property, bins=10, norm=False, xlabel=""):
        
        # Histogram.plot2MetricsDF(self.intersectionDF, property, 'legs', bins=bins, title="Intersection distribution", xlabel=xlabel)
        # Histogram.plot2StackedMetricsDF(self.intersectionDF, property, 'legs', bins=bins, title="Intersection distribution", xlabel=xlabel)
        Histogram.plot2MetricsDFSep(self.intersectionDF, property, 'legs', bins=bins, xlabel=xlabel)


    def plotIntersectionPropertyHist(self, property, bins=10, norm=False, xlabel=""):
        Histogram.plotMetricsDF(self.intersectionDF, property, xlabel="Incident road distribution", bins=bins)

        
    
