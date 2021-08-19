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

    def draw_intersection(self, plt,  color = 'r', include_u_turn=True):
        
        road_polygon = self.intersection_polygon.get_road_polygons(include_u_turns=include_u_turn)
        
        for key in road_polygon:
            polygon = road_polygon[key]
            x, y = polygon.exterior.xy
            plt.plot(x, y, color)
        pass 

    def draw_intersection_area(self, plt, color='c', include_u_turn=True):

        polygon = self.intersection_polygon.get_intersection_area_polygon(include_u_turn)
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

        # road_polygon = self.intersection_polygon.get_road_polygons(include_u_turn)
        # intersection_area_polygon = self.intersection_polygon.get_intersection_area_polygon(include_u_turn)
        # road_overlap_area_polygons = self.intersection_polygon.get_road_overlap_polygons(include_u_turn)
        # combined_road_overlap_polygons = self.intersection_polygon.get_combined_road_overlap_polygon(include_u_turn)

        self.draw_intersection(full_intersection, color='c', include_u_turn=include_u_turn)
        self.draw_intersection_area(intersection_area, color='g', include_u_turn=include_u_turn)
        self.draw_road_overlap_area(road_overlap, color='b', include_u_turn=include_u_turn)
        self.draw_road_overlap_combined_polygon(combined_overlap, color='r', include_u_turn=include_u_turn)

        # for key in road_polygon:
        #     polygon = road_polygon[key]
        #     x, y = polygon.exterior.xy
        #     full_intersection.plot(x, y, color = 'r')

        # x, y = intersection_area_polygon.exterior.xy
        # intersection_area.plot(x, y, color = 'c')

        # for polygon in road_overlap_area_polygons:
        #     if polygon.type == 'Polygon' and polygon.exterior.length > 0:
        #         x, y = polygon.exterior.xy
        #         road_overlap.plot(x, y, color = 'b')

        # # for polygon in combined_road_overlap_polygons:
        # #     print('combined road overlap polygon ', polygon)

        # self.draw_road_overlap_combined_polygon(combined_overlap, color='g')
        plt.show()



        pass


    # def draw_any_p(self, geom):
    #     if geom.type == 'Polygon':
    #         exterior_polygon = Polygon([[p[0], p[1]] for p in geom.exterior.coords[:]])
    #         interior_polygon = []
    #         for interior in geom.interiors:
    #             polygon = Polygon([[p[0], p[1]] for p in interior.coords[:]])
    #             interior_polygon.append(polygon)
    #     elif geom.type == 'MultiPolygon':
    #         exterior_polygon = []
    #         interior_polygon = []

    #         for part in geom:
    #             epc = self.extract_poly_interior_and_exterior_polygon(part)  # Recursive call
    #             exterior_polygon += epc['exterior_polygon']
    #             interior_polygon += epc['interior_polygon']
    #     else:
    #         raise ValueError('Unhandled geometry type: ' + repr(geom.type))
    #     return {'exterior_polygon': exterior_polygon,
    #             'interior_polygon': interior_polygon}
   