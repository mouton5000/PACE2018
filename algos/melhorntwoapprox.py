from dynamicgraphviz.graph.undirectedgraph import UndirectedGraph
from dynamicgraphviz.exceptions.graph_errors import NodeError

from helpers.shortest_paths import voronoi, incremental_voronoi, decremental_voronoi
from helpers.spanning_trees import kruskal
from steiner.tree import Tree


class MelhornTwoApprox:
    def __init__(self, instance):
        dists, paths, closest_sources, limits = voronoi(instance.g, instance.terms, instance.weights)
        self.instance = instance

        self.dists = dists
        self.paths = paths
        self.closest_sources = closest_sources
        self.limits = limits

        self.gc = UndirectedGraph()
        self.treec = None

        self.sources = set(self.instance.terms)

        self.nodes = {x: self.gc.add_node() for x in self.instance.terms}
        self.nodesback = {v: x for x, v in self.nodes.items()}
        self.weights = {}
        self.pathslinks = {}

        for x, limit_nodes in self.limits.items():
            xc = self.nodes[x]
            for u, edges in limit_nodes.items():
                for e in edges:
                    v = e.neighbor(u)
                    y = self.closest_sources[v]
                    yc = self.nodes[y]

                    wc = self.dists[x][u] + self.instance.weights[e] + self.dists[y][v]
                    try:
                        ec = xc.get_incident_edge(yc)
                        if self.weights[ec] > wc:
                            self.weights[ec] = wc
                            self.pathslinks[ec] = (u, v, e)
                    except NodeError:
                        ec = self.gc.add_edge(xc, yc)
                        self.weights[ec] = wc
                        self.pathslinks[ec] = (u, v, e)

    def compute(self):
        self.compute_spanning_tree()
        return self.current_tree()

    def compute_spanning_tree(self):
        self.treec = kruskal(self.gc, self.weights)

    def current_tree(self):

        tree = Tree(self.instance.g, self.instance.weights)
        for ec in self.treec:
            vuc, vvc = ec.extremities
            xu = self.nodesback[vuc]
            xv = self.nodesback[vvc]
            u, v, e = self.pathslinks[ec]

            try:
                pathu = self.paths[xu][u]
                pathv = self.paths[xv][v]
            except KeyError:
                pathu = self.paths[xu][v]
                pathv = self.paths[xv][u]

            for f in pathu:
                tree.add_edge(f)
            for f in pathv:
                tree.add_edge(f)
            tree.add_edge(e)

        tree.simplify(self.instance.terms)
        return tree

    def current_cost(self):
        return self.treec.cost

    def add_sources(self, new_terms):

        incremental_voronoi(self.instance.g, self.sources, self.instance.weights,
                            self.dists, self.paths, self.closest_sources, self.limits, new_terms)

        rem_edges = []
        for ec in self.gc.edges:
            vuc, vvc = ec.extremities
            xu = self.nodesback[vuc]
            xv = self.nodesback[vvc]
            u, v, e = self.pathslinks[ec]

            if self.closest_sources[u] != xu and self.closest_sources[u] != xv or \
               self.closest_sources[v] != xu and self.closest_sources[v] != xv:
                rem_edges.append(ec)

        for ec in rem_edges:
            self.gc.remove_edge(ec)

        self.sources |= set(new_terms)

        nodes = {x: self.gc.add_node() for x in new_terms}
        self.nodes.update(nodes)
        self.nodesback.update({v: x for x, v in nodes.items()})

        for x in new_terms:
            xc = self.nodes[x]
            limit_nodes = self.limits[x]
            for u, edges in limit_nodes.items():
                for e in edges:
                    v = e.neighbor(u)
                    y = self.closest_sources[v]
                    yc = self.nodes[y]
                    wc = self.dists[x][u] + self.instance.weights[e] + self.dists[y][v]
                    try:
                        ec = xc.get_incident_edge(yc)
                        if self.weights[ec] > wc:
                            self.weights[ec] = wc
                            self.pathslinks[ec] = (u, v, e)
                    except NodeError:
                        ec = self.gc.add_edge(xc, yc)
                        self.weights[ec] = wc
                        self.pathslinks[ec] = (u, v, e)

    def rem_sources(self, rem_terms):
        decremental_voronoi(self.instance.g, self.sources, self.instance.weights,
                            self.dists, self.paths, self.closest_sources, self.limits, rem_terms)

        self.sources -= set(rem_terms)
        neighbors = set()

        for x in rem_terms:
            xc = self.nodes.pop(x)
            neighbors |= set(xc.neighbors)
            del self.nodesback[xc]
            self.gc.remove_node(xc)

        neighbors -= set(xc for xc in neighbors if xc not in self.gc)

        for xc in neighbors:
            x = self.nodesback[xc]
            limit_nodes = self.limits[x]
            for u, edges in limit_nodes.items():
                for e in edges:
                    v = e.neighbor(u)
                    y = self.closest_sources[v]
                    yc = self.nodes[y]
                    if yc not in neighbors:
                        continue

                    wc = self.dists[x][u] + self.instance.weights[e] + self.dists[y][v]
                    try:
                        ec = xc.get_incident_edge(yc)
                        if self.weights[ec] > wc:
                            self.weights[ec] = wc
                            self.pathslinks[ec] = (u, v, e)
                    except NodeError:
                        ec = self.gc.add_edge(xc, yc)
                        self.weights[ec] = wc
                        self.pathslinks[ec] = (u, v, e)


def compute(instance):
    """Return the Melhorn et al 2-approx algorithm"""

    melhorn = MelhornTwoApprox(instance)
    return melhorn.compute()
