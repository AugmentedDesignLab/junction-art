import torch
import torch.nn as nn

from junctionart.roundabout.RewardUtil import RewardUtil

class LogFlow(nn.Module):
    def __init__(self, layers, nSlots):
        super().__init__()
        self.mlp = self.make_mlp(layers=layers)
        self.nSlots = nSlots

    def make_mlp(self, layers, act=nn.LeakyReLU(), tail=[]):
        """makes an MLP with no top layer activation"""
        return nn.Sequential(*(sum(
            [[nn.Linear(fro, to)] + ([act] if pair_id < len(layers)-2 else [])
            for pair_id, (fro, to) in enumerate(zip(layers, layers[1:]))], []) + tail))
    
    def forward(self, x):
        filter = RewardUtil.getAllowedActionsFilter(x, self.nLanes)
        x = self.mlp(x)
        return x.exp() * filter
    