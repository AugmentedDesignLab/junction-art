from z3 import *

from junctionart.roadgen.definitions.DirectionIntersection import DirectionIntersection
import logging


class QuadrantSolver:


    """ solves without rotating intersections """


    def __init__(self, debug=True):
        self.debug = debug
        self.name = "QuadrantSolver"
        pass


    def solve(self, grid, cell, candidates):


        # get existing quadrant on top

        neighborTop = self.getNeighbourQuadrantOnTop(grid, cell)
        neighborLeft = self.getNeighbourQuadrantOnLeft(grid, cell)
        neighborBot = self.getNeighbourQuadrantOnBot(grid, cell)
        neighborRight = self.getNeighbourQuadrantOnRight(grid, cell)

        reducedCandidates = []
        scores = []
        # for candidate in candidates:
        #     if self.isCompatibleWithNeighbours(neighborTop, neighborLeft, neighborBot, neighborRight, candidate):
        #         reducedCandidates.append(candidate)
        for candidate in candidates:
            score = self.getCompatibilityScore(neighborTop, neighborLeft, neighborBot, neighborRight, None, None, None, None, candidate)
            if score > 0:
                reducedCandidates.append(candidate)
                scores.append(score)

        return reducedCandidates, scores



    def isCompatibleWithNeighbours(self, neighborTop, neighborLeft, neighborBot, neighborRight, candidate):

        # if self.debug:
        #     logging.info(f"{self.name}: neighborTop: {neighborTop}, neighborLeft: {neighborLeft}, neighborBot: {neighborBot}, neighborRight: {neighborRight}, candidate: {candidate}")

        return (

            self.isCompatible(neighborTop, candidate.top)
            and self.isCompatible(neighborLeft, candidate.left)
            and self.isCompatible(neighborBot, candidate.bot)
            and self.isCompatible(neighborRight, candidate.right)
        )

    def getCompatibilityScore(self, neighborTop, neighborLeft, neighborBot, neighborRight, neighborLeftTop, neighborLeftBot, neighborRightTop, neighborRightBot, candidate):
        

        score = 0

        score = (score + 1) if self.isCompatible(neighborTop, candidate.top) else (score - 0.5)
        score = (score + 1) if self.isCompatible(neighborLeft, candidate.left) else (score - 0.5)
        score = (score + 1) if self.isCompatible(neighborBot, candidate.bot) else (score - 0.5)
        score = (score + 1) if self.isCompatible(neighborRight, candidate.right) else (score - 0.5)


        return score


    def isCompatible(self, quad1, quad2):

        """ And(Implies(nIncoming == 0, nOutgoing == 0), Implies(nOutgoing == 0, nIncoming == 0)) """

        if quad1 is None or quad2 is None: # means we hit a boundary or a blank space. An obstacle will have 0 incoming and outgoing.
            return True

        if quad1.nIncoming == 0 and quad2.nOutgoing != 0:
            return False

        if quad1.nOutgoing == 0 and quad2.nIncoming != 0:
            return False

        if quad2.nIncoming == 0 and quad1.nOutgoing != 0:
            return False

        if quad2.nOutgoing == 0 and quad1.nIncoming != 0:
            return False

        return True


    # def getQuadrantConstraints(self, quad1, quad2):

        """ quad1 and quad2 are in two different intersections """

        # return And(Implies(nIncoming == 0, nOutgoing == 0), Implies(nOutgoing == 0, nIncoming == 0))



    def getNeighbourQuadrantOnTop(self, grid, cell):
        neighbor = grid.topElement(cell)
        if (neighbor is None) or (not isinstance(neighbor, DirectionIntersection)):
            return None
        return neighbor.bot

    def getNeighbourQuadrantOnLeft(self, grid, cell):
        neighbor = grid.leftElement(cell)
        if (neighbor is None) or (not isinstance(neighbor, DirectionIntersection)):
            return None
        return neighbor.right

    def getNeighbourQuadrantOnBot(self, grid, cell):
        neighbor = grid.botElement(cell)
        if (neighbor is None) or (not isinstance(neighbor, DirectionIntersection)):
            return None
        return neighbor.top

    def getNeighbourQuadrantOnRight(self, grid, cell):
        neighbor = grid.rightElement(cell)
        if (neighbor is None) or (not isinstance(neighbor, DirectionIntersection)):
            return None
        return neighbor.left

  