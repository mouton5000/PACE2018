from dynamicgraphviz.graph.undirectedgraph import UndirectedGraph
from dynamicgraphviz.exceptions.graph_errors import NodeError

from helpers.shortest_paths import voronoi
from helpers.spanning_trees import kruskal


def compute(instance):
    """Return the Melhorn et al 2-approx algorithm"""

    dists, paths, closest_sources = voronoi(instance.g, instance.terms, instance.weights)

    gc = UndirectedGraph()
    nodes = {x: gc.add_node() for x in instance.terms}
    nodesback = {v: x for x, v in nodes.items()}
    weights = {}
    pathslinks = {}

    for e in instance.g.edges:
        u, v = e.extremities
        xu = closest_sources[u]
        xv = closest_sources[v]

        if xu != xv:
            xuc = nodes[xu]
            xvc = nodes[xv]
            wc = dists[xu][u] + instance.weights[e] + dists[xv][v]
            try:
                ec = xuc.get_incident_edge(xvc)
                if weights[ec] > wc:
                    weights[ec] = wc
                    pathslinks[ec] = (u, v, e)
            except NodeError:
                ec = gc.add_edge(xuc, xvc)
                weights[ec] = wc
                pathslinks[ec] = (u, v, e)

    treec = kruskal(gc, weights)

    tree = set([])
    for ec in treec:
        vuc, vvc = ec.extremities
        xu = nodesback[vuc]
        xv = nodesback[vvc]
        u, v, e = pathslinks[ec]

        try:
            pathu = paths[xu][u]
            pathv = paths[xv][v]
        except KeyError:
            pathu = paths[xu][v]
            pathv = paths[xv][u]

        for f in pathu:
            tree.add(f)
        for f in pathv:
            tree.add(f)
        tree.add(e)

    return tree
