from dynamicgraphviz.graph.undirectedgraph import UndirectedGraph
from dynamicgraphviz.exceptions.graph_errors import NodeError

from helpers.shortest_paths import voronoi
from helpers.spanning_trees import kruskal


def compute(instance):
    """Return the Melhorn et al 2-approx algorithm"""

    dists, paths, closest_sources, limits = voronoi(instance.g, instance.terms, instance.weights)

    gc = UndirectedGraph()
    nodes = {x: gc.add_node() for x in instance.terms}
    nodesback = {v: x for x, v in nodes.items()}
    weights = {}
    pathslinks = {}

    for x, limit_nodes in limits.items():
        xc = nodes[x]
        for u, edges in limit_nodes.items():
            for e in edges:
                v = e.neighbor(u)
                y = closest_sources[v]
                yc = nodes[y]

                wc = dists[x][u] + instance.weights[e] + dists[y][v]
                try:
                    ec = xc.get_incident_edge(yc)
                    if weights[ec] > wc:
                        weights[ec] = wc
                        pathslinks[ec] = (u, v, e)
                except NodeError:
                    ec = gc.add_edge(xc, yc)
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
