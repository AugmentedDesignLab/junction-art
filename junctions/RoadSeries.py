class RoadSeries:
    """A series of roads connected along the reference line. Some uqitilty functions
    """

    def __init__(self, roads):
        self.roads = roads

    

    def getFirst(self):
        return self.roads[0]

    
    def getLast(self):

        return self.roads[-1]
    
    def getAll(self):
        return self.roads

    def length(self):
        return len(self.roads)