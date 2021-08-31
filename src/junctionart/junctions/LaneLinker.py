from junctionart.junctions.LaneConfiguration import LaneConfiguration
import pyodrx
import junctionart.junctions
import junctionart.extensions as extensions
from pyodrx.exceptions import NotSameAmountOfLanesError
import logging
from junctionart.extensions.ExtendedRoad import ExtendedRoad
from junctionart.junctions.RoadLinker import RoadLinker
from junctionart.extensions.CountryCodes import CountryCodes

class LaneLinker:

    def __init__(self, countryCode: CountryCodes):

        self.name = 'LaneLinker'
        self.countryCode = countryCode
        if countryCode != CountryCodes.US:
            raise Exception("LaneLinker does not support non-US yet.")

    def createLaneLinks(self, road1: ExtendedRoad, road2: ExtendedRoad, ignoreMismatch=False):
        """ create_lane_links takes to roads and if they are connected, match their lanes 
            and creates lane links. 
            NOTE: now only works for roads/connecting roads with the same amount of lanes

            Parameters
            ----------
                road1 (Road): first road to be lane linked

                road2 (Road): second road to be lane linked
        """
        if self.bothNormalRoads(road1, road2):
            #both are roads
            if self.areConsecutive(road1, road2): 
                self._create_links_roads(road1,road2)
            elif self.areConsecutive(road2, road1): 
                self._create_links_roads(road2,road1)

        elif road1.isSingleLaneConnection:
            self._createLinksForSingleLaneConnectionRoad(connecting=road1)

        elif road2.isSingleLaneConnection:
            self._createLinksForSingleLaneConnectionRoad(connecting=road2)

        elif road1.road_type != -1:
            self._create_links_connecting_road(road1,road2)

        elif road2.road_type != -1:
            self._create_links_connecting_road(road2,road1)

    def bothNormalRoads(self, road1, road2):
        return road1.road_type == -1 and road2.road_type == -1


    def areConsecutive(self, road1, road2): 
        """Disinformation. 

        Args:
            road1 ([type]): [description]
            road2 ([type]): [description]

        Returns:
            [type]: [description]
        """
        # return road1.isPredecessorOf(road2) and road2.isSuccessorOf(road1)
        return road1.isExtendedPredecessorOf(road2) and road2.isExtendedSuccessorOf(road1)

    

    def _createLinksForUturns(self, connecting: ExtendedRoad, road: ExtendedRoad):
        # we need to build successor only because incoming traffic is saved in junction def

        if self.countryCode != CountryCodes.US:
            raise Exception("_createLinksForUturns is only US")
        # return if not successor
        try:

            roadCP = RoadLinker.getSuccessorCP(connecting, road) # same link CP for both start and end of uturn

            ########## 1. Add successor lane links ##########
            # get the lane sections
            laneSectionForConnection = connecting.lanes.lanesections[-1] # end of connecting
            # At the end of the uturn, traffic is going from median right lane.
            connectionLanes = laneSectionForConnection.rightlanes

            outgoingLanes = LaneConfiguration.getOutgoingLanesOnARoad(road, roadCP, self.countryCode)


            # now the median right lane on the uturn is connected to all the outgoing road lanes.
            uTurnLane = connectionLanes[0]
            for outgoingLane in outgoingLanes:
                uTurnLane.add_link("successor", outgoingLane.lane_id)


            ######### 1. Add predecessor lane links ##############
            
            # get the lane sections
            laneSectionForConnection = connecting.lanes.lanesections[0] # end of connecting
            # At the end of the uturn, traffic is going from median right lane.
            connectionLanes = laneSectionForConnection.rightlanes

            incomingLanes = LaneConfiguration.getIncomingLanesOnARoad(road, roadCP, self.countryCode)

            # now the median right lane on the uturn is connected to all the outgoing road lanes.
            uTurnLane = connectionLanes[0]
            for incomingLane in incomingLanes:
                uTurnLane.add_link("predecessor", incomingLane.lane_id)
                break # only the first lane.

        except:
            return
        pass
    

    def _createLinksForSingleLaneConnectionRoad(self, connecting: ExtendedRoad):

        if self.countryCode != CountryCodes.US:
            raise Exception("_createLinksForUturns is only US")
        connecting.clearLaneLinks()
        # links at the end
        laneSectionForConnection = connecting.lanes.lanesections[0] # end of connecting
        # At the end of the uturn, traffic is going from median right lane.
        connectionLane = laneSectionForConnection.rightlanes[0]

        for link in connecting.predefinedLaneLinks: #('predecessor', incomingLaneId, connectionLaneId) ('successor', outgoingLaneId, connectionLaneId)
            if link[2] == connectionLane.lane_id:
                connectionLane.add_link(link[0], link[1])
            
        pass


        
    def _create_links_connecting_road(self, connecting: ExtendedRoad, road: ExtendedRoad, ignoreMismatch=True):
        """ _create_links_connecting_road will create lane links between a connecting road and a normal road

            Parameters
            ----------
                connecting (Road): a road of type connecting road (not -1)

                road (Road): a that connects to the connecting road

        """

        if connecting.isUturn():
            return self._createLinksForUturns(connecting=connecting, road=road)

        linktype, sign, connecting_lanesec =  self._get_related_lanesection(connecting,road)
        _, _, road_lanesection_id =  self._get_related_lanesection(road,connecting) 

        # invert lanes if contact points are the same
        try:
            roadCp, conCp = RoadLinker.getContactPoints(road, connecting)
        except:
            # lane linking not possible because they are not neighbours
            return
        
                
        if roadCp == conCp:
            logging.debug(f"{self.name}: switching lane sides for {connecting.id} and {road.id}")

        if connecting_lanesec != None:
            laneSectionForConnection = connecting.lanes.lanesections[connecting_lanesec]
            laneSectionForRoad = road.lanes.lanesections[road_lanesection_id]
            if laneSectionForConnection.leftlanes:
                # do left lanes
                connectionLanes = laneSectionForConnection.leftlanes
                roadLanes = laneSectionForRoad.leftlanes
                
                if roadCp == conCp:
                    roadLanes = laneSectionForRoad.rightlanes



                if len(connectionLanes) == len(roadLanes):
                    for i in range(len(roadLanes)):
                        linkid = roadLanes[i].lane_id
                        connectionLanes[i].add_link(linktype,linkid)
                elif ignoreMismatch:
                    # raise NotImplementedError()
                    # logging.warn(f"number of left lanes are not the same for {connecting.id} and {road.id}")
                    self.connectMinLanesOnOneSide(connectionLanes, roadLanes, linktype, None)

                else:
                    raise NotSameAmountOfLanesError('Connecting road ',connecting.id, ' and road ', road.id, 'do not have the same number of left lanes.')

            if laneSectionForConnection.rightlanes:
                # do right lanes
                connectionLanes = laneSectionForConnection.rightlanes
                roadLanes = laneSectionForRoad.rightlanes

                if roadCp == conCp:
                    roadLanes = laneSectionForRoad.leftlanes

                if len(connectionLanes) == len(roadLanes):
                    for i in range(len(roadLanes)):
                        linkid = roadLanes[i].lane_id
                        connectionLanes[i].add_link(linktype,linkid)
                elif ignoreMismatch:
                    # raise NotImplementedError()
                    # logging.warn(f"number of left lanes are not the same for {connecting.id} and {road.id}")
                    self.connectMinLanesOnOneSide(connectionLanes, roadLanes, linktype, None)
                else:
                    raise NotSameAmountOfLanesError('Connecting road ',connecting.id, ' and road ', road.id, 'do not have the same number of right lanes.')


    def _getRelatedLanesection(self, road:ExtendedRoad, connected_road: ExtendedRoad):
        """ _get_related_lanesection takes to roads, and gives the correct lane section to use
            the type of link and if the sign of lanes should be switched

            This function is very poorly written.

            Parameters
            ----------
                road (Road): the road that you want the information about

                connected_road (Road): the connected road

            Returns
            -------
                linktype (str): the linktype of road to connected road (successor or predecessor)

                sign (int): +1 or -1 depending on if the sign should change in the linking

                road_lanesection_id (int): what lanesection in the road that should be used to link
        """
        linktype = None
        sign = None
        road_lanesection_id = None

        if connected_road.isExtendedSuccessorOf(road):
            linktype = 'successor'
            successorCP = RoadLinker.getSuccessorCP(road, connected_road)
            if successorCP == pyodrx.ContactPoint.start:
                sign = 1
            else:
                sign = -1
            road_lanesection_id = -1

        elif connected_road.isExtendedPredecessorOf(road):
            linktype = 'predecessor'
            predecessorCP = RoadLinker.getPredecessorCP(road, connected_road)
            if predecessorCP == pyodrx.ContactPoint.start:
                sign = -1
            else:
                sign = 1
            road_lanesection_id = 0
            # TODO return here?

        if connected_road.road_type != -1:
            # treat connecting road in junction differently ? Why is it different?
            sign, road_lanesection_id = self.getRelatedLaneSectionGivenSecondIsAConnection(road, connected_road, road_lanesection_id, sign)
        return linktype, sign, road_lanesection_id

    def _get_related_lanesection(self, road, connected_road):
        """ _get_related_lanesection takes to roads, and gives the correct lane section to use
            the type of link and if the sign of lanes should be switched

            This function is very poorly written.

            Parameters
            ----------
                road (Road): the road that you want the information about

                connected_road (Road): the connected road

            Returns
            -------
                linktype (str): the linktype of road to connected road (successor or predecessor)

                sign (int): +1 or -1 depending on if the sign should change in the linking

                road_lanesection_id (int): what lanesection in the road that should be used to link
        """
        linktype = None
        sign = None
        road_lanesection_id = None
    
        if road.successor and road.successor.element_id == connected_road.id:
            linktype = 'successor'
            if road.successor.contact_point == pyodrx.ContactPoint.start:
                sign = 1
            else:
                sign = -1
            road_lanesection_id = -1

            # TODO return here?

        elif road.predecessor and road.predecessor.element_id == connected_road.id:
            linktype = 'predecessor'
            if road.predecessor.contact_point == pyodrx.ContactPoint.start:
                sign = -1
            else:
                sign = 1
            road_lanesection_id = 0
            # TODO return here?

        if connected_road.road_type != -1:
            # treat connecting road in junction differently ? Why is it different?
            sign, road_lanesection_id = self.getRelatedLaneSectionGivenSecondIsAConnection(road, connected_road, road_lanesection_id, sign)
        return linktype, sign, road_lanesection_id

    def getRelatedLaneSectionGivenSecondIsAConnection(self, road, connected_road, road_lanesection_id, sign):
        if connected_road.predecessor.element_id == road.id:
            if connected_road.predecessor.link_type == pyodrx.ContactPoint.start: # TODO wtf is link type here.
                road_lanesection_id = -1
                sign = -1
            else:
                road_lanesection_id = 0
                sign = 1
        elif connected_road.successor.element_id == road.id:
            if connected_road.predecessor.link_type == pyodrx.ContactPoint.start: # TODO wtf is link type here.
                road_lanesection_id = 0
                sign = 1
            else:
                road_lanesection_id = -1
                sign = -1
        return sign, road_lanesection_id

    
    def _create_links_roads(self, pre_road: ExtendedRoad, suc_road: ExtendedRoad, ignoreMismatch=True):
        """ _create_links_roads takes two roads and connect the lanes with links, if they have the same amount. 

            Parameters
            ----------
                pre_road (Road): the predecessor road 

                suc_road (Road): the successor road

        """
        # invert lanes if contact points are the same
        try:
            roadCp, conCp = RoadLinker.getContactPoints(pre_road, suc_road)
        except:
            # lane linking not possible because they are not neighbours
            return
        
                
        if roadCp == conCp:
            logging.debug(f"{self.name}: switching lane sides for {pre_road.id} and {suc_road.id}")


        # pre_linktype, pre_sign, pre_connecting_lanesec =  self._get_related_lanesection(pre_road,suc_road)
        # suc_linktype, suc_sign, suc_connecting_lanesec =  self._get_related_lanesection(suc_road,pre_road)
        pre_linktype, pre_sign, pre_connecting_lanesec =  self._getRelatedLanesection(pre_road,suc_road)
        suc_linktype, suc_sign, suc_connecting_lanesec =  self._getRelatedLanesection(suc_road,pre_road)
        preLaneSection = pre_road.lanes.lanesections[pre_connecting_lanesec]
        # TODO it may be wrong. shouldn't it be suc_connecting_lanesec
        # sucLaneSection = suc_road.lanes.lanesections[-1] 
        sucLaneSection = suc_road.lanes.lanesections[suc_connecting_lanesec] 


        # left
        preLanes = preLaneSection.leftlanes
        sucLanes = sucLaneSection.leftlanes
        if roadCp == conCp:
            sucLanes = sucLaneSection.rightlanes

        if len(preLanes) == len(sucLanes):
            for i in range(len(preLanes)):
                preLanes[i].add_link(pre_linktype, sucLanes[i].lane_id)
                sucLanes[i].add_link(suc_linktype, preLanes[i].lane_id)

        elif ignoreMismatch:
            
            # logging.warn(f"number of left lanes are not the same for {pre_road.id} and {suc_road.id}")
            self.connectMinLanesOnOneSide(preLanes, sucLanes, pre_linktype, suc_linktype)
            

        else:
            raise NotSameAmountOfLanesError('Road ' + str(pre_road.id) + ' and road ' + str(suc_road.id) + ' does not have the same number of right lanes.')

        #right
        preLanes = preLaneSection.rightlanes
        sucLanes = sucLaneSection.rightlanes
        if roadCp == conCp:
            sucLanes = sucLaneSection.leftlanes

        if len(preLanes) == len(sucLanes):
            for i in range(len(preLanes)):
                preLanes[i].add_link(pre_linktype, sucLanes[i].lane_id)
                sucLanes[i].add_link(suc_linktype, preLanes[i].lane_id)

        elif ignoreMismatch:

            # logging.warn(f"number of left lanes are not the same for {pre_road.id} and {suc_road.id}")
            
            self.connectMinLanesOnOneSide(preLanes, sucLanes, pre_linktype, suc_linktype)
            
        else:
            raise NotSameAmountOfLanesError('Road ' + str(pre_road.id) + ' and road ' + str(suc_road.id) + ' does not have the same number of right lanes.')


    def connectMinLanesOnOneSide(self,preLanes, sucLanes, pre_linktype, suc_linktype):
        """[summary]

        Args:
            preLanes ([type]): [description]
            sucLanes ([type]): [description]
            pre_linktype ([type]): [description]
            suc_linktype ([type]): None if prelanes are from connecting roads.
        """
        
        lensToConnect = len(preLanes)
        if len(preLanes) > len(sucLanes):
            lensToConnect = len(sucLanes)

        for i in range(lensToConnect):
            preLanes[i].add_link(pre_linktype, sucLanes[i].lane_id)
            if suc_linktype is not None:
                sucLanes[i].add_link(suc_linktype, preLanes[i].lane_id)


