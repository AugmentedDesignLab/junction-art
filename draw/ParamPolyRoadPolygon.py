
from draw.RoadPolygon import RoadPolygon
import numpy as np
from junctions.StandardCurveTypes import StandardCurveTypes
import math
from shapely.geometry.polygon import Polygon
from shapely.ops import unary_union

# from shapely.geometry import Point
from sympy.geometry import Line2D, Point


class ParamPolyRoadPolygon(RoadPolygon):
    def __init__(self, road) -> None:
        super().__init__(road)

    def build_polygon(self, step = 0.1):
        # print('parampoly polygon building', self.road)
        if self.road.curveType != StandardCurveTypes.Poly:
            return print('cant draw if not polygon')

        self.fill_line_points(step)

        polygon = self.create_lane_polygon_parampoly_road((self.center_line_points[0], self.center_line_points[1]), (self.right_line_points[0], self.right_line_points[1]))

        self.polygon = polygon
        return self.polygon

    def create_lane_polygon_parampoly_road(self, center_line_points, lane_points):
        array_size = len(center_line_points[0])
        polygon = np.empty((2*array_size, 2))
        for i in range(0, array_size):
            polygon[i][0], polygon[i][1] = center_line_points[0][i], center_line_points[1][i]
        for i in range(array_size, 2*array_size):
            polygon[i][0], polygon[i][1] = lane_points[0][array_size-i-1], lane_points[1][array_size-i-1]
        
        polygon = Polygon(polygon)        
        return polygon

    def fill_line_points(self, step = 0.1):

        # taking geometry for coefficient
        geom = self.road.planview._adjusted_geometries[0]
        lane_sections = self.road.lanes.lanesections

        # coefficient from planview
        aU, bU, cU, dU, aV, bV, cV, dV = self.get_parampoly_coefficiants(geom)

        # start position and heading for final geometric transformation
        start_position = self.road.getAdjustedStartPosition()
        start_heading = start_position[2]
        start_point = Point(start_position[0],start_position[1])

        # initialize
        xVal_centerline, yVal_centerline = [], []
        xVal_leftlane, yVal_leftlane = [], []
        xVal_rightlane, yVal_rightlane = [], []

        # for loop: interpolating from paramter [0, 1] for intermediate points
        for i in np.arange(0, 1 + step, step):

            # center line 
            x, y = self.get_abs_coordinate_for_parampoly(aU, bU, cU, dU, aV, bV, cV, dV, i)
            point_wrt_origin = Point(x, y)
            x_trans, y_trans = self.transform_to_geometric_start_point(start_heading, start_point, point_wrt_origin)
            # center line point array 
            xVal_centerline.append(x_trans)
            yVal_centerline.append(y_trans)

            # points at the lane width
            x_diff_val, y_diff_val = self.get_differentiated_value_for_parampoly(bU, cU, dU, bV, cV, dV, i)

            if len(self.rightlanes) != 0:
                x_trans_right, y_trans_right = self.calc_coordinate_wrt_inertial_start(start_heading, 
                                                                                        start_point, 
                                                                                        +self.lanewidth, 
                                                                                        x_diff_val, y_diff_val, 
                                                                                        point_wrt_origin)
                xVal_rightlane.append(x_trans_right)
                yVal_rightlane.append(y_trans_right)



        self.center_line_points.append(xVal_centerline)
        self.center_line_points.append(yVal_centerline)

        self.right_line_points.append(xVal_rightlane)
        self.right_line_points.append(yVal_rightlane)

        return super().fill_line_points()


    def calc_coordinate_for_lane(self, lanewidth, point_wrt_origin, x_diff_val, y_diff_val): 
        temp = lanewidth/math.sqrt(x_diff_val**2 + y_diff_val**2)
        x_lane = point_wrt_origin.x + temp*y_diff_val
        y_lane = point_wrt_origin.y - temp*x_diff_val
        return x_lane,y_lane

    def calc_coordinate_wrt_inertial_start(self, h_start, start_point, lanewidth, x_diff_val, y_diff_val, centerline_point):
        x_lane, y_lane = self.calc_coordinate_for_lane(lanewidth, centerline_point, x_diff_val, y_diff_val)
        point_wrt_origin = Point(x_lane, y_lane)
        x_trans, y_trans = self.transform_to_geometric_start_point(h_start, start_point, point_wrt_origin)
        return x_trans,y_trans

    def get_differentiated_value_for_parampoly(self, bU, cU, dU, bV, cV, dV, i):
        x_diff_val = bU + 2*cU*i + 3*dU*(i**2)
        y_diff_val = bV + 2*cV*i + 3*dV*(i**2)
        return x_diff_val,y_diff_val

    def transform_to_geometric_start_point(self, h_start, geometric_start_point, point_wrt_origin):
        x_trans = point_wrt_origin.x*math.cos(h_start) - point_wrt_origin.y*math.sin(h_start) + geometric_start_point.x
        y_trans = point_wrt_origin.x*math.sin(h_start) + point_wrt_origin.y*math.cos(h_start) + geometric_start_point.y
        return x_trans,y_trans


    def get_abs_coordinate_for_parampoly(self, aU, bU, cU, dU, aV, bV, cV, dV, i):
        x_abs = aU + bU*i + cU*(i**2) + dU*(i**3)
        y_abs = aV + bV*i + cV*(i**2) + dV*(i**3)
        return x_abs,y_abs
    
    def get_parampoly_coefficiants(self, geom):
        _attr = geom.geom_type.get_attributes()
        aU, bU, cU, dU = float(_attr['aU']), float(_attr['bU']), float(_attr['cU']), float(_attr['dU'])
        aV, bV, cV, dV = float(_attr['aV']), float(_attr['bV']), float(_attr['cV']), float(_attr['dV'])
        return aU,bU,cU,dU,aV,bV,cV,dV






