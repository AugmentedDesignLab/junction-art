import unittest
import numpy as np
from roadgen.layout.Grid import Grid
from roadgen.layout.MapBuilder import MapBuilder
from roadgen.definitions.LogicalIntersection import LogicalIntersection
from roadgen.definitions.LogicalQuadrant import LogicalQuadrant

class test_MapBuilder(unittest.TestCase):

    def setUp(self):
        
        grid = Grid(size=(1000, 1000), cellSize=(100, 100))
        intersections = self.createIntersections()
        self.mapBuilder = MapBuilder(grid, intersections)


    def createIntersections(self):
        intersections = []

        intersections.append(self.createRandomIntersection())

        return intersections
    

    def createRandomIntersection(self):

        # random top
        top = LogicalQuadrant(np.random.choice([0, 1, 2]), np.random.choice([0, 1, 2]))
        left = LogicalQuadrant(np.random.choice([0, 1, 2]), np.random.choice([0, 1, 2]))
        bot = LogicalQuadrant(np.random.choice([0, 1, 2]), np.random.choice([0, 1, 2]))
        right = LogicalQuadrant(np.random.choice([0, 1, 2]), np.random.choice([0, 1, 2]))
        # random bot...
        return LogicalIntersection(top=top, left=left, bot=bot, right=right)
        

    def test_Builder(self):

        self.mapBuilder.run(1)