import matplotlib.pyplot as plt
import seaborn as sns
# Apply the default theme
sns.set_theme()


class ScatterPlot:

    
    @staticmethod
    def plot2MetricsDF(data, col1, col2):
        g = sns.scatterplot(data=data, x=col1, y=col2)
        # g.set_axis_labels(name, "Number of Intersections")
        # g.set_titles(f"Distribution of {name}")
        plt.show()