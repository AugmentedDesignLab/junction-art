# main object dict road id, polygon
# incoming is a road 
# returns  
# road geometry is an abstract class 
# build polygon 
# center lane line
# left lane 
# right lane 

from abc import ABC, abstractmethod 


class RoadPolygon(ABC):
    def __init__(self, road) -> None:
        self.odr_road = road
        self.polygon = []
        # self.center_line = []
        super().__init__()
    
    @property
    def road_polygon(self):
        return self.polygon


    @abstractmethod
    def build_polygon(self):
        pass

    

class ParampolyRoadPolygon(RoadPolygon):
    def __init__(self, road) -> None:
        super().__init__(road)

    def build_polygon(self):
        print('parampoly polygon building', self.odr_road)
        self.polygon = 'parampoly road polygon'
        return 

class StraightRoadPolygon(RoadPolygon):
    def __init__(self, road) -> None:
        super().__init__(road)

    def build_polygon(self):
        print('straight road buiding', self.odr_road)
        self.polygon = 'straight road polygon'
        return 


roads = []

roads.append(ParampolyRoadPolygon('roadID 1'))
roads.append(StraightRoadPolygon('roadID 2'))
roads.append(StraightRoadPolygon('roadID 3'))

for road in roads:
    road.build_polygon()
    print('polygon ', road.road_polygon)


