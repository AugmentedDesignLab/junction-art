from roadgen.controlLine.ControlLineBasedGenerator import ControlLineBasedGenerator

class GraphBasedGenerator:

    def __init__(self, debug=True, randomizeDistance=False, nLaneDistributionOnASide=[0.2, 0.7, 0.1, 0]):
        self.generator = ControlLineBasedGenerator((400, 400), debug=debug, seed=3, randomizeDistance=randomizeDistance, nLaneDistributionOnASide=nLaneDistributionOnASide)

    
    def generate(self, graph):
        pass