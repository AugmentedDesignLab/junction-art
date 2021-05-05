# from z3 import * 

# from roadgen.definitions.Polygon import Polygon

# class Map:

#     def __init__(self):
#         self._polygons = []
#         self._polyCounter = 0
    

#     def createPolyId(self):
#         self._polyCounter += 1
#         return f'pol{self._polyCounter}'

    
#     def createPolygon(self, points, id=None):

#         if id is None:
#             id = self.createPolyId()
        
#         poly = Polygon(id, points)
#         self._polygons.append(poly)
    
#     def constraint(self):

#         # constraints = self.createOverlapConstraints()
#         # constraints += self.createPolygonConstraints()
#         pass


#     def constraintForAdjacentPolygons(self, poly1, poly2):

#         pass