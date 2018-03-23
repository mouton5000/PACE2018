from dynamicgraphviz.graph.undirectedgraph import UndirectedGraph
from dynamicgraphviz.exceptions.graph_errors import NodeError

from helpers.shortest_paths import voronoi, incremental_voronoi, decremental_voronoi
from helpers.spanning_trees import kruskal
from steiner.tree import Tree
from helpers.heap_dict import heapdict

from helpers.sortedcontainers.sortedlist import SortedListWithKey


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
        self.nontree_edges = SortedListWithKey(key=lambda ec: self.weights[ec])

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

        self.treec = kruskal(self.gc, self.weights)
        edges = set(self.treec)
        for e in self.gc.edges:
            if e not in edges:
                self.nontree_edges.add(e)

    def compute(self):
        return self.current_tree()

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

    def _add_edge(self, ec):
        fc = self.treec.add_edge(ec)
        if fc is not None:
            self.nontree_edges.add(fc)
        if not self.treec.check_root():
            print('not check')
            import sys
            sys.exit(-1)

    def _decrease_edge_key(self, ec, wc, pathlink):
        if ec in self.nontree_edges:
            self.nontree_edges.remove(ec)
            self.weights[ec] = wc
            self.nontree_edges.add(ec)
        else:
            self.weights[ec] = wc
        self.pathslinks[ec] = pathlink

    def _remove_edges(self, rem_edges):
        for ec in rem_edges:
            try:
                self.nontree_edges.remove(ec)
            except ValueError:
                self.treec.remove_edge(ec)

        for ec in self.nontree_edges:
            self.treec.add_edge(ec, handle_conflict=False)
            if len(self.treec) == len(self.gc) - 1:
                break

    def add_sources(self, new_terms):
        incremental_voronoi(self.instance.g, self.sources, self.instance.weights,
                            self.dists, self.paths, self.closest_sources, self.limits, new_terms)

        print(new_terms)

        rem_edges = []
        for ec in self.gc.edges:
            vuc, vvc = ec.extremities
            xu = self.nodesback[vuc]
            xv = self.nodesback[vvc]
            u, v, e = self.pathslinks[ec]

            if self.closest_sources[u] != xu and self.closest_sources[u] != xv or \
               self.closest_sources[v] != xu and self.closest_sources[v] != xv:
                rem_edges.append(ec)
        print(rem_edges)

        self.sources |= set(new_terms)
        nodes = {x: self.gc.add_node() for x in new_terms}
        self.nodes.update(nodes)
        self.nodesback.update({v: x for x, v in nodes.items()})

        add_edges = []
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
                        add_edges.append(ec)

        for ec in add_edges:
            self._add_edge(ec)

        for ec in rem_edges:
            self.gc.remove_edge(ec)
        self._remove_edges(rem_edges)

    def rem_sources(self, rem_terms):
        decremental_voronoi(self.instance.g, self.sources, self.instance.weights,
                            self.dists, self.paths, self.closest_sources, self.limits, rem_terms)

        self.sources -= set(rem_terms)
        neighbors = set()
        rem_nodes = set()
        for x in rem_terms:
            xc = self.nodes.pop(x)
            neighbors |= set(xc.neighbors)
            del self.nodesback[xc]
            rem_nodes.add(xc)

        neighbors -= set(xc for xc in neighbors if xc not in self.gc)

        add_edges = set()
        decrease_key_edges = {}
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
                            if ec not in add_edges:
                                decrease_key_edges[ec] = (wc, (u, v, e))
                            else:
                                self.weights[ec] = wc
                                self.pathslinks[ec] = (u, v, e)
                    except NodeError:
                        ec = self.gc.add_edge(xc, yc)
                        self.weights[ec] = wc
                        self.pathslinks[ec] = (u, v, e)
                        add_edges.add(ec)

        for ec, val in decrease_key_edges.items():
            wc, pathlink = val
            self._decrease_edge_key(ec, wc, pathlink)
        for ec in add_edges:
            self._add_edge(ec)
        rem_edges = set()
        for xc in rem_nodes:
            rem_edges |= set(xc.incident_edges)
            self.gc.remove_node(xc)
        self._remove_edges(rem_edges)


def compute(instance):
    """Return the Melhorn et al 2-approx algorithm"""

    melhorn = MelhornTwoApprox(instance)
    return melhorn.compute()
