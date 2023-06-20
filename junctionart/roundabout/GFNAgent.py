import torch
from junctionart.roundabout.LogFlow import LogFlow
from tqdm import tqdm
class GFNAgent():
    def __init__(self, generatorEnv, layers, nSlots, nLanes, roadDefinitions, epsilon=0.1):
        self.generatorEnv = generatorEnv
        self.layers = layers
        self.nSlots = nSlots
        self.lgF = LogFlow(layers=layers, nSlots=self.nSlots)
        self.nLanes = nLanes
        self.epsilon = epsilon
        self.roadDefinitions = roadDefinitions

    def train(self, epoch = 5000, updateFrequency = 5):
        opt = torch.optim.Adam(self.lgF.parameters(), lr=0.003)
        totalLoss = 0
        losses = []
        states = []
        for i in tqdm(range(epoch)):
            try:
                state, loss = self.generateTrajectoryAndGetLoss()
            except RuntimeError:
                # print(f"cought RuntimeError at {i}th iteration")
                continue
        
            states.append(state)
            totalLoss += loss
            if i % updateFrequency == 0:
                opt.zero_grad()
                totalLoss.backward()
                opt.step()
                losses.append(totalLoss.item())
                totalLoss = 0

        return states, losses

    def generateTrajectoryAndGetLoss(self):
        state = torch.zeros(self.nLanes * self.nSlots)
        # print("new traj")
        for actionId in range(self.nLanes):
            newState = self.getNewStateFromFlow(state) # that's the s'

            # print("at ", self.getConfigFromEncoding(newState))
 
            try:
                totalBackwardFlow = self.getTotalBackwardFlow(newState) # that's the left part
            except ValueError:
                print("value error")
                continue
            totalForwardFlow = self.getTotalForwardFlow(newState) # that's the right part
            loss = (totalBackwardFlow - totalForwardFlow).pow(2)
            # print(f"actionId: {actionId}, forwardflow:{totalForwardFlow}, backwardflow:{totalBackwardFlow} loss: {loss}")
            state = newState
        return state, loss
   



    def getState(self, state, action):
        newState = state.clone()
        newState[action] = 1
        try:
            self.getConfigFromEncoding(newState)
        except ValueError:
            print("state: ", state)
            print("action: ", action)
            print("newState: ", newState)
            raise
        return newState
    
    def getNewStateFromFlow(self, state):
        flows = self.lgF.forward(state)
   
        action = torch.multinomial(flows, 1)
        try:
            newState = self.getState(state, action)
        except ValueError:
            print("flows: ", flows)
            raise
        return newState
    
    def getTotalForwardFlow(self, state):
        """
            finding the log (sum explogF(s', a') + eps + r(s')) for all a' in A(s'), here `state` is s'
        """
        flows = self.lgF.forward(state)
        return torch.log(flows.sum() + self.epsilon + self.reward(state))
    
    def getTotalBackwardFlow(self, state):
        """
            finding the log( sum explog(s, a) + eps) for (s, a) that leads to s'
        """

        parents, actions = self.getParentsAndActions(state)
        parentStates = [self.encodeState(parent) for parent in parents]
        flows = torch.stack([self.lgF.forward(parentState) for parentState in parentStates])
        backFlows = flows[torch.arange(len(parentStates)), actions] # get the flows of the action to s'
        return torch.log(backFlows.sum() + self.epsilon)


    def reward(self, state):
        """
            if terminal state, get reward, other wise return 0
        """
        if state.sum() == self.nLanes:
            config = self.getConfigFromEncoding(state)
        
            self.generatorEnv.generateWithRoadDefinition(self.roadDefinitions,
                outgoingLanesMerge=False,
                nSegments=self.nSlots,
                laneToCircularId=config
                )
            
            reward = self.generatorEnv.getRoundabout().getReward()
            # if reward > 0:
            #     print(f"reward got for config {config}")
            return reward

        return 0
    
    def getConfigFromEncoding(self, state):
        laneToSlotConfig = []
        for i in range(0, len(state), self.nSlots):
            _ = state[i:i+self.nSlots]
            try:
                laneToSlotConfig.append(int((_ == 1).nonzero(as_tuple=True)[0]) if len(_[_==1]) > 0 else -1)
            except ValueError:
                print(f"state: {state}")
                raise
        return laneToSlotConfig
    
    def getParentsAndActions(self, state):
        parents = []
        actions = []
        actions = (state == 1).nonzero(as_tuple=True)[0].tolist()
        config = self.getConfigFromEncoding(state)
        for i, action in enumerate(config):
            if action == -1:
                continue
            _ = config.copy()
            _[i] = -1
            parents.append(_)
        return parents, actions
    

    def encodeState(self, laneToSlotConfig):
        encode = torch.zeros(len(laneToSlotConfig) * self.nSlots)
        for i, laneToCircularID in enumerate(laneToSlotConfig):
            if laneToCircularID == -1:
                continue
            encode[i * self.nSlots + laneToCircularID] = 1
            
        return encode
    
    def generateTrajectory(self):
        state = torch.zeros(self.nLanes * self.nSlots)
        for actionId in range(self.nLanes):
            newState = self.getNewStateFromFlow(state)
            state = newState
        return self.getConfigFromEncoding(state)