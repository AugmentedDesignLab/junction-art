
# from draw.IntersectionPolygon import IntersectionPolygon
import numpy as np
from shapely.geometry.polygon import Polygon
from shapely.ops import unary_union
import matplotlib.pyplot as plt

class PolygonHelper:

    @staticmethod
    def extract_poly_coords(geom):
        if geom.type == 'Polygon':
            exterior_coords = geom.exterior.coords[:]
            interior_coords = []
            for interior in geom.interiors:
                interior_coords += interior.coords[:]
        elif geom.type == 'MultiPolygon':
            exterior_coords = []
            interior_coords = []
            for part in geom:
                epc = PolygonHelper.extract_poly_coords(part)  # Recursive call
                exterior_coords += epc['exterior_coords']
                interior_coords += epc['interior_coords']
        else:
            raise ValueError('Unhandled geometry type: ' + repr(geom.type))
        return {'exterior_coords': exterior_coords,
                'interior_coords': interior_coords}

    @staticmethod
    def extract_poly_interior_and_exterior_polygon(geom):
        if geom.type == 'Polygon':
            exterior_polygon = Polygon([[p[0], p[1]] for p in geom.exterior.coords[:]])
            interior_polygon = []
            for interior in geom.interiors:
                polygon = Polygon([[p[0], p[1]] for p in interior.coords[:]])
                interior_polygon.append(polygon)
        elif geom.type == 'MultiPolygon':
            exterior_polygon = []
            interior_polygon = []

            for part in geom:
                epc = PolygonHelper.extract_poly_interior_and_exterior_polygon(part)  # Recursive call
                exterior_polygon += epc['exterior_polygon']
                interior_polygon += epc['interior_polygon']
        else:
            raise ValueError('Unhandled geometry type: ' + repr(geom.type))
        return {'exterior_polygon': exterior_polygon,
                'interior_polygon': interior_polygon}

    @staticmethod
    def get_all_polygon_as_list(geom):
        result = []
        if geom.type == 'Polygon':
            result = geom
        elif geom.type == 'MultiPolygon':
            for part in geom:
                result.append(geom)
        else:
            raise ValueError('Unhandled geometry type: ' + repr(geom.type))
        return result


    # def interior_and_exterior_area_of_intersection(self, include_u_turn=True):
    #     intersection_polygon = self.intersection_polygon
    #     road_polygon = intersection_polygon.road_polygon.copy()


    #     connection_road = intersection_polygon.internal_connection_roads
    #     if include_u_turn is False:
    #         connection_road = intersection_polygon.connection_roads_without_u_turn
        
    #     # print('road polygon connection road ', road_polygon, connection_road)
    #     road_polygons = []
    #     area = []
    #     i = 0
    #     for road in connection_road:
    #         polygon = road_polygon[road.id]
    #         # print('road id, area ', road.id, polygon.area)
    #         area.append(polygon.area)
    #         road_polygons.append(polygon)
            
    #     area_arr = np.asarray(area)
    #     combined_polygon = unary_union(road_polygons)
    #     print('sum of road areas ',np.sum(area_arr))
    #     print('sum after unary union ', combined_polygon.area)
    #     # print('exterior length', combined_polygon.exterior.length)
    #     # print('interiors ', combined_polygon.interiors)

    #     # result = self.extract_poly_coords(combined_polygon)

    #     # interior_coords = result['interior_coords']
    #     # exterior_coords = result['exterior_coords']

    #     result_polygon = self.extract_poly_interior_and_exterior_polygon(combined_polygon)

    #     interior_polygon = result_polygon['interior_polygon']
    #     exterior_polygon = result_polygon['exterior_polygon']

    #     # print(result_polygon)
    #     # interior_polygon = Polygon([[p[0], p[1]] for p in interior_coords])
    #     # exterior_polygon = Polygon([[p[0], p[1]] for p in exterior_coords])

    #     for p in interior_polygon:
    #         # print('interior ', p)
    #         x, y = p.exterior.xy
    #         plt.plot(x, y, color='k')
    
    #     # for p in exterior_polygon:
    #     # print('exterior ', exterior_polygon)
    #     x, y = exterior_polygon.exterior.xy
    #     plt.plot(x, y, color='b')

    #     # # print(exterior_polygon, interior_polygon)
    #     # xe, ye = exterior_polygon.exterior.xy
    #     # xi, yi = interior_polygon.exterior.xy
    #     # plt.plot(xe, ye, color='k')
    #     # plt.plot(xi, yi, color='b')
    #     # for p in exterior_coords:
    #     #     print('exterior ', p)

    #     # plt.plot(interior_coords, color = 'g')
    #     # plt.plot((1,1), color = 'r')
    #     plt.show()

    #     return 0
