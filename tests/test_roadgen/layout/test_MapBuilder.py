import unittest
import numpy as np
from junctionart.roadgen.layout.Grid import Grid
from junctionart.roadgen.layout.MapBuilder import MapBuilder
from junctionart.roadgen.definitions.DirectionIntersection import DirectionIntersection
from junctionart.roadgen.definitions.DirectionQuadrant import DirectionQuadrant


class test_MapBuilder(unittest.TestCase):

    def setUp(self):
        
        grid = Grid(size=(500, 500), cellSize=(100, 100))
        intersections = self.createIntersections(0)
        self.mapBuilder = MapBuilder(grid, intersections, random_seed=40)
        pass



    def createIntersections(self, n=4):

        np.random.seed(40)
        intersections = []

        for _ in range(n):

            intersections.append(self.createRandomIntersection())
        
        return intersections
    
    def createRandomIntersection(self):

        top = DirectionQuadrant(np.random.choice([0, 0, 1, 2]), np.random.choice([0, 0, 1, 2]))
        left = DirectionQuadrant(np.random.choice([0, 0, 1, 2]), np.random.choice([0, 0, 1, 2]))
        bot = DirectionQuadrant(np.random.choice([0, 0, 1, 2]), np.random.choice([0, 0, 1, 2]))
        right = DirectionQuadrant(np.random.choice([0, 0, 1, 2]), np.random.choice([0, 0, 1, 2]))

        return DirectionIntersection(top=top, left=left, bot=bot, right=right)



    def test_Builder(self):


        nextCells = self.mapBuilder.grid.getEmptyCellsWithLowestEntropy()

        assert len(nextCells) == self.mapBuilder.grid.nCells()

        self.mapBuilder.run(100)

    