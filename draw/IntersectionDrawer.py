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


class Color(Enum):
    CENTER_LANE = 'r'
    LEFT_LANE = 'g'
    RIGHT_LANE = 'g'


class IntersectionDrawer():
    def __init__(self, intersection, step = 0.1) -> None:
        self.intersection = intersection
        self.intersection_polygon = IntersectionPolygon(intersection)
        pass 


# TODO direction of left lane and right depends on lane width
#       currently just concerned about the area
# TODO straight line drawing angle may be not correct

    def draw_intersection(self, color = 'r', include_u_turn=True):
        
        road_polygon = self.intersection_polygon.get_road_polygons(include_u_turns=include_u_turn)
        
        for key in road_polygon:
            polygon = road_polygon[key]
            x, y = polygon.exterior.xy
            plt.plot(x, y, color)
        return plt

    def draw_intersection_area(self, color='c', include_u_turn=True):

        polygon = self.intersection_polygon.get_intersection_area_polygon(include_u_turn)
        x, y = polygon.exterior.xy
        plt.fill(x, y, color)
        return plt


    def draw_road_overlap_area(self, color = 'g', include_u_turn = True):
        road_overlap_polygons = self.intersection_polygon.get_road_overlap_polygons(include_u_turn)
        
        for polygon in road_overlap_polygons:
            if polygon.type == 'Polygon' and polygon.exterior.length > 0:
                x, y = polygon.exterior.xy
                plt.fill(x, y, color)
        
        # plt.show()
        return plt


    def draw_polygon_image_arr(self, include_u_turn=True):

        fig, (full_intersection, intersection_area, road_overlap) = plt.subplots(1, 3)
        fig.suptitle('image array ')
        fig.set_figwidth(12)
        fig.set_figheight(3)

        road_polygon = self.intersection_polygon.get_road_polygons(include_u_turn)
        intersection_area_polygon = self.intersection_polygon.get_intersection_area_polygon(include_u_turn)
        road_overlap_area_polygons = self.intersection_polygon.get_road_overlap_polygons(include_u_turn)

        for key in road_polygon:
            polygon = road_polygon[key]
            x, y = polygon.exterior.xy
            full_intersection.plot(x, y, color = 'r')

        x, y = intersection_area_polygon.exterior.xy
        intersection_area.plot(x, y, color = 'c')

        for polygon in road_overlap_area_polygons:
            if polygon.type == 'Polygon' and polygon.exterior.length > 0:
                x, y = polygon.exterior.xy
                road_overlap.plot(x, y, color = 'b')

        plt.show()

        pass

   