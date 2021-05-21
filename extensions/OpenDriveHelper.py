import numpy as np


class OpenDriveHelper():
    def __init__(self, odr):
        self.odr = odr
        self.name = 'OpenDriveHelper'
        
        
    def rotateOpenDrive(self, startX=0, startY=0, heading=np.pi/6):
        if self.odr is None:
            raise Exception(f"No odr is given")
        self.odr.reset()
        firstRoad = self.odr.roads['0']
        firstRoad.planview.set_start_point(x_start=startX,y_start=startY,h_start=heading)
        self.odr.adjust_roads_and_lanesByPredecessor()
        return self.odr 

    def getMinMaxRoadIDFromODR(self):
        minRoadID = 2**10
        maxRoadID = -2**10
        for road in self.odr.roads.values():
            minRoadID = min(minRoadID, road.id)
            maxRoadID = max(maxRoadID, road.id)
        return minRoadID, maxRoadID

    def printKeyAndRoadIDFromDictWithPredSucc(self, roadDict):
        print("\n")
        for roadKey, roadValue in roadDict.items():
            print("road ->", roadKey, roadValue.id)
            for predDictKey, predDictValue in roadValue.extendedPredecessors.items():
                print ("Pred ", predDictKey, predDictValue.road.id)
            for succDictKey, succDictValue in roadValue.extendedSuccessors.items():
                print ("Succ ", succDictKey, succDictValue.road.id)


    def copyPredecessors(self, realCopy, shallowCopy, oldKeyNewKeyDict):
        for key, predecessor in realCopy.extendedPredecessors.items():
            newRoadID = oldKeyNewKeyDict[str(key)]
            predecessor.road.id = newRoadID
            cp = predecessor.cp
            shallowCopy.addExtendedPredecessor(predecessor.road, 0, cp)
        return shallowCopy

    def copySuccessors(self, realCopy, shallowCopy, oldKeyNewKeyDict):
        for key, successor in realCopy.extendedSuccessors.items():
            newRoadID = oldKeyNewKeyDict[str(key)]
            successor.road.id = newRoadID
            cp = successor.cp
            shallowCopy.addExtendedSuccessor(successor.road, 0, cp)
        return shallowCopy
        
    def updateOpenDriveRoadIDStartFrom(self, startRoadID):
        # self.printKeyAndRoadIDFromDictWithPredSucc(self.odr.roads)
        oldRoadDict = self.odr.roads.copy()
        oldKeyNewKeyDict = self.createOldKeyNewKeyDict(startRoadID)
        self.modify_odrRoadDict(oldKeyNewKeyDict, oldRoadDict)
        self.odr.adjust_roads_and_lanesByPredecessor()
        # self.printKeyAndRoadIDFromDictWithPredSucc(self.odr.roads)
        return self.odr

    # modify original odr with the roads with new id 
    def modify_odrRoadDict(self, oldKeyNewKeyDict, oldRoadDict):
        self.odr.roads = {}
        self.odr.roads['-1'] = None # odr can not be empty otherwise it checks if the pred is already in the dictionary
        for oldKey, newKey in oldKeyNewKeyDict.items():
            oldRoad = oldRoadDict[oldKey]
            roadShallowCopy = oldRoad.shallowCopy()
            roadShallowCopy.id = newKey
            roadShallowCopy = self.copyPredecessors(oldRoad,
                                                    roadShallowCopy, 
                                                    oldKeyNewKeyDict)

            roadShallowCopy = self.copySuccessors(oldRoad,
                                                  roadShallowCopy, 
                                                  oldKeyNewKeyDict)

            self.odr.addRoads([roadShallowCopy])
        del self.odr.roads['-1'] # deleting the dummy

    def createOldKeyNewKeyDict(self, startRoadID):
        oldKeyNewKeyDict = {}
        for oldKey in self.odr.roads.keys():
            newKey = int(oldKey) + startRoadID
            oldKeyNewKeyDict[oldKey] = newKey
        return oldKeyNewKeyDict
    

    