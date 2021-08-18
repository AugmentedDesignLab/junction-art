
from sympy.geometry.point import Point2D
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

    # def fill_line_points(self, step):

    #     xVal_centerline = np.zeros([])

    #     return super().fill_line_points()

    def get_center_coordinates_wrt_origin(self, aU, bU, cU, dU, aV, bV, cV, dV, step):
        
        array_size = np.int64((1/step)+1)

        coff1 = np.array([[aU, bU, cU, dU]])
        coff2 = np.array([[aV, bV, cV, dV]])

        mat_i = np.array([i for i in np.arange(0, 1+step, step)])
        new_mat = np.zeros((4, array_size))
        for i in range(4):
            new_mat[i] = mat_i**i

        xVal = coff1.dot(new_mat)
        yVal = coff2.dot(new_mat)

        return xVal[0], yVal[0]

    def get_differentiated_values(self, bU, cU, dU, bV, cV, dV, step):
        
        array_size = np.int64((1/step)+1)

        coff1 = np.array([[bU, 2*cU, 3*dU]])
        coff2 = np.array([[bV, 2*cV, 3*dV]])

        mat_i = np.array([i for i in np.arange(0, 1+step, step)])
        new_mat = np.zeros((3, array_size))
        for i in range(3):
            new_mat[i] = mat_i**i

        finalx = coff1.dot(new_mat)
        finaly = coff2.dot(new_mat)

        return finalx[0], finaly[0]

    def fill_line_points(self, step = 0.1):

        # taking geometry for coefficient
        geom = self.road.planview._adjusted_geometries[0]
        lane_sections = self.road.lanes.lanesections

        # coefficient from planview
        aU, bU, cU, dU, aV, bV, cV, dV = self.get_parampoly_coefficiants(geom)
        # print('coeff U', aU, bU, cU, dU)
        # print('coeff V', aV, bV, cV, dV)

        # start position and heading for final geometric transformation
        start_position = self.road.getAdjustedStartPosition()
        start_heading = start_position[2]
        start_point = Point2D(start_position[0],start_position[1])

        # initialize
        xVal_centerline, yVal_centerline = [], []
        xVal_leftlane, yVal_leftlane = [], []
        xVal_rightlane, yVal_rightlane = [], []

        # print('start ', start_point, start_heading)
        # for loop: interpolating from paramter [0, 1] for intermediate points

        xVal_center_wrt_origin, yVal_center_wrt_origin = self.get_center_coordinates_wrt_origin(aU, bU, cU, dU, aV, bV, cV, dV, step)

        xVal_centerline = xVal_center_wrt_origin*math.cos(start_heading) - yVal_center_wrt_origin*math.sin(start_heading) + start_point.x
        yVal_centerline = xVal_center_wrt_origin*math.sin(start_heading) + yVal_center_wrt_origin*math.cos(start_heading) + start_point.y

        self.center_line_points.append(xVal_centerline.tolist())
        self.center_line_points.append(yVal_centerline.tolist())
        
        if len(self.rightlanes) != 0:
            x_diff_val, y_diff_val = self.get_differentiated_values(bU, cU, dU, bV, cV, dV, step)

            temp = self.lanewidth / np.sqrt(x_diff_val**2 + y_diff_val**2)
            x_lane_right_wrt_origin = xVal_center_wrt_origin + temp*y_diff_val
            y_lane_right_wrt_origin = yVal_center_wrt_origin - temp*x_diff_val


            xVal_rightlane = x_lane_right_wrt_origin*math.cos(start_heading) - y_lane_right_wrt_origin*math.sin(start_heading) + start_point.x
            yVal_rightlane = x_lane_right_wrt_origin*math.sin(start_heading) + y_lane_right_wrt_origin*math.cos(start_heading) + start_point.y        

            self.right_line_points.append(xVal_rightlane.tolist())
            self.right_line_points.append(yVal_rightlane.tolist())



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


    






