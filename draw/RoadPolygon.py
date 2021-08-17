# main object dict road id, polygon
# incoming is a road 
# returns  
# road geometry is an abstract class 
# build polygon 
# center lane line
# left lane 
# right lane 

from abc import ABC, abstractmethod

# import numpy as np
# from junctions.StandardCurveTypes import StandardCurveTypes
# from draw.IntersectionDrawer import Color
# import math
# from shapely.geometry.polygon import Polygon
# from shapely.ops import unary_union

# # from shapely.geometry import Point
# from sympy.geometry import Line2D, Point

class RoadPolygon(ABC):
    def __init__(self, road) -> None:
        self.road = road
        self.road_id = road.id
        self.leftlanes = road.lanes.lanesections[0].leftlanes
        self.rightlanes = road.lanes.lanesections[0].rightlanes
        self.polygon = []

        self.center_line_points = []
        self.left_line_points = []
        self.right_line_points = []
        
        self.lanewidth = 3
        # self.center_line = []
        super().__init__()
    


    @abstractmethod
    def build_polygon(self):
        pass

    @abstractmethod
    def fill_line_points(self):
        pass



    

