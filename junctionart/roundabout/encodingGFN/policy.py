import torch
from torch import nn
from torch.nn.functional import relu, leaky_relu, one_hot
from torch.nn.functional import softmax

class ForwardPolicy(nn.Module):
    def __init__(self, state_dim, hidden_dim, num_actions):
        super().__init__()
        self.num_actions = num_actions
        self.dense1 = nn.Linear(state_dim, hidden_dim)
        self.dense2 = nn.Linear(hidden_dim, num_actions)
    
    def forward(self, s_):
        s = s_.clone()
        s /= ((self.num_actions-1)/2)
        x = self.dense1(s)
        # if torch.isnan(x).any() or (x.sum(1).unsqueeze(1) == 0).any():
        #     print(f"probs from policy: {x}")
        #     print(f"s: {s}")
        x = leaky_relu(x)
        x = self.dense2(x)
        return softmax(x, dim=1)
    
class BackwardPolicy:
    def __init__(self, state_dim, num_actions):
        super().__init__()
        self.num_actions = num_actions
        self.size = state_dim # no one-hot encoding, so size and state_dim are the same
    
    
    def __call__(self, s):
        # find the left most and right most non-zero elements in each row
        
        left_values = s[:, 0]
        right_values = s[torch.arange(len(s)), (s == 0).long().argmax(dim = 1) - 1]
     
        probs = torch.zeros(len(s), self.num_actions)
        probs[torch.arange(len(s)), left_values.long() - 1] = 0.5
        probs[torch.arange(len(s)), (right_values - 1 + (self.num_actions - 1 )/ 2).long()] = 0.5
     
        return probs

