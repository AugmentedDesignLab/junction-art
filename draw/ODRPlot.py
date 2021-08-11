from extensions.moreHelpers import laneWidths
import math
import matplotlib.pyplot as plt
import pyodrx
from extensions.ExtendedOpenDrive import ExtendedOpenDrive
from junctions.StandardCurveTypes import StandardCurveTypes
import numpy as np
from sympy import Point, Line

class ODRPlot():
    def __init__(self, odr):
        self.odr = odr
        self.roads = odr.roads
        self.xVal = []
        self.yVal = []


    def draw_odr(self):
        for key in self.odr.roads:
            road = self.odr.roads.get(key)
            if road.curveType == StandardCurveTypes.Line:
                # self.draw_straight_road(road)
                print()
            elif road.curveType == StandardCurveTypes.Poly and road.id == 1:
                self.draw_poly_road(road)
                # print(road.id)


        for i in range(len(self.xVal)):
            plt.plot(self.xVal[i], self.yVal[i])

        # plt.plot(self.xVal, self.yVal)
        plt.show()
        pass

    def draw_straight_road(self, StraightRoad, cp1=pyodrx.ContactPoint.start):
        
        start_coordinate = StraightRoad.planview.get_start_point()
        end_coordinate = StraightRoad.planview.get_end_point()

        start_point = Point(start_coordinate[0], start_coordinate[1])
        end_point = Point(end_coordinate[0], end_coordinate[1])

        self.arrange_and_append_coordinate(start_point, end_point)

        lane_width = 3

        center_line = Line(start_point, end_point)
        
        for lanesection in StraightRoad.lanes.lanesections:
            for lane_index in range (0, len(lanesection.leftlanes)):
                self.draw_lane(lane_width*(lane_index + 1), center_line)
            for lane_index in range (0, len(lanesection.rightlanes)):
                self.draw_lane(-lane_width*(lane_index + 1), center_line)

        pass

    def draw_lane(self, lane_width, center_line):
        parallel_line = self.calculate_parallel_line_at_distance(center_line, lane_width)
        perpendicular_at_start = center_line.perpendicular_line(center_line.p1)
        perpendicular_at_end = center_line.perpendicular_line(center_line.p2)
        parallel_point_at_start = perpendicular_at_start.intersection(parallel_line)[0]
        parallel_point_at_end = perpendicular_at_end.intersection(parallel_line)[0]
        self.arrange_and_append_coordinate(parallel_point_at_start, parallel_point_at_end)

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

    def arrange_coordinate(self, start, end):
        x_val = [start.x, end.x]
        y_val = [start.y, end.y]
        return x_val,y_val

    def append_coordinate(self, x_val, y_val):
        self.xVal.append(x_val)
        self.yVal.append(y_val)
        pass

    


    def draw_poly_road(self, ParamPolyRoad):

        x_start, y_start, h_start = ParamPolyRoad.planview.get_start_point()
        start_point = Point(x_start, y_start)

        lanewidth = 3

        # print('parampoly road  id ', ParamPolyRoad.id)
        lanesections = ParamPolyRoad.lanes.lanesections
        for lanesection in lanesections:
            print('left lanes ', lanesection.leftlanes)
            print('right lanes ', lanesection.rightlanes)
        for geom in ParamPolyRoad.planview._adjusted_geometries:

            aU, bU, cU, dU, aV, bV, cV, dV = self.get_parampoly_coefficiants(geom)

            xVal_centerline = []
            yVal_centerline = []

            xVal_leftlane = []
            yVal_leftlane = []

            xVal_rightlane = []
            yVal_rightlane = []

            for i in np.arange(0, 1.01, 0.01):
                # getting the value from the actual equation from (0, 0) origin
                x_abs, y_abs = self.get_abs_coordinate_for_parampoly(aU, bU, cU, dU, aV, bV, cV, dV, i)
                x_diff_val, y_diff_val = self.get_differentiated_value_for_parampoly(bU, cU, dU, bV, cV, dV, i)

                # transforming the points from the end of incident roads
                # TODO: transform wrt contact point
                point_wrt_origin = Point(x_abs, y_abs)
                x_trans, y_trans = self.transform_to_geometric_start_point(h_start, start_point, point_wrt_origin)
                xVal_centerline.append(x_trans)
                yVal_centerline.append(y_trans)

                # x_trans = x_abs
                # y_trans = y_abs
                x_leftlane, y_leftlane = self.calc_coordinate_for_lane(lanewidth, point_wrt_origin, x_diff_val, y_diff_val)
                xVal_leftlane.append(x_leftlane)
                yVal_leftlane.append(y_leftlane)

                x_rightlane, y_rightlane = self.calc_coordinate_for_lane(-lanewidth, point_wrt_origin, x_diff_val, y_diff_val)
                xVal_rightlane.append(x_rightlane)
                yVal_rightlane.append(y_rightlane)

                # x_original.append(x_abs)
                # y_original.append(y_abs)

                
                # print(i, x_abs, y_abs)

            # self.xVal.append(x_original)
            # self.yVal.append(y_original)


            self.append_coordinate(xVal_centerline, yVal_centerline)
            # self.xVal.append(xVal_centerline)
            # self.yVal.append(yVal_centerline)

            self.append_coordinate(xVal_leftlane, yVal_leftlane)
            # self.xVal.append(xVal_leftlane)
            # self.yVal.append(yVal_leftlane)

            self.append_coordinate(xVal_rightlane, yVal_rightlane)
            # self.xVal.append(x_val_rightlane)
            # self.yVal.append(y_val_rightlane)

            # self.xVal.append(x_val)
            # self.yVal.append(y_val)
        pass

    def calc_coordinate_for_lane(self, lanewidth, point_wrt_origin, x_diff_val, y_diff_val):
        temp = lanewidth*y_diff_val*x_diff_val/math.sqrt(x_diff_val**2 + y_diff_val**2)
        x_leftlane = point_wrt_origin.x + temp/x_diff_val
        y_leftlane = point_wrt_origin.y - temp/y_diff_val
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
