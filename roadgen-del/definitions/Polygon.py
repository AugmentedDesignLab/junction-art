from z3 import *
from roadgen.definitions.LineSegment import LineSegment
from roadgen.definitions.Point import Point

class Polygon:

    def __init__(self, id, points, fixedPoints=None):

        """
        
        Args:
            points (list of tuples): vertices in clockwise manner
            fixedPoints: vertices with absolute positions
        """
        self.id = id
        self.lsCounter = 0
        self.lsCounter = 0
        self.originalPoints = points
        self.points = []
        self._createPointVars()
        self.fixedPoints = fixedPoints
        self.allLineSegments = {}
        self.outerLineSegments = self._createOutLineSegments()
        self.innerLineSegments = self._createInnerLineSegments()
        self.solvedPoints = []


    def createLsId(self):
        self.lsCounter += 1
        return f'pol{self.id}_lin{self.lsCounter}'
    
    def getPointId(self, index):
        return f'pol{self.id}_point{index}'

    def _createPointVars(self):
        index = 0
        for originalCoord in self.originalPoints:
            self.points.append(Point(self.getPointId(index), originalCoord))
            # self.points.append(Point(self.getPointId(index), point[0], point[1]))
            index += 1

    def _createOutLineSegments(self):
        
        lss = []

        for i in range(len(self.points) - 1):
            p1 = self.points[i]
            p2 = self.points[i + 1]
            ls = LineSegment.createFromPoints(self.createLsId(), p1, p2)
            lss.append(ls)
            self.allLineSegments[ls.id] = ls
        
        # last segment
        if len(self.points) > 2:
            p1 = self.points[-1]
            p2 = self.points[0]
            ls = LineSegment.createFromPoints(self.createLsId(), p1, p2)
            lss.append(ls)
            self.allLineSegments[ls.id] = ls

        return lss

    def _createInnerLineSegments(self):
        lss = []
        length = len(self.points)
        for i in range(length - 2):
            for j in range(i+2, length):
                if i == 0 and j == length-1:
                    break
                p1 = self.points[i]
                p2 = self.points[j]
                ls = LineSegment.createFromPoints(self.createLsId(), p1, p2)
                lss.append(ls)
                self.allLineSegments[ls.id] = ls
        return lss

    
    def constraint(self):
        constraints = []
        
        for p in self.points:
            constraints += p.constraint()
        for ls in self.outerLineSegments:
            constraints += ls.constraint()
        return constraints
        # csCombined = And()
        # for ls in self.outerLineSegments:
        #     csCombined = And(csCombined, ls.constraint())
        # return simplify(csCombined)

    
    def extractSolvedPoints(self, model):
        self.solvedPoints = []
        for ls in self.outerLineSegments:
            
            [p1, p2] = ls.extractSolvedPoints(model)
            self.solvedPoints.append(p1)
            


                