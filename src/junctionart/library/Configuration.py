import yaml
from .DotDict import DotDict


class Configuration:

    def __init__(self):
        self.load()
    
    pass


    def load(self):
        with open('./config.yaml', 'r') as stream:
            self.dic = DotDict(yaml.safe_load(stream))
            # print(self.dic)
            
    
    def get(self, key):
        
        return self.dic.dot_get(key)
        # raise KeyError(f"{key} not found in configuration")

        