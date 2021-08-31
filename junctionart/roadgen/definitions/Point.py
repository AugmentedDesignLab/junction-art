from z3 import *
import math
from junctionart.roadgen.library.ValueConverter import ValueConverter


class Point:
    def __init__(self, id, originalPosition):
        
        self.id = id
        self.originalPosition = originalPosition
        self.x = Real(f'{self.id}_x')
        self.y = Real(f'{self.id}_y')
        self._constraints = []
        # if x is not None:
        #     self._constraints.append(self.x == x)
        # if y is not None:
        #     self._constraints.append(self.y == y)
        self.createPositiveConstraints()

    def createPositiveConstraints(self):
        self._constraints.append(self.x >= 0)
        self._constraints.append(self.y >= 0)

    def constraint(self):
        return self._constraints
        # csCombined = And()
        # for cs in self._constraints:
        #     csCombined = And(csCombined, cs)
        
        # return simplify(cs)