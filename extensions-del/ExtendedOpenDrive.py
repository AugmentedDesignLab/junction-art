import pyodrx
import xml.etree.ElementTree as ET
from xml.etree.ElementTree import Element
from pyodrx.enumerations import ElementType, ContactPoint
from pyodrx.links import _Link, _Links, create_lane_links
import numpy as np
from itertools import combinations
import math
import logging
import extensions


class ExtendedOpenDrive(pyodrx.OpenDrive):
    
    def __init__(self, name, laneLinker = None):

        super().__init__(name)
        self.laneLinker = laneLinker
        self.name = 'ExtendedOpenDrive'

    def reset(self):
        """Reset only keeps road links, removes lane links, adjustments, adjusted geometries. Useful for editing and ODR
        """
        
        logging.debug(f"{self.name}: reset: refreshing odr road adjustments")
        # TODO create a method to readjust in Extended Open Drive.
        for road in self.roads.values():
            road.reset()
        pass

    def resetAndReadjust(self, byPredecessor = False):
        self.reset()
        if byPredecessor:
            self.adjust_roads_and_lanesByPredecessor()
        else:
            self.adjust_roads_and_lanes()

    def adjust(self, byPredecessor = False):
        if byPredecessor:
            self.adjust_roads_and_lanesByPredecessor()
        else:
            self.adjust_roads_and_lanes()

    def write_xml(self,filename=None,prettyprint = True):
        """ writeXml writes the open scenario xml file

        Parameters
        ----------
            filename (str): path and filename of the wanted xml file
                Default: name of the opendrive

            prettyprint (bool): pretty print or ugly print?
                Default: True

        """
        if filename == None:
            filename = self.name + '.xodr'
        pyodrx.printToFile(self.get_element(), filename, prettyprint)

        extensions.modify_xodr_for_roadrunner(filename)


    def get_element(self):
        """ returns the elementTree of the FileHeader

        """
        element = Element('OpenDRIVE')
        headerElement = self._header.get_element()
        element.append(headerElement)
        for r in self.roads:
            roadElement = self.roads[r].get_element()
            if roadElement is not None:
                element.append(roadElement)
    
        for j in self.junctions:
            element.append(j.get_element())

        return element

    def hasRoad(self, roadId):

        if str(roadId) in self.roads:
            return True
        return False

    
    def updateRoads(self, roads):
        for road in roads:
            if self.hasRoad(road.id) is False:
                self.add_road(road)
        pass
    

    def addFirstRoad(self, road):
        # if len(self.roads) != 0:
        #     raise Exception("ODR already has a first road")
        self.roads[str(road.id)] = road
        

    def addRoads(self, roads):
        for road in roads:
            if self.hasRoad(road.id) is False:
                self.add_road(road)
        pass


    def getSuccessorRoad(self, road):
        """[summary]

        Args:
            road ([type]): [description]

        Returns:
            [type]: successor road object.
        """
        if road.successor is None:
            return None
        return self.roads[str(road.successor.element_id)]


    def getPredecessorRoad(self, road):
        """[summary]

        Args:
            road ([type]): [description]

        Returns:
            [type]: predecessor road object.
        """
        if road.predecessor is None:
            return None
        return self.roads[str(road.predecessor.element_id)]

    
    def adjust_roads_and_lanesByPredecessor(self): 
        """ Adjust starting position of all geoemtries of all roads and try to link lanes in neightbouring roads 

            Parameters
            ----------

        """
        #adjust roads and their geometries 
        logging.debug(f"{self.name}: adjust_roads_and_lanesByPredecessor: start points starting")
        self.adjust_startpointsByPredecessor()

        # print("start points adjusted")

        results = list(combinations(self.roads, 2))

        for r in range(len(results)):
            # print('analizing roads', results[r][0], results[r][1] )
            
            # print(f"create_lane_links for roads {results[r][0]} and {results[r][1]} ")
            if self.laneLinker is not None:
                self.laneLinker.createLaneLinks(self.roads[results[r][0]],self.roads[results[r][1]]) 
            else:
                create_lane_links(self.roads[results[r][0]],self.roads[results[r][1]])  


    def adjust_startpointsByPredecessor(self): 
        """ Adjust starting position of all geoemtries of all roads

            roads must have predecessors and be in the order of predecessors in roads dictionary. 
            It assumes the predecessor will always be adjusted beforehand, and current road is an extended succesor with cp == start

            Parameters
            ----------

        """
        
        count_adjusted_roads = 0
        for roadIdStr in self.roads: # fine one case when this for loop is executed more than once.

            currRoad = self.roads[roadIdStr]
            # 1. Adjustment for the first road. It's always adjusted.
            if count_adjusted_roads == 0: 
                currRoad.planview.adjust_geometires() 
                count_adjusted_roads += 1
                continue

            if currRoad.hasPredecessor():
                predRoad = self.getPredecessorRoad(currRoad)
                curAsSuc = predRoad.getExtendedSuccessorByRoadId(currRoad.id)

                if curAsSuc is None:
                    raise Exception(f"current road {currRoad.id} is not an extended successor of its predecessor. Cannot adjust start point")

                if curAsSuc.cp != pyodrx.ContactPoint.start:
                    raise Exception(f"current road {currRoad.id}'s cp is not start. Cannot adjust start point")

                if self.getPredecessorRoad(currRoad).planViewAdjusted():
                    self.adjust_road_wrt_neightbour(roadIdStr, currRoad.predecessor.element_id, currRoad.predecessor.contact_point, 'predecessor')
                else:
                    raise Exception(f"road {currRoad.id}'s predecessor (#{currRoad.predecessor.element_id}) is not adjusted. Cannot adjust start points")
            else:
                raise Exception(f"road #{currRoad.id} has no predecessor. Cannot adjust start points")

        pass

    
    def adjust_startpoints(self): 
        """ Adjust starting position of all geoemtries of all roads

            Parameters
            ----------

        """
        
        count_adjusted_roads = 0

        maxIteration = len(self.roads) * 3
        iteration = 0


        while count_adjusted_roads < len(self.roads):

            iteration += 1
            if iteration > maxIteration:
                raise Exception(f"maximum iteration exceeded, there might be problem with road links")


            for roadIdStr in self.roads: # fine one case when this for loop is executed more than once.

                currRoad = self.roads[roadIdStr]
                # 1. Adjustment for the first road. It's always adjusted.
                if count_adjusted_roads == 0: 
                    currRoad.planview.adjust_geometires() 
                    count_adjusted_roads += 1
                    continue

                if currRoad.planview.adjusted is True: 
                    # count_adjusted_roads += 1 # don't run into an infinity loop.
                    continue                
                
                # the part may fail if there are 2 consecutive connection roads.
                # adjust wrt normal predecessor 
                if (self.canAdjust_wrt_nonConnectionPredecessor(currRoad)): 

                    self.adjust_road_wrt_neightbour(roadIdStr, currRoad.predecessor.element_id, currRoad.predecessor.contact_point, 'predecessor')
                    count_adjusted_roads +=1

                    count_adjusted_roads = self.tryAdjustSuccessorIfCurrentIsConnection(currRoad, count_adjusted_roads)
                    continue 

                # or adjust wrt normal successor 
                elif self.canAdjust_wrt_nonConnectionSuccessor(currRoad): 

                    self.adjust_road_wrt_neightbour(roadIdStr, currRoad.successor.element_id, currRoad.successor.contact_point, 'successor')
                    count_adjusted_roads +=1

                    count_adjusted_roads = self.tryAdjustPredecessorIfCurrentIsConnection(currRoad, count_adjusted_roads)
                    continue

                pass

            pass

        pass



    def canAdjust_wrt_nonConnectionPredecessor(self, road):
        return (road.hasPredecessor()
                and self.getPredecessorRoad(road).planViewAdjusted()
                and road.predecessor.element_type is not ElementType.junction)
                
    
    def canAdjust_wrt_nonConnectionSuccessor(self, road):
        return (road.hasSuccessor()
                and self.getSuccessorRoad(road).planViewAdjusted()
                and road.successor.element_type is not ElementType.junction)


    def tryAdjustSuccessorIfCurrentIsConnection(self, currRoad, count_adjusted_roads):

        if (currRoad.isConnection
            and currRoad.hasSuccessor()
            and self.getSuccessorRoad(currRoad).planViewNotAdjusted()):

            succ_id = currRoad.successor.element_id
            if currRoad.successor.contact_point == ContactPoint.start:   
                self.adjust_road_wrt_neightbour(succ_id, currRoad.id, ContactPoint.end, 'predecessor') # conceptually may be wrong.
            else: 
                self.adjust_road_wrt_neightbour(succ_id, currRoad.id, ContactPoint.end, 'successor') # conceptually may be wrong.
            count_adjusted_roads +=1

        return count_adjusted_roads

    
    def tryAdjustPredecessorIfCurrentIsConnection(self, currRoad, count_adjusted_roads):
        if (currRoad.isConnection
            and currRoad.hasPredecessor()
            and self.getPredecessorRoad(currRoad).planViewNotAdjusted()):
            
            pred_id = currRoad.predecessor.element_id
            if currRoad.predecessor.contact_point == ContactPoint.start:   
                self.adjust_road_wrt_neightbour(pred_id, currRoad.id, ContactPoint.start, 'predecessor')
            else: 
                self.adjust_road_wrt_neightbour(pred_id, currRoad.id, ContactPoint.start, 'successor')
            count_adjusted_roads +=1

        return count_adjusted_roads



    def adjust_road_wrt_neightbour(self, road_id, neightbour_id, contact_point, neightbour_type): 
        """ Adjust geometries of road[road_id] taking as a successor/predecessor the neightbouring road with id neightbour_id. 
            NB Passing the type of contact_point is necessary because we call this function also on roads connecting to 
            to a junction road (which means that the road itself do not know the contact point of the junction road it connects to)


            Parameters
            ----------
            road_id (int): id of the road we want to adjust 

            neightbour_id(int): id of the neightbour road we take as reference (we suppose the neightbour road is already adjusted)

            contact_point(ContactPoint): type of contact point with point of view of roads[road_id]. Contact point of the neighbour.
            
            neightbour_type(str): 'successor'/'predecessor' type of linking to the neightbouring road 


        """

        main_road = self.roads[str(road_id)]
        neighbourRoad = self.roads[str(neightbour_id)]

        if neightbour_type == 'predecessor':

            if contact_point == ContactPoint.start :    
                x,y,h = neighbourRoad.planview.get_start_point()
                h = h + np.pi #we are attached to the predecessor's start, so road[k] will start in its opposite direction 
            elif contact_point == ContactPoint.end:
                x,y,h = neighbourRoad.planview.get_end_point()
            else:
                raise Exception(f"predecessor contact point not defined for road {road_id}")
            
            # adjust reference line offset
            if main_road.predecessorOffset != 0:

                if main_road.isConnection is False:
                    raise Exception("Cannot shift reference line for non connection roads")

                # in local coordinate the reference line moves along v

                localShiftAmount = neighbourRoad.getBorderDistanceOfLane(main_road.predecessorOffset, contact_point)

                if contact_point == pyodrx.ContactPoint.start:
                    if main_road.predecessorOffset > 0: 
                        x += localShiftAmount * math.cos(h + np.pi/2) * -1
                        y += localShiftAmount * math.sin(h + np.pi/2) * -1
                    else:
                        x += localShiftAmount * math.cos(h + np.pi/2)
                        y += localShiftAmount * math.sin(h + np.pi/2) 
                else:
                    if main_road.predecessorOffset > 0: 
                        x += localShiftAmount * math.cos(h + np.pi/2) 
                        y += localShiftAmount * math.sin(h + np.pi/2) 
                    else:
                        x += localShiftAmount * math.cos(h + np.pi/2) * -1
                        y += localShiftAmount * math.sin(h + np.pi/2) * -1

                # raise Exception("predecessorOffset is not implemented yet")
            
            # check if the heading is predefined.
            if main_road.startHeading is not None:
                h = main_road.startHeading

            main_road.planview.set_start_point(x,y,h)
            main_road.planview.adjust_geometires()

        elif neightbour_type == 'successor':

            if contact_point == ContactPoint.start:    
                x,y,h = neighbourRoad.planview.get_start_point()
            elif contact_point == ContactPoint.end:
                x,y,h = neighbourRoad.planview.get_end_point()
            else:
                raise Exception(f"successor contact point not defined for road {road_id}")
            main_road.planview.set_start_point(x,y,h)
            main_road.planview.adjust_geometires(True)      


    def adjust_roads_and_lanes(self): 
        """ Adjust starting position of all geoemtries of all roads and try to link lanes in neightbouring roads 

            Parameters
            ----------

        """
        #adjust roads and their geometries 
        logging.debug(f"{self.name}: adjust_roads_and_lanes: start points starting")
        self.adjust_startpoints()

        # print("start points adjusted")

        results = list(combinations(self.roads, 2))

        for r in range(len(results)):
            # print('analizing roads', results[r][0], results[r][1] )
            
            # print(f"create_lane_links for roads {results[r][0]} and {results[r][1]} ")
            if self.laneLinker is not None:
                self.laneLinker.createLaneLinks(self.roads[results[r][0]],self.roads[results[r][1]]) 
            else:
                create_lane_links(self.roads[results[r][0]],self.roads[results[r][1]])  
                