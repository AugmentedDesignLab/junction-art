from enum import Enum

import numpy as np
from sympy.core.parameters import evaluate
from sympy.geometry.point import Point2D 
from junctions.Intersection import Intersection
from extensions.ExtendedRoad import ExtendedRoad
from shapely.geometry import Polygon
from shapely.ops import unary_union
from sympy import Point, Line
import matplotlib.pyplot as plt
import math
from junctions.StandardCurveTypes import StandardCurveTypes


class Color(Enum):
    CENTER_LANE = 'r'
    LEFT_LANE = 'g'
    RIGHT_LANE = 'g'


class IntersectionDrawer():
    def __init__(self, intersection) -> None:
        self.intersection = intersection
        self.road_polygon = {} # key - road id, val - 1 polygon
        self.xVal = []
        self.yVal = []
        self.color = []
        self.lanewidth = 3
        self.two_road_overlap_geom = []
        self.plot_pair = {} # key road1, road2 || val -> 2 plot
        pass 


# TODO direction of left lane and right depends on lane width
#       currently just concerned about the area
# TODO straight line drawing angle may be not correct

    def draw_intersection(self, step_size = 0.1):
        # print('intersection ID ', self.intersection.id)
        for road in self.intersection.incidentRoads:
            # print('pretend there is straight road ... ')
            # print('incident road ID ', road.id)
            # if road.id == straight_road:
            self.create_coord_list_for_incident_road(road)

        print('internal connection road #', len(self.intersection.internalConnectionRoads))
        for road in self.intersection.internalConnectionRoads:
            # if road.id == parampoly_id:
            # print('connection road id ', road.id)
            self.create_coord_list_for_parampoly_road(road, step_size)

        for i in range(len(self.xVal)):
            plt.plot(self.xVal[i], self.yVal[i], color=self.color[i].value)
        plt.show()
        pass


    def get_plot_two_parampoly_with_straight_road(self, parampoly1, parampoly2):
        
        for road in self.intersection.incidentRoads:
            self.create_coord_list_for_incident_road(road)
        for road in self.intersection.internalConnectionRoads:
            if road.id == parampoly1 or road.id == parampoly2:
                self.create_coord_list_for_parampoly_road(road, 0.1)
        for i in range(len(self.xVal)):
            plt.plot(self.xVal[i], self.yVal[i], color=self.color[i].value)
        return plt
        # pass
    
    # def get_plot_two_parampoly_overlap(self, )

    def draw_intersection_area(self):
        # print('drawing intersection area ', len(self.road_polygon))
        result_polygon = Polygon()
        for road in self.intersection.internalConnectionRoads:
            polygon = self.road_polygon[road.id]
            result_polygon = unary_union([result_polygon, polygon])
        print('intersection area ', result_polygon.area)
        x, y = result_polygon.exterior.xy
        plt.fill(x, y, color = 'c')
        plt.show()
        pass

    def draw_road_overlap(self):
        all_road_polygon_inside_intersection = []
        road_id = []
        two_road_overlap_geom = []
        for road in self.intersection.internalConnectionRoads:
            if self.check_key_exist(road.id):
                polygon = self.road_polygon[road.id]
                all_road_polygon_inside_intersection.append(polygon)
                road_id.append(road.id)

        for i in range(len(all_road_polygon_inside_intersection)-1):
            for j in range(i+1, len(all_road_polygon_inside_intersection)):
                overlap = all_road_polygon_inside_intersection[i].intersection(all_road_polygon_inside_intersection[j])
                # print('overlap between ', road_id[i], ' and ', road_id[j], ' type ', overlap.geom_type)
                if overlap.geom_type == 'GeometryCollection':
                    for geom in overlap:
                        if geom.geom_type == 'Polygon':
                            two_road_overlap_geom.append(geom)
                        # print('geom collection ', geom.geom_type)
                if overlap.geom_type == 'Polygon':
                    two_road_overlap_geom.append(overlap)
        
         
        combined_ploygon = unary_union(two_road_overlap_geom)
        print('combined polytype ', combined_ploygon.geom_type)
        # print('combined exterior ', combined_ploygon.exterior)
        x, y = combined_ploygon.exterior.xy
        plt.plot(x, y, color= 'g')
        plt.show()
        # print('combined interior ', combined_ploygon.interior)


        for i in range(len(two_road_overlap_geom)):
            if two_road_overlap_geom[i].exterior.length != 0:
                # print('polygon ', two_road_overlap_geom[i].geom_type)
                x, y = two_road_overlap_geom[i].exterior.xy
                plt.plot(x, y, color= 'b')
            else:
                print()
                # print(two_road_overlap_geom[i].geom_type)
                # coord = two_road_overlap_geom[i].exterior
                # print(coord)
        plt.show()
        # return two_road_overlap_geom
        pass
    
    def append_in_polygon_dict(self, road_id, polygon):
        if self.check_key_exist(road_id): 
            # print('key exist ')
            exisiting_polygon = self.road_polygon[road_id]
            merged_polygon = unary_union([exisiting_polygon, polygon])
            self.road_polygon[road_id] = merged_polygon
            # print('merging polygon')
        else:
            self.road_polygon[road_id] = polygon
            # print('appending new polygon ')
        pass

    def check_key_exist(self, key):
        try:
            value = self.road_polygon[key]
            return True
        except KeyError:
            return False

    def create_coord_list_for_incident_road(self, road):
        # print('incident roads ', road)
        # print('road curve type ', road.curveType)

        start_coordinate = road.getAdjustedStartPosition()
        end_coordinate = road.getAdjustedEndPosition()
        # print('start_position ', start_coordinate, ' end_position ', end_coordinate)

        start_point = Point(start_coordinate[0], start_coordinate[1])
        end_point = Point(end_coordinate[0], end_coordinate[1])

        # start_point, end_point = end_point, start_point

        self.arrange_and_append_line_with_color(start_point, end_point, Color.CENTER_LANE)
        
        center_line = Line(start_point, end_point)
        
        # print('lanesection len ', len(road.lanes.lanesections))

        lanesection = road.lanes.lanesections[0]
        left_lanes = lanesection.leftlanes
        right_lanes = lanesection.rightlanes
        
        # print('left and right lanes len ', len(left_lanes), len(right_lanes))

        for lane_index in range(0, len(left_lanes)):
            leftlane_start, leftlane_end = self.get_lane_start_and_end(-self.lanewidth*(lane_index+1), center_line)
            self.arrange_and_append_line_with_color(leftlane_start, leftlane_end, Color.LEFT_LANE)
            polygon = self.create_lane_polygon_straight_road(center_line.p1, center_line.p2, leftlane_start, leftlane_end)
            self.append_in_polygon_dict(road.id, polygon)
            # self.road_polygon[road.id] = polygon
            # print('check if key exist ', self.check_key_exist(road.id))
            # print('polygon ', polygon)

        for lane_index in range(0, len(right_lanes)):
            rightlane_start, rightlane_end = self.get_lane_start_and_end(self.lanewidth*(lane_index+1), center_line)
            self.arrange_and_append_line_with_color(rightlane_start, rightlane_end, Color.RIGHT_LANE)
            polygon = self.create_lane_polygon_straight_road(center_line.p1, center_line.p2, rightlane_start, rightlane_end)
            self.append_in_polygon_dict(road.id, polygon)
            # print('right lane', rightlane_start, rightlane_end)

        pass

    def create_lane_polygon_straight_road(self, centerlane_start, centerlane_end, lane_start, lane_end):
        polygon = Polygon([centerlane_start, centerlane_end, lane_end, lane_start])
        # print(centerlane_start, centerlane_end, lane_start, lane_end)
        return polygon
    
    # def create_lane_polygon(self, xVal_center, yVal_center, xVal_lane, yVal_lane):
    #     array_size = len(xVal_center)
    #     # print('array size ', array_size)
    #     polygon = np.empty((2*array_size, 2))
    #     for i in range(0, array_size):
    #         polygon[i][0], polygon[i][1] = xVal_center[i], yVal_center[i]
    #     for i in range(array_size, 2*array_size):
    #         polygon[i][0], polygon[i][1] = xVal_lane[array_size-i-1], yVal_lane[array_size-i-1]

    #     polygon = Polygon(polygon)        
    #     return polygon

    def create_lane_polygon_parampoly_road(self, center_line_points, lane_points):
        array_size = len(center_line_points[0])
        polygon = np.empty((2*array_size, 2))
        for i in range(0, array_size):
            polygon[i][0], polygon[i][1] = center_line_points[0][i], center_line_points[1][i]
        for i in range(array_size, 2*array_size):
            polygon[i][0], polygon[i][1] = lane_points[0][array_size-i-1], lane_points[1][array_size-i-1]
        
        polygon = Polygon(polygon)        
        return polygon


    def get_lane_start_and_end(self, lane_width, center_line):
        # print('draw line ', lane_width, center_line, color)
        parallel_line = self.calculate_parallel_line_at_distance(center_line, lane_width)
        perpendicular_at_start = center_line.perpendicular_line(center_line.p1)
        perpendicular_at_end = center_line.perpendicular_line(center_line.p2)

        # print('angle perpendicular line start ', center_line.angle_between(perpendicular_at_start))
        # print('angle perpendicular line end ', center_line.angle_between(perpendicular_at_end))

        parallel_point_at_start = perpendicular_at_start.intersection(parallel_line)[0]
        parallel_point_at_end = perpendicular_at_end.intersection(parallel_line)[0]
        # print('parallel point ', parallel_point_at_start, parallel_point_at_end)
        return parallel_point_at_start, parallel_point_at_end
        # pass

    def calculate_parallel_line_at_distance(self, line, distance):
        a, b, c = line.coefficients # ax + by + c = 0
        m, c = -(a/b), -(c/b) # y = mx + c
        abs_diff = distance*math.sqrt(m**2 + 1)
        new_c = c - abs_diff
        new_line = Line(Point(-new_c/m, 0), Point(0, new_c))
        # print('calculating parallel line angle ', math.degrees(new_line.angle_between(line)))
        return new_line


    def arrange_and_append_line_with_color(self, start_point, end_point, color):
        x_val, y_val = self.arrange_coordinate(start_point, end_point)
        self.append_coordinate_list_and_color(x_val, y_val, color)
        pass

    def append_coordinate_list_and_color(self, x_val, y_val, color):
        self.append_coordinate_list(x_val, y_val)
        self.append_color(color)

    def arrange_coordinate(self, start, end):
        x_val = [start.x, end.x]
        y_val = [start.y, end.y]
        return x_val,y_val

    def append_coordinate_list(self, x_val, y_val):
        self.xVal.append(x_val)
        self.yVal.append(y_val)
        pass

    def append_color(self, color):
        self.color.append(color)


    def create_coord_list_for_parampoly_road(self, road, step_size = 0.1):
        if road.curveType != StandardCurveTypes.Poly:
            print('not a parampoly road ')
            return
        if road.planViewNotAdjusted():
            print('can not work with raw geometry ')
            return 

        geom = road.planview._adjusted_geometries[0]
        lane_sections = road.lanes.lanesections
        # print('adjusted geom ', len(geom))
        aU, bU, cU, dU, aV, bV, cV, dV = self.get_parampoly_coefficiants(geom)
        # print('U and V ', aU, bU, cU, dU, aV, bV, cV, dV)

        start_position = road.getAdjustedStartPosition()
        start_heading = start_position[2]
        start_point = Point(start_position[0],start_position[1])

        # print('start position ', start_position)

        xVal_centerline, yVal_centerline = [], []
        xVal_leftlane, yVal_leftlane = [], []
        xVal_rightlane, yVal_rightlane = [], []


        for i in np.arange(0, 1+step_size, step_size):
            # print('i ', i)
            x, y = self.get_abs_coordinate_for_parampoly(aU, bU, cU, dU, aV, bV, cV, dV, i)
            point_wrt_origin = Point(x, y)
            x_trans, y_trans = self.transform_to_geometric_start_point(start_heading, start_point, point_wrt_origin)
            # print('abs ', x, y)
            
            xVal_centerline.append(x_trans)
            yVal_centerline.append(y_trans)

            x_diff_val, y_diff_val = self.get_differentiated_value_for_parampoly(bU, cU, dU, bV, cV, dV, i)

            # print('# leftlanes, # rightlanes ',len(lane_sections[0].leftlanes), len(lane_sections[0].rightlanes))

        #     if len(lane_sections[0].leftlanes) != 0:
        #         x_trans_left, y_trans_left = self.calc_coordinate_wrt_geometric_start(start_heading, 
        #                                                                               start_point, 
        #                                                                               self.lanewidth, 
        #                                                                               x_diff_val, y_diff_val, 
        #                                                                               point_wrt_origin)
        #         xVal_leftlane.append(x_trans_left)
        #         yVal_leftlane.append(y_trans_left)
        #         # print('inside leftlanes ', len(lane_sections[0].leftlanes))
            # start_point = Point(0, 0)
            if len(lane_sections[0].rightlanes) != 0:
                x_trans_right, y_trans_right = self.calc_coordinate_wrt_geometric_start(start_heading, 
                                                                                        start_point, 
                                                                                        +self.lanewidth, 
                                                                                        x_diff_val, y_diff_val, 
                                                                                        point_wrt_origin)
                xVal_rightlane.append(x_trans_right)
                yVal_rightlane.append(y_trans_right)
                # print('inside rightlanes ', len(lane_sections[0].rightlanes))

        # self.create_lane_polygon_parampoly_road((xVal_centerline, yVal_centerline), (xVal_leftlane, yVal_leftlane))
        self.append_coordinate_list_and_color(xVal_centerline, yVal_centerline, Color.CENTER_LANE)
        # self.append_coordinate_list_and_color(xVal_leftlane, yVal_leftlane, Color.LEFT_LANE)
        self.append_coordinate_list_and_color(xVal_rightlane, yVal_rightlane, Color.RIGHT_LANE)
        
        polygon = self.create_lane_polygon_parampoly_road((xVal_centerline, yVal_centerline), (xVal_rightlane, yVal_rightlane))
        self.append_in_polygon_dict(road.id, polygon)



        # print('parampoly curve type ', road.curveType)
        # print('number of lanesection ', len(road.getLaneSections()[0]))
        # print('center lane ', road.getLaneSections()[0].centerlane)
        # print('# left lane ',len(road.getLaneSections()[0].leftlanes))
        # print('# right lane ', len(road.getLaneSections()[0].rightlanes))
        pass

    def transform_to_geometric_start_point(self, h_start, geometric_start_point, point_wrt_origin):
        x_trans = point_wrt_origin.x*math.cos(h_start) - point_wrt_origin.y*math.sin(h_start) + geometric_start_point.x
        y_trans = point_wrt_origin.x*math.sin(h_start) + point_wrt_origin.y*math.cos(h_start) + geometric_start_point.y
        return x_trans,y_trans

    def calc_coordinate_wrt_geometric_start(self, h_start, start_point, lanewidth, x_diff_val, y_diff_val, centerline_point):
        x_leftlane, y_leftlane = self.calc_coordinate_for_lane(lanewidth, centerline_point, x_diff_val, y_diff_val)
        point_wrt_origin = Point(x_leftlane, y_leftlane)
        x_trans_left, y_trans_left = self.transform_to_geometric_start_point(h_start, start_point, point_wrt_origin)
        return x_trans_left,y_trans_left

    def calc_coordinate_for_lane(self, lanewidth, point_wrt_origin, x_diff_val, y_diff_val): 
        temp = lanewidth/math.sqrt(x_diff_val**2 + y_diff_val**2)
        x_leftlane = point_wrt_origin.x + temp*y_diff_val
        y_leftlane = point_wrt_origin.y - temp*x_diff_val
        return x_leftlane,y_leftlane

    def get_differentiated_value_for_parampoly(self, bU, cU, dU, bV, cV, dV, i):
        x_diff_val = bU + 2*cU*i + 3*dU*(i**2)
        y_diff_val = bV + 2*cV*i + 3*dV*(i**2)
        return x_diff_val,y_diff_val

    def get_abs_coordinate_for_parampoly(self, aU, bU, cU, dU, aV, bV, cV, dV, i):
        x_abs = aU + bU*i + cU*(i**2) + dU*(i**3)
        y_abs = aV + bV*i + cV*(i**2) + dV*(i**3)
        return x_abs,y_abs

    def get_parampoly_coefficiants(self, geom):
        _attr = geom.geom_type.get_attributes()
        aU, bU, cU, dU = float(_attr['aU']), float(_attr['bU']), float(_attr['cU']), float(_attr['dU'])
        aV, bV, cV, dV = float(_attr['aV']), float(_attr['bV']), float(_attr['cV']), float(_attr['dV'])
        return aU,bU,cU,dU,aV,bV,cV,dV