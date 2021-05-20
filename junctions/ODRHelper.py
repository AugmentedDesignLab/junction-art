import pyodrx
from extensions.ExtendedOpenDrive import ExtendedOpenDrive
from junctions.LaneLinker import LaneLinker
from junctions.RoadLinker import RoadLinker
from extensions.ExtendedRoad import ExtendedRoad

from typing import Dict, List

class ODRHelper:


    @staticmethod
    def transform(odr: ExtendedOpenDrive, startX=0, startY=0, heading=0):
        if odr is None:
            raise Exception(f"No odr is given")
        odr.reset()
        roads = list(odr.roads.values())
        firstRoad = roads[0]
        # firstRoad.planview.set_start_point(x_start=startX,y_start=startY,h_start=heading)
        ODRHelper.transformRoad(firstRoad, startX, startY, heading)
        odr.adjust_roads_and_lanesByPredecessor()
        return odr

    # def get_element(self):
    # """ returns the elementTree of the FileHeader

    # """
    # element = ET.Element('OpenDRIVE')
    # element.append(self._header.get_element())
    # for r in self.roads:
    #     element.append(self.roads[r].get_element())

    # for j in self.junctions:
    #     element.append(j.get_element())

    # return element

    @staticmethod
    def transformRoad(road: ExtendedRoad, startX, startY, heading):
        road.planview.set_start_point(x_start=startX, y_start=startY, h_start=heading)


    @staticmethod
    def combine(odrList: List[ExtendedOpenDrive], name):

        """Does not readjust

        Returns:
            [type]: [description]
        """
          
        laneLinker = LaneLinker()
        roadLinker = RoadLinker()
        
        combinedOdr = ExtendedOpenDrive(name, laneLinker=laneLinker)

        for odr in odrList:
            roads = list(odr.roads.values())
            junctions = odr.junctions

            combinedOdr.addFirstRoad(roads[0])

            for r in roads:
                combinedOdr.add_road(r)
            
            for junction in junctions:
                combinedOdr.add_junction(junction)
        
        return combinedOdr

    
    @staticmethod
    def addAdjustedRoads(odr: ExtendedOpenDrive, roads: List[ExtendedRoad]):

        for road in roads:
            odr.add_road(road)

        pass

    
