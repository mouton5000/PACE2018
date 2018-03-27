from collections import defaultdict
from steiner.tree import Tree


def kruskal(g, weights):
    edges = [e for e in g.edges]
    edges.sort(key=lambda x: weights[x])

    tree = Tree(g, weights)
    for e in edges:
        tree.add_edge(e, handle_conflict=False)
    return tree
