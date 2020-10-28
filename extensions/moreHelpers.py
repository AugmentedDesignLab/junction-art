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
