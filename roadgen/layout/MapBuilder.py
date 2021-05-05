from roadgen.layout.Grid import Grid
from copy import copy
import numpy as np

from roadgen.layout.QuadrantSolver import QuadrantSolver
from roadgen.definitions.EmptySpace import EmptySpace


class MapBuilder:

    def __init__(self, grid, intersections, seed=39):
        self.grid = grid
        # self.polygons = polygons
        self.intersections = intersections
        self.candidates = set(intersections)
        np.random.seed(seed)
        self.qSolver = QuadrantSolver()

    def run(self, maxTries=100):
        # do

        for i in range(maxTries):
            if len(self.candidates) == 0:
                break

            nextCells = self.grid.getEmptyCellsWithLowestEntropy()
            cell = np.random.choice(nextCells)

            # 2 get possible candidates for this cell
            validCandidates = self.qSolver.solve(self.grid, cell, self.candidates)
            

            # 3. choose one candidate for this cell, set an empty space if no candidate
            if len(validCandidates) == 0:
                self.grid.setElement(cell, EmptySpace())
            else:
                chosenIntersection = np.random.choice(validCandidates)
                self.grid.setElement(cell, chosenIntersection)
                # 5. remove candidate from candidates set
                self.candidates.remove(chosenIntersection)




