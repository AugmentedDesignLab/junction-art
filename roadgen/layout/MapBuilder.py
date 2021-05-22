from roadgen.layout.Grid import Grid
from copy import copy
import numpy as np

from roadgen.layout.QuadrantSolver import QuadrantSolver
from roadgen.definitions.EmptySpace import EmptySpace
import logging



class MapBuilder:

    def __init__(self, grid, directionIntersections, random_seed=39, debug=True):
        self.grid = grid
        # self.polygons = polygons
        self.directionIntersections = directionIntersections
        self.candidates = set(directionIntersections)
        self.qSolver = QuadrantSolver()
        self.debug = debug
        self.name = "MapBuilder"

            
        np.random.seed(random_seed)
    

    def setDirectionIntersections(self, directionIntersections):
        self.directionIntersections = directionIntersections
        self.candidates = set(directionIntersections)
        pass


    def run(self, maxTries=100, plot=True):
        # do

        for i in range(maxTries):

            if self.debug:
                logging.info(f"{self.name}: Try #{i}")

            if len(self.candidates) == 0 or self.grid.nEmptyCells() == 0:
                if self.debug:
                    logging.info(f"{self.name}: exitting due to candidates: {len(self.candidates)}, empty cells: {self.grid.nEmptyCells()}")
                break

            nextCells = self.grid.getEmptyCellsWithLowestEntropy()
            cell = np.random.choice(nextCells)

            if self.debug:
                logging.info(f"{self.name}: chosen cell {cell.cell_position}")

            # 2 get possible candidates for this cell
            validCandidates = self.qSolver.solve(self.grid, cell, self.candidates)

            if self.debug:
                logging.info(f"{self.name}: number of valid candidates{len(validCandidates)}")
            

            # 3. choose one candidate for this cell, set an empty space if no candidate
            if len(validCandidates) == 0:
                self.grid.setCellElement(cell, EmptySpace())
            else:
                chosenIntersection = np.random.choice(validCandidates)
                if self.debug:
                    logging.info(f"{self.name}: chosen intersection {chosenIntersection}")

                self.grid.setCellElement(cell, chosenIntersection)
                # 5. remove candidate from candidates set
                self.candidates.remove(chosenIntersection)

        
        # self.grid.printCellElements()
        if plot:
            self.grid.plot()

    
    def getPositions(self):
        return None


