from junctions.SequentialJunctionBuilder import SequentialJunctionBuilder

class JunctionBuilderFromRoadDefinition(SequentialJunctionBuilder):
    
    def __init__(self, 
                 roadBuilder, 
                 straightRoadLen, 
                 minAngle, 
                 maxAngle, 
                 country, 
                 random_seed, 
                 minConnectionLength, 
                 maxConnectionLength, 
                 probMinAngle, 
                 probLongConnection, 
                 probRestrictedLane):

        super().__init__(roadBuilder=roadBuilder, 
                         straightRoadLen=straightRoadLen, 
                         minAngle=minAngle, 
                         maxAngle=maxAngle, 
                         country=country, 
                         random_seed=random_seed, 
                         minConnectionLength=minConnectionLength, 
                         maxConnectionLength=maxConnectionLength, 
                         probMinAngle=probMinAngle, 
                         probLongConnection=probLongConnection, 
                         probRestrictedLane=probRestrictedLane)

        self.name = 'JunctionBuilderFromRoadDefinition'
        

        