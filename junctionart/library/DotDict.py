from operator import getitem
from functools import reduce

class DotDict(dict):
    """dot.notation access to dictionary attributes"""
    __getattr__ = dict.get
    __setattr__ = dict.__setitem__
    __delattr__ = dict.__delitem__

    
    def dot_get(self, s):
        return reduce(getitem, s.split('.'), self)  