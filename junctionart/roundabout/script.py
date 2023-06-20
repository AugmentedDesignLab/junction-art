import torch

from junctionart.roundabout.LogFlow import LogFlow
from junctionart.roundabout.RewardUtil import RewardUtil

# assume there are 5 slots, 3 lanes
layers = [15, 128, 256, 15]
nSlots = 5
# lgF = LogFlow(layers=layers, nSlots=nSlots)

laneToCircularIDs=[-1, 1, -1]
state = RewardUtil.encodeState(laneToCircularIDs, nSlots)
# newState = lgF.forward(state)
print(state)



