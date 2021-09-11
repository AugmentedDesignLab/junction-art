


from shapely.geometry import polygon
from shapely.geometry.polygon import Polygon
from shapely.ops import unary_union
from junctionart.draw.ParamPolyRoadPolygon import ParamPolyRoadPolygon
from junctionart.draw.StraightRoadPolygon import StraightRoadPolygon
from junctionart.draw.AreaGeometry import PolygonHelper


class IntersectionPolygon():
    def __init__(self, intersection, step) -> None:
        self.intersection = intersection

        self.incident_roads = intersection.incidentRoads
        self.internal_connection_roads = intersection.internalConnectionRoads
        self.connection_roads_without_u_turn = self.get_connection_roads_without_uturn()

        self.road_polygon = self.create_road_polygons(step) # key - road id , val - road polygon

        pass


    
    def create_road_polygons(self, step = 0.1):
        road_polygon = {}
        for road in self.incident_roads:
            straight_road_polygon = StraightRoadPolygon(road)
            polygon  = straight_road_polygon.build_polygon()
            road_polygon[road.id] = polygon

        for road in self.internal_connection_roads:
            # print('parampoly road id', road.id)
            parampoly_road_polygon = ParamPolyRoadPolygon(road)
            polygon  = parampoly_road_polygon.build_polygon(step=step)
            road_polygon[road.id] = polygon

        return road_polygon

    def get_road_polygons(self, include_u_turns = True):

        road_polygon_dict = {}
        if include_u_turns:
            return self.road_polygon
        else: 
            for road in self.incident_roads:
                polygon = self.road_polygon[road.id]
                road_polygon_dict[road.id] = polygon

            for road in self.connection_roads_without_u_turn:
                polygon = self.road_polygon[road.id]
                road_polygon_dict[road.id] = polygon
        
        return road_polygon_dict


    def get_road_overlap_polygons(self, include_u_turn = True):
        
        road_overlap_polygons = []

        internal_connection_roads = self.internal_connection_roads
        if include_u_turn is False:
            internal_connection_roads = self.connection_roads_without_u_turn

        for road1 in internal_connection_roads:
            road_polygon1 = self.road_polygon[road1.id]
            for road2 in internal_connection_roads:
                if road1.id != road2.id:
                    road_polygon2 = self.road_polygon[road2.id]
                    if road_polygon1.is_valid and road_polygon2.is_valid:
                        overlap_polygon = road_polygon1.intersection(road_polygon2)
                        if overlap_polygon.type == 'Polygon': 
                            if overlap_polygon.exterior.length > 0:
                                road_overlap_polygons.append(overlap_polygon)
                            else:
                                continue
                                # print('polygon length ', overlap_polygon.exterior.length)
                        elif overlap_polygon.type == 'MultiPolygon':
                            for polygon in overlap_polygon:
                                if polygon.exterior.length > 0:
                                    road_overlap_polygons.append(polygon)
                        else:
                            # print('intersection geometry is of type ', overlap_polygon.type)
                            continue
                else:
                    continue

        return road_overlap_polygons


    def get_intersection_area_polygon(self, include_u_turn = True):
        
        connection_road = self.internal_connection_roads
        if include_u_turn is False:
            connection_road = self.connection_roads_without_u_turn

        connection_road_polygons = []
        for road in connection_road:
            polygon = self.road_polygon[road.id]
            connection_road_polygons.append(polygon)

        # print('size of connetion polygons ', len(connection_road_polygons))
        result = unary_union([polygon if polygon.is_valid else polygon.buffer(0) for polygon in connection_road_polygons])
        if result.geom_type == 'MultiPolygon':
            multi_result = []
            for polygon in result:
                multi_result.append(polygon)
            return multi_result
        return [result]

    def get_connection_roads_without_uturn(self):
        internal_connection_road_without_uturn = []
        for road in self.internal_connection_roads:
            if road.isUturn():
                # print('u turn')
                continue
            else:
                internal_connection_road_without_uturn.append(road)
        return internal_connection_road_without_uturn



    def get_combined_road_overlap_polygon(self, include_u_turn = True):

        polygon_list = self.get_road_overlap_polygons(include_u_turn)
        combined_polygon = unary_union([polygon if polygon.is_valid else polygon.buffer(0) for polygon in polygon_list])

        return combined_polygon


    def get_intersection_area_value(self, include_u_turn = True):
        area_value = 0
        intersection_area_polygon = self.get_intersection_area_polygon(include_u_turn)
        for polygon in intersection_area_polygon:
            area_value += polygon.area
        # print('intersection_area polygon ', intersection_area_polygon.type)
        return area_value

    def get_combined_road_overlap_value(self, include_u_turn = True):
        
        area_value = 0
        combined_road_polygon = self.get_combined_road_overlap_polygon(include_u_turn)
        
        if combined_road_polygon.type == 'MultiPolygon':
            for polygon in combined_road_polygon:
                area_value += polygon.area
        
        if combined_road_polygon.type == 'Polygon':
            area_value = combined_road_polygon.area

        return area_value

    