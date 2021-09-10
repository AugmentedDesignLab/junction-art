from shapely.geometry.base import EmptyGeometry
from junctionart.junctions.StraightRoadBuilder import StraightRoadBuilder
from junctionart.extensions.moreHelpers import laneWidths
import math
import matplotlib.pyplot as plt
import pyodrx
from junctionart.extensions.ExtendedOpenDrive import ExtendedOpenDrive
from junctionart.junctions.StandardCurveTypes import StandardCurveTypes
import numpy as np
from shapely.geometry import Polygon
from shapely.ops import unary_union
from sympy import Point, Line

class ODRPlot():
    def __init__(self, odr):
        self.odr = odr
        self.roads = odr.roads
        self.xVal = []
        self.yVal = []
        self.color = []
        self.parampoly_polygons = {}
        self.intersection_polygon = None
        self.overlapping_polygon = []

        # self.lanewidth = 5


    def draw_odr(self, lanewidth=3, low=0, high=10):
        for key in self.odr.roads:
            road = self.odr.roads.get(key)
            if road.curveType == StandardCurveTypes.Line:
                self.draw_straight_road(road, lanewidth)
                print()
            elif road.curveType == StandardCurveTypes.Poly and road.id < high and road.id > low:
                self.draw_poly_road(road, lanewidth, 0.2)
                # print(road.id)

        for i in range(len(self.xVal)):
            plt.plot(self.xVal[i], self.yVal[i], color=self.color[i])
        plt.show()
        pass
    
    def draw_intersection_area(self):
        self.intersection_polygon = self.combine_parampoly_polygon()
        print('intersection area ', self.intersection_polygon.area)
        x,y = self.intersection_polygon.exterior.xy
        plt.fill(x, y, color='r')
        plt.show()
        pass

    def draw_conflict_zone_polygon(self, length_threshold=5, area_threshold=10):
        parampoly_polygon_list = []
        two_road_intersecting_area_polygon = []
        road_id = []
        for key in self.parampoly_polygons:
            parampoly_polygon_list.append(self.parampoly_polygons[key])
            road_id.append(key)

        for i in range(0, len(parampoly_polygon_list)-1):
            for j in range(i+1, len(parampoly_polygon_list)):
                # print('bounds ', parampoly_polygon_list[i].bounds, parampoly_polygon_list[j].bounds)
                # print('length ', parampoly_polygon_list[i].exterior.length, parampoly_polygon_list[j].exterior.length)
                area_i = parampoly_polygon_list[i].area
                area_j = parampoly_polygon_list[j].area
                print('road id : area diff ',road_id[i], road_id[j], area_i - area_j)

                # len_i = parampoly_polygon_list[i].lenght
                # len_j = parampoly_polygon_list[j].lenght
                # print('length_diff ', len_i - len_j)
                intersection_polygon = parampoly_polygon_list[i].intersection(parampoly_polygon_list[j])
                if intersection_polygon.exterior.length != 0:
                    x, y = intersection_polygon.exterior.xy
                    plt.plot(x, y, color='g')

        #         if intersection_polygon.type == 'MultiPolygon':
        #             for polygon in intersection_polygon:
        #                 two_road_intersecting_area_polygon.append(polygon)

        #         elif intersection_polygon.type == 'Polygon' and intersection_polygon is not None:
        #             two_road_intersecting_area_polygon.append(intersection_polygon)

        #         else:
        #             print('intersection polygon type ', intersection_polygon.type)

        # for conflict_zone in two_road_intersecting_area_polygon:
        #     if conflict_zone.type == 'Polygon' and conflict_zone.exterior.length != 0:
        #         # print('conflict zone type ', conflict_zone.type)
        #         # print('cz ', conflict_zone)
        #         # print(conflict_zone.exterior.length)
        #         x, y = conflict_zone.exterior.xy
        #         plt.plot(x, y, color='g')

        plt.show()
        pass


    def draw_road_polygon(self):
        parampoly_polygon_list = []
        for key in self.parampoly_polygons:
            parampoly_polygon_list.append(self.parampoly_polygons[key])

        for polygon in parampoly_polygon_list:
            x,y = polygon.exterior.xy
            plt.plot(x, y, color='k')
        plt.show()

    def draw_straight_road(self, StraightRoad, lanewidth=3):
        
        start_coordinate = StraightRoad.planview.get_start_point()
        end_coordinate = StraightRoad.planview.get_end_point()

        start_point = Point(start_coordinate[0], start_coordinate[1])
        end_point = Point(end_coordinate[0], end_coordinate[1])

        self.arrange_and_append_coordinate(start_point, end_point)
        self.color.append('r')

        center_line = Line(start_point, end_point)
        
        for lanesection in StraightRoad.lanes.lanesections:
            for lane_index in range (0, len(lanesection.leftlanes)):
                self.draw_lane(lanewidth*(lane_index + 1), center_line)
            for lane_index in range (0, len(lanesection.rightlanes)):
                self.draw_lane(-lanewidth*(lane_index + 1), center_line)

        pass

    def draw_lane(self, lane_width, center_line):
        parallel_line = self.calculate_parallel_line_at_distance(center_line, lane_width)
        perpendicular_at_start = center_line.perpendicular_line(center_line.p1)
        perpendicular_at_end = center_line.perpendicular_line(center_line.p2)
        parallel_point_at_start = perpendicular_at_start.intersection(parallel_line)[0]
        parallel_point_at_end = perpendicular_at_end.intersection(parallel_line)[0]
        self.arrange_and_append_coordinate(parallel_point_at_start, parallel_point_at_end)
        color = 'g' if lane_width>0 else 'b'
        self.color.append(color)
        pass

    def calculate_parallel_line_at_distance(self, line, distance):
        a, b, c = line.coefficients # ax + by + c = 0
        m, c = -(a/b), -(c/b) # y = mx + c
        abs_diff = distance*math.sqrt(m**2 + 1)
        new_c = c - abs_diff
        line = Line(Point(-new_c/m, 0), Point(0, new_c))
        return line

    def arrange_and_append_coordinate(self, start_point, end_point):
        x_val, y_val = self.arrange_coordinate(start_point, end_point)
        self.append_coordinate(x_val, y_val)
        pass

    def arrange_coordinate(self, start, end):
        x_val = [start.x, end.x]
        y_val = [start.y, end.y]
        return x_val,y_val

    def append_coordinate(self, x_val, y_val):
        self.xVal.append(x_val)
        self.yVal.append(y_val)
        pass

    


    def draw_poly_road(self, ParamPolyRoad, lanewidth=3, step=0.1):

        x_start, y_start, h_start = ParamPolyRoad.planview.get_start_point()
        start_point = Point(x_start, y_start)

        for geom in ParamPolyRoad.planview._adjusted_geometries:

            aU, bU, cU, dU, aV, bV, cV, dV = self.get_parampoly_coefficiants(geom)
            xVal_centerline, yVal_centerline = [], []
            xVal_leftlane, yVal_leftlane = [], []
            xVal_rightlane, yVal_rightlane = [], []

            for i in np.arange(0, 1+step, step):
                # getting the value from the actual equation from (0, 0) origin
                x_abs, y_abs = self.get_abs_coordinate_for_parampoly(aU, bU, cU, dU, aV, bV, cV, dV, i)

                # getting the differentiated value
                x_diff_val, y_diff_val = self.get_differentiated_value_for_parampoly(bU, cU, dU, bV, cV, dV, i)
                
                # transforming the points from the end of incident roads
                # TODO: transform wrt contact point
                centerline_point = Point(x_abs, y_abs)
                x_trans, y_trans = self.transform_to_geometric_start_point(h_start, start_point, centerline_point)
                xVal_centerline.append(x_trans)
                yVal_centerline.append(y_trans)

                # x_trans = x_abs
                # y_trans = y_abs
                # print('# leftlane', len(ParamPolyRoad.lanes.lanesections[0].leftlanes), '# rightlane ', len(ParamPolyRoad.lanes.lanesections[0].rightlanes))
                if len(ParamPolyRoad.lanes.lanesections[0].leftlanes) != 0:
                    x_trans_left, y_trans_left = self.calc_coordinate_wrt_geometric_start(h_start, start_point, +lanewidth, x_diff_val, y_diff_val, centerline_point)
                    xVal_leftlane.append(x_trans_left)
                    yVal_leftlane.append(y_trans_left)

                if len(ParamPolyRoad.lanes.lanesections[0].rightlanes) != 0:
                    x_trans_right, y_trans_right = self.calc_coordinate_wrt_geometric_start(h_start, start_point, -lanewidth, x_diff_val, y_diff_val, centerline_point)
                    xVal_rightlane.append(x_trans_right)
                    yVal_rightlane.append(y_trans_right)

            self.append_coordinate(xVal_centerline, yVal_centerline)
            self.color.append('r')
            # print('parampoly road ', ParamPolyRoad.id)
            polygon_leftlane, polygon_rightlane = None, None
            if len(ParamPolyRoad.lanes.lanesections[0].leftlanes) != 0:
                self.append_coordinate(xVal_leftlane, yVal_leftlane)
                self.color.append('g')
                polygon_leftlane = self.create_lane_polygon(xVal_centerline, yVal_centerline, xVal_leftlane, yVal_leftlane)

            if len(ParamPolyRoad.lanes.lanesections[0].rightlanes) != 0:
                self.append_coordinate(xVal_rightlane, yVal_rightlane)
                self.color.append('b')
                polygon_rightlane = self.create_lane_polygon(xVal_centerline, yVal_centerline, xVal_rightlane, yVal_rightlane)
            
            self.parampoly_polygons[ParamPolyRoad.id] = (polygon_rightlane, polygon_rightlane)
            if polygon_leftlane is None:
                combined_polygon = polygon_rightlane
            elif polygon_rightlane is None:
                combined_polygon = polygon_leftlane
            else:
                combined_polygon = unary_union([polygon_leftlane, polygon_rightlane])
            
            self.parampoly_polygons[ParamPolyRoad.id] = combined_polygon
        pass

    def create_lane_polygon(self, xVal_center, yVal_center, xVal_lane, yVal_lane):
        array_size = len(xVal_center)
        # print('array size ', array_size)
        polygon = np.empty((2*array_size, 2))
        for i in range(0, array_size):
            polygon[i][0], polygon[i][1] = xVal_center[i], yVal_center[i]
        for i in range(array_size, 2*array_size):
            polygon[i][0], polygon[i][1] = xVal_lane[array_size-i-1], yVal_lane[array_size-i-1]

        polygon = Polygon(polygon)        
        return polygon

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

    def get_parampoly_coefficiants(self, geom):
        _attr = geom.geom_type.get_attributes()
        aU, bU, cU, dU = float(_attr['aU']), float(_attr['bU']), float(_attr['cU']), float(_attr['dU'])
        aV, bV, cV, dV = float(_attr['aV']), float(_attr['bV']), float(_attr['cV']), float(_attr['dV'])
        return aU,bU,cU,dU,aV,bV,cV,dV

    def transform_to_geometric_start_point(self, h_start, geometric_start_point, point_wrt_origin):
        x_trans = point_wrt_origin.x*math.cos(h_start) - point_wrt_origin.y*math.sin(h_start) + geometric_start_point.x
        y_trans = point_wrt_origin.x*math.sin(h_start) + point_wrt_origin.y*math.cos(h_start) + geometric_start_point.y
        return x_trans,y_trans

    def get_differentiated_value_for_parampoly(self, bU, cU, dU, bV, cV, dV, i):
        x_diff_val = bU + 2*cU*i + 3*dU*(i**2)
        y_diff_val = bV + 2*cV*i + 3*dV*(i**2)
        return x_diff_val,y_diff_val

    def get_abs_coordinate_for_parampoly(self, aU, bU, cU, dU, aV, bV, cV, dV, i):
        x_abs = aU + bU*i + cU*(i**2) + dU*(i**3)
        y_abs = aV + bV*i + cV*(i**2) + dV*(i**3)
        return x_abs,y_abs

    def combine_parampoly_polygon(self):
        result = Polygon()
        polygon_list = []
        for key in self.parampoly_polygons:
            # polygon_list.append(self.parampoly_polygons[key])
            polygon = self.parampoly_polygons[key]
            # print('polygon ', polygon)
            result = unary_union([polygon, result])
            # print()
            # print('key value ', key, self.parampoly_polygons[key])
        return result

