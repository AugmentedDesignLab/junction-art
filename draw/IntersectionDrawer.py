from enum import Enum

import numpy as np
from sympy.core.parameters import evaluate
from sympy.geometry.point import Point2D 
from junctions.Intersection import Intersection
from extensions.ExtendedRoad import ExtendedRoad
from shapely.geometry import Polygon, polygon
from shapely.ops import unary_union
from sympy import Point, Line
import matplotlib.pyplot as plt
import math
from junctions.StandardCurveTypes import StandardCurveTypes

# import draw
from draw.StraightRoadPolygon import StraightRoadPolygon
from draw.ParamPolyRoadPolygon import ParamPolyRoadPolygon
from draw.IntersectionPolygon import IntersectionPolygon

# found error in this intersection from 10000
# [472, 798, 806, 819, 854, 854, 1275, 1500, 1501, 2028, 2036, 2095, 2096, 2907, 2917, 2944, 2945, 3430, 3431, 3436, 3446, 3456, 3789, 4208, 4221, 4356, 4708, 5334, 5335, 5724, 5725, 6141, 6292, 6880, 6886, 6971, 7203, 7213, 7228, 7242, 7624, 7633, 7732, 7733, 8338, 8339, 8473, 8474, 8842, 8843, 9098, 9099, 9178, 9187, 9403, 9552, 9560, 9606, 9724, 9856, 9974]



class Color(Enum):
    CENTER_LANE = 'r'
    LEFT_LANE = 'g'
    RIGHT_LANE = 'g'


class IntersectionDrawer():
    def __init__(self, intersection, step = 0.1) -> None:
        self.intersection = intersection
        self.intersection_polygon = IntersectionPolygon(intersection, step)
        pass 


# TODO direction of left lane and right depends on lane width
#       currently just concerned about the area
# TODO straight line drawing angle may be not correct

    def draw_intersection(self, plt,  color = 'r', include_u_turn=True):
        
        road_polygon = self.intersection_polygon.get_road_polygons(include_u_turns=include_u_turn)
        
        for key in road_polygon:
            polygon = road_polygon[key]
            x, y = polygon.exterior.xy
            plt.plot(x, y, color)
        pass 

    def draw_intersection_area(self, plt, color='c', include_u_turn=True):

        intersection_polygon = self.intersection_polygon.get_intersection_area_polygon(include_u_turn)
        for polygon in intersection_polygon:
            x, y = polygon.exterior.xy
            plt.plot(x, y, color)
        pass 


    def draw_road_overlap_area(self, plt, color = 'g', include_u_turn = True):
        road_overlap_polygons = self.intersection_polygon.get_road_overlap_polygons(include_u_turn)
        
        for polygon in road_overlap_polygons:
            if polygon.type == 'Polygon' and polygon.exterior.length > 0:
                x, y = polygon.exterior.xy
                plt.plot(x, y, color)
        
        # plt.show()
        pass 

    def draw_road_overlap_combined_polygon(self, plt, color= 'c', include_u_turn = True):

        combined_road_overlap_polygon = self.intersection_polygon.get_combined_road_overlap_polygon(include_u_turn)
        # print('perimeter ', combined_road_overlap_polygon.exterior.length)
        if combined_road_overlap_polygon.geom_type == 'MultiPolygon':
            for polygon in combined_road_overlap_polygon:
                x, y = polygon.exterior.xy
                plt.plot(x, y, color)
        else:
            x, y = combined_road_overlap_polygon.exterior.xy
            plt.plot(x, y, color)

        # plt.show()
        pass



    def draw_polygon_image_arr(self, include_u_turn=True):

        fig, (full_intersection, intersection_area, road_overlap, combined_overlap) = plt.subplots(1, 4)
        fig.suptitle('image array ')
        fig.set_figwidth(12)
        fig.set_figheight(3)

        self.draw_intersection(full_intersection, color='c', include_u_turn=include_u_turn)
        self.draw_intersection_area(intersection_area, color='g', include_u_turn=include_u_turn)
        self.draw_road_overlap_area(road_overlap, color='b', include_u_turn=include_u_turn)
        self.draw_road_overlap_combined_polygon(combined_overlap, color='r', include_u_turn=include_u_turn)

        plt.show()
        pass

    def get_intersection_area_value(self, include_u_turn = True):
        return self.intersection_polygon.get_intersection_area_value(include_u_turn)

    def get_road_overlap_area_value(self, include_u_turn = True):
        return self.intersection_polygon.get_combined_road_overlap_value(include_u_turn)

    def get_area_values(self, include_u_turn = True):
        
        intersection_area_value = self.get_intersection_area_value(include_u_turn)
        # print('intersection area value ', intersection_area_value)
        road_overlap_area_value = self.get_road_overlap_area_value(include_u_turn)
        # print('overlap area value ', road_overlap_area_value)
        
        return {'IntersectionArea': intersection_area_value,
                'ConflictArea': road_overlap_area_value}