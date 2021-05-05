from z3 import *

from roadgen.definitions.LogicalIntersection import LogicalIntersection



class QuadrantSolver:


    """ solves without rotating intersections """


    def __init__(self):
        pass


    def solve(self, grid, cell, candidates):


        # get existing quadrant on top

        neighborTop = self.getNeighbourQuadrantOnTop(grid, cell)
        neighborLeft = self.getNeighbourQuadrantOnLeft(grid, cell)
        neighborBot = self.getNeighbourQuadrantOnBot(grid, cell)
        neighborRight = self.getNeighbourQuadrantOnRight(grid, cell)

        reducedCandidates = set([])
        for candidate in candidates:
            if self.isCompatibleWithNeighbours(neighborTop, neighborLeft, neighborBot, neighborRight, candidate):
                reducedCandidates.add(candidate)

        return reducedCandidates



    def isCompatibleWithNeighbours(self, neighborTop, neighborLeft, neighborBot, neighborRight, candidate):

        return (

            self.isCompatible(neighborTop, candidate.top)
            and self.isCompatible(neighborLeft, candidate.left)
            and self.isCompatible(neighborBot, candidate.bot)
            and self.isCompatible(neighborRight, candidate.right)
        )



    def isCompatible(self, quad1, quad2):

        """ And(Implies(nIncoming == 0, nOutgoing == 0), Implies(nOutgoing == 0, nIncoming == 0)) """

        if quad1.nIncoming == 0 and quad2.nOutgoing != 0:
            return False

        if quad1.nOutgoing == 0 and quad2.nIncoming != 0:
            return False

        return True


    # def getQuadrantConstraints(self, quad1, quad2):

        """ quad1 and quad2 are in two different intersections """

        # return And(Implies(nIncoming == 0, nOutgoing == 0), Implies(nOutgoing == 0, nIncoming == 0))



    def getNeighbourQuadrantOnTop(self, grid, cell):
        neighbor = grid.topElement(cell)
        if (neighbor is None) or (not isinstance(neighbor, LogicalIntersection)):
            return None
        return neighbor.bot

    def getNeighbourQuadrantOnLeft(self, grid, cell):
        neighbor = grid.leftElement(cell)
        if (neighbor is None) or (not isinstance(neighbor, LogicalIntersection)):
            return None
        return neighbor.right

    def getNeighbourQuadrantOnBot(self, grid, cell):
        neighbor = grid.botElement(cell)
        if (neighbor is None) or (not isinstance(neighbor, LogicalIntersection)):
            return None
        return neighbor.top

    def getNeighbourQuadrantOnRight(self, grid, cell):
        neighbor = grid.rightElement(cell)
        if (neighbor is None) or (not isinstance(neighbor, LogicalIntersection)):
            return None
        return neighbor.left

  