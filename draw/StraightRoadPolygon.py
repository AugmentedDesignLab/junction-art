
from draw.RoadPolygon import RoadPolygon

import numpy as np
from junctions.StandardCurveTypes import StandardCurveTypes
import math
from shapely.geometry.polygon import Polygon
from shapely.ops import unary_union

# from shapely.geometry import Point
from sympy.geometry import Line2D, Point


class StraightRoadPolygon(RoadPolygon):
    def __init__(self, road) -> None:
        super().__init__(road)

    def build_polygon(self):
        # print('build polygon straight road ')
        self.fill_line_points()
        
        lane_polygons = []
        # right_lane_polygons = []

        for i in range(len(self.leftlanes)):
            polygon = self.create_lane_polygon_straight_road(self.center_line_points[0],
                                                             self.center_line_points[1],
                                                             self.left_line_points[2*i],
                                                             self.left_line_points[2*i+1])
            lane_polygons.append(polygon)
            

        for i in range(len(self.rightlanes)):
            polygon = self.create_lane_polygon_straight_road(self.center_line_points[0],
                                                             self.center_line_points[1],
                                                             self.right_line_points[2*i],
                                                             self.right_line_points[2*i+1])
            lane_polygons.append(polygon)

        # combined_polygon = None
        self.polygon = unary_union(lane_polygons)

        # for i in range(len(lane_polygons)):
        #     print(' lane polygons ', lane_polygons[i].geom_type)

        return self.polygon

    def fill_line_points(self):

        start_coordinate = self.road.getAdjustedStartPosition()
        end_coordinate = self.road.getAdjustedEndPosition()
        # print('start_position ', start_coordinate, ' end_position ', end_coordinate)

        start_point = Point(start_coordinate[0], start_coordinate[1])
        end_point = Point(end_coordinate[0], end_coordinate[1])

        self.center_line_points.append(start_point)
        self.center_line_points.append(end_point)
        # print('filled center points ')

        for leftlane in range(len(self.leftlanes)):
            leftlane_start, leftlane_end = self.get_lane_start_and_end(start_point, end_point, leftlane + 1)
            self.left_line_points.append(leftlane_start)
            self.left_line_points.append(leftlane_end)
            # print('filled left line points ')

        for rightlane in range(len(self.rightlanes)):
            rightlane_start, rightlane_end = self.get_lane_start_and_end(start_point, end_point, - rightlane - 1)
            self.right_line_points.append(rightlane_start)
            self.right_line_points.append(rightlane_end)
            # print('filled right line points ')

        pass

    def create_lane_polygon_straight_road(self, centerlane_start, centerlane_end, lane_start, lane_end):
        polygon = Polygon([centerlane_start, centerlane_end, lane_end, lane_start])
        # print(centerlane_start, centerlane_end, lane_start, lane_end)
        return polygon

    def get_lane_start_and_end(self, center_line_start, center_line_end, lane_id):
        center_line = Line2D(center_line_start, center_line_end) 
        total_lane_width = self.lanewidth*lane_id
        parallel_line = self.calculate_parallel_line_at_distance(center_line, total_lane_width)

        perpendicular_at_start = center_line.perpendicular_line(center_line.p1)
        perpendicular_at_end = center_line.perpendicular_line(center_line.p2)

        parallel_point_at_start = perpendicular_at_start.intersection(parallel_line)[0]
        parallel_point_at_end = perpendicular_at_end.intersection(parallel_line)[0]

        return parallel_point_at_start, parallel_point_at_end


    def calculate_parallel_line_at_distance(self, line, distance):
        a, b, c = line.coefficients # ax + by + c = 0
        m, c = -(a/b), -(c/b) # y = mx + c
        abs_diff = distance*math.sqrt(m**2 + 1)
        new_c = c - abs_diff
        if m == 0:
            new_line = Line2D(Point(0, new_c), Point(10, new_c))
        else:
            new_line = Line2D(Point(-new_c/m, 0), Point(0, new_c)) # x/a + y/b = 1
        return new_line

