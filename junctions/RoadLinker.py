import pyodrx
import logging

class RoadLinker:


    def linkConsequtiveRoadsWithNoBranches(self, roads, linkLastToFirst=False, cp1 = pyodrx.ContactPoint.end, cpRest=pyodrx.ContactPoint.start):


        previousRoad = None
        previousFirst = True
        for road in roads:
            if previousRoad is not None:
                previousRoad.updateSuccessor(road.elementType, road.id, pyodrx.ContactPoint.start)

                if previousFirst:
                    road.updatePredecessor(previousRoad.elementType, previousRoad.id, cp1)
                elif previousRoad.isConnection:
                    road.updatePredecessor(previousRoad.elementType, previousRoad.id, pyodrx.ContactPoint.end)
                else:
                    road.updatePredecessor(previousRoad.elementType, previousRoad.id, cpRest)
                    previousFirst = False
            previousRoad = road
        
        if linkLastToFirst:
            roads[-1].updateSuccessor(roads[0].elementType, roads[0].id, cp1)


    def adjustLaneOffsetsForOdr(self, odr):

        for road in odr.roads.values():
            if road.hasLaneOffsets() is False:
                logging.error(F"The road object do not have extended lanes properties. Please, update your code.")
                return
                
            pred = odr.getPredecessorRoad(road)
            if pred is not None:
                self.adjustLaneOffsets(pred, road)


    def adjustLaneOffsets(self, pred, suc):
        suc.setFirstLaneOffset(pred.getLastLaneOffset())

