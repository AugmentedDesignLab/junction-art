from typing import List

class Node:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        pass


class Edge:
    def __init__(self, u: Node, v: Node, d:float = 0):
        self.u = u
        self.v = v
        self.d = d
        pass


class Graph:
    def __init__(self, nodes:List[Node], edges:List[Edge]):
        self.nodes = nodes
        self.edges = edges
        pass

    
