from dynamicgraphviz.graph.undirectedgraph import UndirectedGraph

from helpers.shortest_paths import all_shp_between_sources
from helpers.spanning_trees import kruskal


def compute(instance):
    """Return the Kou et al 2-approx algorithm"""
    dists, paths = all_shp_between_sources(instance.g, instance.terms, instance.weights)

    gc = UndirectedGraph()
    nodes = {x: gc.add_node() for x in instance.terms}
    nodesback = {v: x for x, v in nodes.items()}
    weights = {}

    for i, x1 in enumerate(instance.terms):
        v1 = nodes[x1]
        for x2 in instance.terms[i+1:]:
            v2 = nodes[x2]
            e = gc.add_edge(v1, v2)
            try:
                weights[e] = dists[x1][x2]
            except KeyError:
                weights[e] = dists[x2][x1]

    treec = kruskal(gc, weights)

    tree = set([])
    for ec in treec:
        v1, v2 = ec.extremities
        x1 = nodesback[v1]
        x2 = nodesback[v2]
        try:
            path = paths[x1][x2]
        except KeyError:
            path = paths[x2][x1]
        for e in path:
            tree.add(e)
    return tree
