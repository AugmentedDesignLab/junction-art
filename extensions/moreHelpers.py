import xml.etree.ElementTree as ET
import xml.dom.minidom as mini


import os
import sys
import csv
import math
import matplotlib.pyplot as plt

def view_road(opendrive,esminipath = 'esmini'):
    """ write a scenario and runs it in esminis OpenDriveViewer with some random traffic
        Parameters
        ----------
            opendrive (OpenDrive): the pyodrx road to run

            esminipath (str): the path to esmini 
                Default: pyoscx

        

    """
    _scenariopath = os.path.join(esminipath,'resources','xodr')
    opendrive.write_xml(os.path.join(_scenariopath,'pythonroad.xodr'),True)

    xodrPath =  os.path.join(esminipath,'resources','xodr','pythonroad.xodr')
    viewRoadFromFile(xodrPath, esminipath)

    pass



def viewRoadFromFile(xodrPath, esminipath = 'esmini'):


    print(f"plotting xord: {xodrPath}")

    if os.name == 'posix':
        ordPlotPath = os.path.join(esminipath,'bin','odrplot')
    elif os.name == 'nt':
        ordPlotPath = os.path.join(esminipath,'bin','odrplot.exe')

    os.system(f"{ordPlotPath} {xodrPath}")
    
    print("opening matplot lib")
    plotRoadFromCSV('track.csv')
    os.remove('track.csv')

    pass


def plotRoadFromCSV(csvFile):
    

    with open(csvFile, 'r') as f:
        reader = csv.reader(f, skipinitialspace=True)
        positions = list(reader)

    ref_x = []
    ref_y = []
    ref_z = []
    ref_h = []

    lane_x = []
    lane_y = []
    lane_z = []
    lane_h = []

    ref = False
    for pos in positions:
        if pos[0] == 'lane':
            if pos[3] == '0':
                ref = True
                ref_x.append([])
                ref_y.append([])
                ref_z.append([])
                ref_h.append([])
            else:
                ref = False
                lane_x.append([])
                lane_y.append([])
                lane_z.append([])
                lane_h.append([])
        else:
            if ref:
                ref_x[-1].append(float(pos[0]))
                ref_y[-1].append(float(pos[1]))
                ref_z[-1].append(float(pos[2]))
                ref_h[-1].append(float(pos[3]) + math.pi/2.0)
            else:
                lane_x[-1].append(float(pos[0]))
                lane_y[-1].append(float(pos[1]))
                lane_z[-1].append(float(pos[2]))
                lane_h[-1].append(float(pos[3]) + math.pi / 2.0)

    p1 = plt.figure(1, figsize=(16,8))
    for i in range(len(ref_x)):
        plt.plot(ref_x[i], ref_y[i], linewidth=2.0, color='#BB5555')
    for i in range(len(lane_x)):
        plt.plot(lane_x[i], lane_y[i], linewidth=1.0, color='#3333BB')

    # hdg_lines = []
    # for i in range(len(h)):
    #     for j in range(len(h[i])):
    #         hx = x[i][j] + H_SCALE * math.cos(h[i][j])
    #         hy = y[i][j] + H_SCALE * math.sin(h[i][j])
    #         plt.plot([x[i][j], hx], [y[i][j], hy])


    p1.gca().set_aspect('equal', adjustable='box')

    plt.show()


# def createConnection16(connectionRoads, id, roads):
    """ create_junction creates the junction struct for a set of roads

        This function violates the open drive 1.6 rule: Each connecting road shall be represented by exactly one <connection> element. A connecting road may contain as many lanes as required.


        Parameters
        ----------
            junction_roads (list of Road): all connecting roads in the junction

            id (int): the id of the junction
            
            roads (list of Road): all incomming roads to the junction

        Returns
        -------
            junction (Junction): the junction struct ready to use

    """
    # junc = Junction('my junction',id)
    
    # for connectionRoad in connectionRoads:

    #     conne1 = Connection(connectionRoad.successor.element_id, connectionRoad.id, ContactPoint.end) 
    #     _, sign, _ =  _get_related_lanesection(roads[connectionRoad.successor.element_id], connectionRoad ) 
    #     n_lanes = len(connectionRoad.lanes.lanesections[-1].leftlanes) 
    #     for i in range(1, n_lanes+1, 1):
    #         conne1.add_lanelink( 1*i, 1*sign*i)
    #         conne1.add_lanelink(-1*i,-1*sign*i)
    #         junc.add_connection(conne1)

    #     conne2 = Connection(connectionRoad.predecessor.element_id, connectionRoad.id, ContactPoint.start)
    #     _, sign, _ =  _get_related_lanesection(roads[connectionRoad.predecessor.element_id], connectionRoad) 
    #     n_lanes = len(connectionRoad.lanes.lanesections[0].leftlanes) 
    #     for i in range(1, n_lanes+1, 1):
    #         conne2.add_lanelink( 1*i, 1*sign*i)
    #         conne2.add_lanelink(-1*i,-1*sign*i)
    #         junc.add_connection(conne2)

 

    # return junc


def getConnectionRoads(roads, junction):
    """ Finds connection roads which exists in the junction only

    Args:
        roads (dictionary): key - id, value - road object
        junction ([type]): [description]
    """

    # print(roads)
    connectionRoads = []
    for connection in junction.connections:
        connectionRoadId = connection.connecting_road
        # print(f"getConnectionRoads connectionRoadId: {connectionRoadId}")
        connectionRoads.append(getRoadFromRoadDic(roads, connectionRoadId))
    
    return connectionRoads


def getRoadFromRoadDic(roads, roadId):
    return roads[str(roadId)]




