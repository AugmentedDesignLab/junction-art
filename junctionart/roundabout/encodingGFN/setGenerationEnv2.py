import torch
from torch.nn.functional import one_hot
from junctionart.roundabout.encodingGFN.gflownet.env import Env
from junctionart.roundabout.encodingGFN.RoundaboutLaneEncodingEnv import RoundaboutLaneEncodingEnv
from tqdm import tqdm
from shapely.geometry import LinearRing, LineString, Point
import matplotlib.pyplot as plt

class SetGenerationEnv2(Env):
    # takes s (state) [bcz_size x size]
    # 0 means no number is assigned to that position. So initial state is torch.zeros(bcz_size, size)
    def __init__(self, size, number=4, roadDefinitions=None, base = 10000):
        self.size = size
        self.state_dim = size # no one-hot encoding, so size and state_dim are the same
        self.num_actions = size + 1 # [k added to left, k added to right, terminate action] k being one of the numbers
        self.number = number
        self.roadDefinitions = roadDefinitions
        self.generatorEnv = RoundaboutLaneEncodingEnv()
        config = torch.zeros(size).long().tolist()
        self.base = base
        self.generatorEnv.generateWithRoadDefinition(roadDefinitions,outgoingLanesMerge=False,nSegments=number,laneToCircularId=config, createOdr=True)
        self.circularPoints, self.roadEndPoints = self.generatorEnv.getCircularPointsAndRoadEndPoints(roadDefinitions, number)
        self.circle = LinearRing([(point[0], point[1]) for point in self.circularPoints])
        # print("Circular Points", self.circularPoints)
        # print("End points", self.roadEndPoints)
        self.encodingToReward = {} # maps string literal of lists to its reward
        
    def update(self, s, actions):
        s[torch.arange(0, len(s)), actions] += 1
        return s.float()
    
    def mask(self, s):
        mask = torch.ones(len(s), self.num_actions)

        mask[torch.where(s >= self.number)] = 0
        return mask
        
    def reward(self, s, showProgress=False):
        s = self.getStateForm(s)
        R0 = torch.zeros(len(s))
        for i in tqdm(range(len(s)), disable=not showProgress):
            config = (s[i] - 1).long().tolist()
            # self.generatorEnv.generateWithRoadDefinition(
            #         roadDefinition=self.roadDefinitions,
            #         outgoingLanesMerge=False,
            #         nSegments=self.number,
            #         laneToCircularId=config
            # )
            # R0[i] = self.generatorEnv.getRoundabout().getReward() + 1e-8
            R0[i] = self.getProxyReward(config, normalize=True)
            self.encodingToReward[str(s[i].long().tolist())] = R0[i].clone().item() 
            R0[i] = self.base**R0[i] 
           
        
        return R0.float() 
    
    def getProxyReward(self, config, normalize=False):
        # first reward no intersection with circle
        reward = 0
        denom = 0
        for i, slotNumber in enumerate(config):
            #draw a line
            line = LineString([self.roadEndPoints[i], self.circularPoints[slotNumber]])
            denom += 0.5
            #if line does not intersect w circle, add .5 to the reward
            if type(line.intersection(self.circle)) == Point:
                reward += 0.5

        # now do pairwise line intersection (proxy reward, so it is not entirely representitive of real life lanes)
        for i in range(len(config)):
            for j in range(i + 1, len(config)):
                line1 = LineString([self.roadEndPoints[i], self.circularPoints[config[i]]])
                line2 = LineString([self.roadEndPoints[j], self.circularPoints[config[j]]])
                if not line1.intersects(line2):
                    reward += 0.5
                denom += 0.5
   
        return reward / denom if normalize else reward
    
    def proxyRewardView(self, config):
        # show what proxy reward function sees
        plt.gca().set_aspect('equal')
        plt.plot(*self.circle.xy)
        for i, slot in enumerate(config):
            line = LineString([self.circularPoints[slot - 1], self.roadEndPoints[i]])
            plt.plot(*line.xy)
    def getStateForm(self, s):
        return s