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

        self.normalize()
        pass

    
    def normalize(self):
        self.incidentRoadDFNormalized = self.normalizeWhole(self.incidentRoadDF)
        self.connectionRoadDFNormalized = self.normalizeWhole(self.connectionRoadDF)
        self.intersectionDFNormalized = self.normalizeWhole(self.intersectionDF)

    
    def normalizeWhole(self, df):
        return (df-df.min())/(df.max()-df.min())

    def plotIncidentHist(self, cols=["fov", "cornerDeviation", 'maxCurvature'], subplots=False):

        ax = self.incidentRoadDFNormalized.plot.hist(bins=10, alpha=0.5, xlabel="Normalized Scale 0.0 - 1.0)", y=cols, subplots=subplots)
        plt.show()
        ax = self.incidentRoadDF.plot.hist(bins=10, alpha=0.5, y=cols, subplots=subplots)
        plt.show()
        return 

    def plotIncidentDistributions(self, cols=["fovNorm", "cornerDeviationNorm", 'maxCurvatureNorm'], subplots=False):

        # ax = self.incidentRoadDF.plot.density(y=cols, subplots=subplots)
        # ax = self.incidentRoadDF.fovNorm.plot.kde()
        # plt.show()
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

        complexityMaxBins = np.linspace(0, self.incidentRoadDF['complexity_max'].max(), bins)
        self.incidentRoadDF['complexity_max-level'] = pd.cut(self.incidentRoadDF['complexity_max'], bins=complexityMaxBins, labels=False)

        curveBins = np.linspace(0, self.incidentRoadDF['maxCurvature'].max(), bins)
        self.incidentRoadDF['maxCurvature-level'] = pd.cut(self.incidentRoadDF['maxCurvature'], bins=curveBins, labels=False)

        # fovLevels = np.linspace(0, self.incidentRoadDF['fov'].max(), )
        fobBins = np.linspace(0, self.incidentRoadDF['fov'].max(), bins)
        self.incidentRoadDF['fov-level'] = pd.cut(self.incidentRoadDF['fov'], bins=fobBins, labels=False)
        
        cvBins = np.linspace(0, self.incidentRoadDF['cornerDeviation'].max(), bins)
        self.incidentRoadDF['cornerDeviation-level'] = pd.cut(self.incidentRoadDF['cornerDeviation'], bins=cvBins, labels=False)
    
    def plotIncidentHeatMaps(self):

        bins=25
        self.discretizeIncidentDf(bins)
        ticks = np.arange(0, bins, 1.0)
        annot=False

        heatDf = pd.crosstab(self.incidentRoadDF['complexity_max-level'], self.incidentRoadDF['maxCurvature-level']).div(len(self.incidentRoadDF))
        ax = sns.heatmap(heatDf, annot=annot)
        ax.set_title("Heatmap Curvature & Complexity")
        ax.set_xlabel("Curvature")
        ax.set_ylabel("Complexity")
        ax.xaxis.set_major_locator(ticker.MultipleLocator(5))
        ax.xaxis.set_major_formatter(ticker.ScalarFormatter())
        plt.show()

        # heatDf = pd.crosstab(self.incidentRoadDF['complexity_max-level'], self.incidentRoadDF['fov-level']).div(len(self.incidentRoadDF))
        # ax = sns.heatmap(heatDf, annot=annot)
        # ax.set_title("Heatmap FOV & Complexity")
        # ax.set_xlabel("FOV")
        # ax.set_ylabel("Complexity")
        # plt.show()

        # heatDf = pd.crosstab(self.incidentRoadDF['complexity_max-level'], self.incidentRoadDF['cornerDeviation-level']).div(len(self.incidentRoadDF))
        # ax = sns.heatmap(heatDf, annot=annot)
        # ax.set_title("Heatmap Deviation-Sight line & Complexity")
        # ax.set_xlabel("Deviation form Sight-line")
        # ax.set_ylabel("Complexity")
        # plt.show()

        
        # # g = sns.displot(data=self.incidentRoadDF, x="fov", y="maxCurvature", bins=bins)
        # # # g.set_axis_labels(name, "Number of Intersections")
        # # g.set_titles(f"Fov vs Curvature")
        # # g.set(xlim=(0, 180), ylim=(0, 36))
        # # plt.show()

        # heatDf = pd.crosstab(self.incidentRoadDF['maxCurvature-level'], self.incidentRoadDF['fov-level']).div(len(self.incidentRoadDF))
        # ax = sns.heatmap(heatDf, annot=annot)
        # ax.set_title("Heatmap FOV & Curvature")
        # # ax.set_xlabel("FOV")
        # # ax.set_ylabel("Curvature")
        # plt.show()


    
    def plotIncidentComplexityVs(self):
        self.incidentRoadDFNormalized.plot(y=["complexity", "fov", "cornerDeviation", "maxCurvature"])
        plt.show()

        
    
