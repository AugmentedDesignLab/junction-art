import pyodrx
import xml.etree.ElementTree as ET
from extensions.ExtendedRoad import ExtendedRoad
from extensions.CountryCodes import CountryCodes
from junctions.LaneConfiguration import LaneConfiguration
from typing import List, Dict

class JunctionDef:

    def __init__(self, id, name="MyJunction", countryCode = CountryCodes.US) -> None:

        self.id = id
        self.countryCode = countryCode
        self.connections = []
        self.junctionName = "JunctionDef"
        self.name = "JunctionDef"
        self.junction = None
        pass


    def get_attributes(self):
        """ returns the attributes as a dict of the Road

        """
        retdict = {}
        if self.junctionName:
            retdict['name'] = self.junctionName
        retdict['id'] = str(self.id)
        return retdict

    def get_element(self):
        # element = ET.Element('junction', attrib=self.get_attributes())
        return self.junction.get_element()


    def addSingleLaneConnectionUS(self, incomingRoad: ExtendedRoad, connectionRoad: ExtendedRoad):

        # both roads have their link informations.
        # connectionRoad's predecessor offset says which border

        incomingLanes = LaneConfiguration.getIncomingLanesOnARoad(incomingRoad, incomingRoad.junctionCP, self.countryCode)
        outgoingLaneId = -1 # right lane
        incomingLaneId = incomingLanes[0].lane_id # when no offset, its the first lane

        if connectionRoad.predecessorOffset < 0:
            incomingLaneId = connectionRoad.predecessorOffset - 1
        elif connectionRoad.predecessorOffset > 0:
            incomingLaneId = connectionRoad.predecessorOffset + 1

        # incomingLaneId = 0
        # for lane in incomingLanes:
        #     if lane.lane_id == connectionRoad.predecessorOffset:
        #         incomingLaneId = 

        connection = pyodrx.Connection(incomingRoad.id, connectionRoad.id, pyodrx.ContactPoint.start)
        connection.add_lanelink(incomingLaneId, outgoingLaneId)

        # self.connections.append(connection)
        self.junction.add_connection(connection)

        pass


    def build(self, connectionRoads: List[ExtendedRoad]):

        self.connections = []
        self.junction = pyodrx.Junction(self.name, self.id)

        # set junction id

        # for incidentRoad in incidentRoads:
        #     incidentRoad.junctionId = self.id

        for connectionRoad in connectionRoads:
            # we need to create the incoming lane links.
            if self.countryCode == CountryCodes.US:
                if connectionRoad.isSingleLaneConnection:
                    # have a right lane.
                    # now we need the predecessor
                    predecessorRoad = list(connectionRoad.extendedPredecessors.values())[0].road
                    predecessorRoad.junctionId = self.id
                    self.addSingleLaneConnectionUS(predecessorRoad, connectionRoad)
                else:
                    raise Exception(f"{self.name}: build: only single lane is implemented")
            else:
                raise Exception(f"{self.name}: build: only US is implemented")
        
        return self.junction
