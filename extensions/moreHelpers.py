import xml.etree.ElementTree as ET
import xml.dom.minidom as mini


import os


def view_road(opendrive,esminipath = 'esmini'):
    """ write a scenario and runs it in esminis OpenDriveViewer with some random traffic
        Parameters
        ----------
            opendrive (OpenDrive): the pyodrx road to run

            esminipath (str): the path to esmini 
                Default: pyoscx

        

    """
    _scenariopath = os.path.join(esminipath,'resources','xodr')
    print(_scenariopath)
    opendrive.write_xml(os.path.join(_scenariopath,'pythonroad.xodr'),True)

    xodrPath =  os.path.join(esminipath,'resources','xodr','pythonroad.xodr')
    visualiserPath =  os.path.join(esminipath,'EnvironmentSimulator', 'Applications', 'OdrPlot', 'xodr.py')

    
    if os.name == 'posix':
        ordPlotPath = os.path.join(esminipath,'bin','odrplot')
    elif os.name == 'nt':
        ordPlotPath = os.path.join(esminipath,'bin','odrplot.exe')
        
    os.system(f"{ordPlotPath} {xodrPath}")
    os.system(f"python {visualiserPath} track.csv")
    os.remove('track.csv')
