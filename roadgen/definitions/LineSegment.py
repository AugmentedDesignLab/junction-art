from z3 import *
import math
from roadgen.library.ValueConverter import ValueConverter


class LineSegment:

    def __init__(self, id, distance, x1, y1, x2, y2):
        self.id = id
        self.distance = distance
        self.x1 = x1
        self.y1 = y1
        self.x2 = x2
        self.y2 = y2

        self._constraints = [simplify(((self.x1 - self.x2) ** 2 + (self.y1 - self.y2) ** 2) == (self.distance ** 2))]


        

    def constraint(self):
        return self._constraints
        # csCombined = And()
        # for cs in self._constraints:
        #     csCombined = And(csCombined, cs)
        
        # return simplify(cs)
    
    @staticmethod
    def createFromPoints(id, p1, p2, fixedP1=False, fixedP2=False):

        x1 = p1.x
        y1 = p1.y
        x2 = p2.x
        y2 = p2.y
        
        distance = math.sqrt((p1.originalPosition[0] - p2.originalPosition[0]) **2 + (p1.originalPosition[1] - p2.originalPosition[1]) ** 2)
        return LineSegment(id, distance, x1, y1, x2, y2)

    
    def extractSolvedPoints(self, model):
        return [
                ( ValueConverter.z3AnyToFloat(model[self.x1]), ValueConverter.z3AnyToFloat(model[self.y1]) ), 
                ( ValueConverter.z3AnyToFloat(model[self.x2]), ValueConverter.z3AnyToFloat(model[self.y2]) )
            ]