# Handles the automated signal placement.
# Takes the road object as parameter and instantiates the signal object with the correct attributes. 
from pyodrx.signals import Signals, Signal
import extensions


class SignalManager:
    def __init__(self):
        """When signalManager object is instantiated, it instantiates signals and signal objects for each road. 
        """
        self.roads = [] #list of road objects
        self.signalsList = [] #List of signals objects added using this class. Need it for object lifetime. 
    
        
    ## Call these functions after the adjust functions have been called for the Opendrive object

    #Finding the rightmost lane of a given road. Helps with the signal placement.
    def findRightMostlane(self, individualRoad):
        rightlanesList = individualRoad.lanes.lanesections[len(individualRoad.lanes.lanesections)-1].rightlanes
        rightMostLane = rightlanesList[len(rightlanesList)-1]
        return rightMostLane

    
    #Place a signal for the individual road. Called once for each road element.
    def addSignal(self, individualRoad):

        #call functions for calculations on the road element given. Then use that to populate the signal object parameters.

        #get existing road attributes as is. 
        road_dict = individualRoad.get_attributes()

        #call functions for calculations.
        rightMostLane = self.findRightMostlane(individualRoad)
        temp_signal = Signal(road_dict["length"], rightMostLane.a)  
        
        # instantiate signals object here because one road element -> one signals element. Add signal to signals. 
        temp_signals = Signals()
        temp_signals.signalList.append(temp_signal)
        self.signalsList.append(temp_signals)
        #make sure that successor is junction type
        #if (str(self.successor.element_type)=='junction'):
            #final_lanesection = self.lanes.lanesections[len(self.lanes.lanesections) - 1]

    #Iterate roads and add signals for each road. Also add signals element to the road element tree. 
    #def addAllSignals(self):
    #    for road in self.roads:
    #        self.addSignal(road)
        