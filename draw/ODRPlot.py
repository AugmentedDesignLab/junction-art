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
                self.draw_straight_road(road)
                # print()
            # elif road.curveType == StandardCurveTypes.Poly:
            #     if road.id < 6:
            #         # self.draw_poly_road(road)
            #         print(road.id)


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

    def arrange_and_append_coordinate(self, start_point, end_point):
        x_val, y_val = self.arrange_coordinate(start_point, end_point)
        self.append_coordinate(x_val, y_val)

    def arrange_coordinate(self, start_point, end_point):
        x_val = [start_point.x, end_point.x]
        y_val = [start_point.y, end_point.y]
        return x_val,y_val

    def append_coordinate(self, x_val, y_val):
        self.xVal.append(x_val)
        self.yVal.append(y_val)
        pass

    def calculate_parallel_line_at_distance(self, line, distance):
        a, b, c = line.coefficients # ax + by + c = 0
        m, c = -(a/b), -(c/b) # y = mx + c
        abs_diff = distance*math.sqrt(m**2 + 1)
        new_c = c - abs_diff
        line = Line(Point(-new_c/m, 0), Point(0, new_c))
        return line


    def draw_poly_road(self, ParamPolyRoad):
        pv = ParamPolyRoad.planview
        adjusted_geoms = pv._adjusted_geometries
        x_start, y_start, h_start = pv.get_start_point()
        x_end, y_end, h_end = pv.get_end_point()

        # print('start ', x_start, y_start, h_start)
        # print('end ', x_end, y_end, h_end)

        for geom in adjusted_geoms:
            _attr = geom.geom_type.get_attributes()

            aU, bU, cU, dU = float(_attr['aU']), float(_attr['bU']), float(_attr['cU']), float(_attr['dU'])
            aV, bV, cV, dV = float(_attr['aV']), float(_attr['bV']), float(_attr['cV']), float(_attr['dV'])

            # print('U ',aU, bU, cU, dU)
            # print('V ',aV, bV, cV, dV)

            x_val = []
            y_val = []

            # h_start = h_start - h_end

            for i in np.arange(0, 1.1, 0.1):
                # getting the value from the actual equation from (0, 0) origin
                x_abs = aU + bU*i + cU*(i**2) + dU*(i**3)
                y_abs = aV + bV*i + cV*(i**2) + dV*(i**3)

                # transforming the points from the end of incident roads
                # TODO: transform wrt contact point
                x_trans = x_abs*math.cos(h_start) - y_abs*math.sin(h_start) + x_start
                y_trans = x_abs*math.sin(h_start) + y_abs*math.cos(h_start) + y_start

                # x_trans = x_abs
                # y_trans = y_abs

                x_val.append(x_trans)
                y_val.append(y_trans)
                # print(i, x_abs, y_abs)

            self.xVal.append(x_val)
            self.yVal.append(y_val)
        pass
