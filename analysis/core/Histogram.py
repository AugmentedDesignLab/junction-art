import matplotlib.pyplot as plt
import seaborn as sns
# Apply the default theme
sns.set_theme()


class Histogram:


    @staticmethod
    def plotNormalizedMetrics(data, name, bins=10):
        g = sns.displot(data=data, kde=True, stat="probability", bins=bins)
        g.set_axis_labels(name, "Number of Intersections")
        g.set_titles(f"Distribution of {name}")
        plt.show()
    
    @staticmethod
    def plotNormalizedMetricsDF(data, col, name, bins=10):
        g = sns.displot(data=data, x=col, kde=True, stat="probability", bins=bins)
        g.set_axis_labels(name, "Number of Intersections")
        g.set_titles(f"Distribution of {name}")
        plt.show()

    
    @staticmethod
    def plot2MetricsDF(data, col1, col2, bins=10, title=""):
        g = sns.displot(data=data, x=col1, hue=col2, kde=True, stat="probability", bins=bins)
        # g.set_axis_labels(name, "Number of Intersections")
        g.set_titles(f"{title}")
        plt.show()

    @staticmethod
    def plot2StackedMetricsDF(data, col1, col2, bins=10, title=""):
        g = sns.displot(data=data, x=col1, hue=col2, multiple="stack", stat="probability", bins=bins)
        # g.set_axis_labels(name, "Number of Intersections")
        g.set_titles(f"{title}")
        plt.show()

    @staticmethod
    def plot2MetricsDFSep(data, col1, col2, bins=10, title=""):
        g = sns.displot(data=data, x=col1, col=col2, kde=True, stat="probability", bins=bins)
        # g.set_axis_labels(name, "Number of Intersections")
        g.set_titles(f"{title}")
        plt.show()
