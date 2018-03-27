import dynamicgraphviz
from collections import defaultdict
import parameters


class SteinerInstance:
    def __init__(self, g, terms, weights):
        self.g = g
        self.terms = terms
        self.weights = weights

    def check(self, t):
        return all(x in t.nodes for x in self.terms) and sum(1 if tu.is_root() else 0 for tu in t.nodes.values()) == 1
