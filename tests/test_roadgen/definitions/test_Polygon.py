# import unittest
# from z3 import *
# from junctionart.roadgen.definitions.Polygon import Polygon
# import pprint
# import matplotlib.pyplot as plt
# import copy

# class test_Polygon(unittest.TestCase):

#     def setUp(self):

#         self.pp = pprint.PrettyPrinter()

#     def test_innerPairs(self):
        
#         length = 6
#         print(f"for length = {length}")
#         for i in range(length - 2):
#             for j in range(i+2, length):
#                 if i == 0 and j == length-1:
#                     break
#                 print(i, j)
#         length = 3
#         print(f"for length = {length}")
#         for i in range(length - 2):
#             for j in range(i+2, length):
#                 if i == 0 and j == length-1:
#                     break
#                 print(i, j)
#         length = 4
#         print(f"for length = {length}")
#         for i in range(length - 2):
#             for j in range(i+2, length):
#                 if i == 0 and j == length-1:
#                     break
#                 print(i, j)


#     def test_def(self):

#         points = [
#             (0, 0),
#             (3, 4),
#             (3, 14)
#         ]
#         poly = Polygon('1', points)

#         for ls in poly.outerLineSegments:
#             print(ls.constraint())

    
#     def test_solve(self):
#         points = [
#             (0, 0),
#             (3, 4),
#             (3, 14)
#         ]
#         coord = copy.deepcopy(points)
#         coord.append(coord[0]) #repeat the first point to create a 'closed loop'
#         xs, ys = zip(*coord) #create lists of x and y values
        

#         poly = Polygon('1', points)
#         self.pp.pprint(poly.constraint())



#         s = Solver()
#         s.add(poly.constraint())

#         for i in range(3):
#             if s.check() == sat:
#                 self.pp.pprint(s.model())

#             poly.extractSolvedPoints(s.model())
#             print(poly.solvedPoints)
        
#             coord2 = copy.deepcopy(poly.solvedPoints)
#             coord2.append(coord2[0]) #repeat the first point to create a 'closed loop'
#             xs2, ys2 = zip(*coord2) #create lists of x and y values
            
#             fig, ax = plt.subplots(nrows=1, ncols=2)
            
#             ax[0].set_xlim([0, 50])   
#             ax[0].set_ylim([0, 50])   
#             ax[1].set_xlim([0, 50])   
#             ax[1].set_ylim([0, 50])   


#             ax[0].plot(xs,ys) 
#             ax[1].plot(xs2,ys2) 
#             plt.show()

#             # s.add(poly.points[0].x >= s.model()[poly.points[0].x])
        
            