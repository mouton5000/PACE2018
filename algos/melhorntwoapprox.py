from dynamicgraphviz.graph.undirectedgraph import UndirectedGraph
from dynamicgraphviz.exceptions.graph_errors import NodeError

from helpers.shortest_paths import Voronoi
from helpers.spanning_trees import kruskal
from steiner.tree import Tree
import parameters

from helpers.sortedcontainers.sortedlist import SortedListWithKey


class MelhornTwoApprox:
    def __init__(self, instance):

        self.voronoi = Voronoi(instance.g, instance.terms, instance.weights)
        self.voronoi.reinit()

        self.instance = instance

        self.gc = UndirectedGraph()

        self.treec = None
        self.lower_treec = None

        self.nodes = {x: self.gc.add_node() for x in self.instance.terms}
        self.nodesback = {v: x for x, v in self.nodes.items()}
        self.pathslinks = {}
        self.weights = {}
        self.lower_weights = {}

        self.nontreec_edges = SortedListWithKey(key=lambda ec: self.weights[ec])
        self.non_lowertreec_edges = SortedListWithKey(key=lambda ec: self.lower_weights[ec])

        for x, limit_nodes in self.voronoi.limits.items():
            xc = self.nodes[x]
            for u, edges in limit_nodes.items():
                for e in edges:
                    v = e.neighbor(u)
                    y = self.voronoi.closest_sources[v]
                    yc = self.nodes[y]

                    wc = self.voronoi.dists[x][u] + self.instance.weights[e] + self.voronoi.dists[y][v]
                    lwc = min(self.voronoi.dists[x][u], self.voronoi.dists[y][v]) + self.instance.weights[e]
                    try:
                        ec = xc.get_incident_edge(yc)
                        if self.weights[ec] > wc:
                            self.weights[ec] = wc
                            self.pathslinks[ec] = (u, v, e)
                        if self.lower_weights[ec] > lwc:
                            self.lower_weights[ec] = lwc
                    except NodeError:
                        ec = self.gc.add_edge(xc, yc)
                        self.weights[ec] = wc
                        self.lower_weights[ec] = lwc
                        self.pathslinks[ec] = (u, v, e)

        self.treec = kruskal(self.gc, self.weights)
        edges = set(self.treec)

        self.lower_treec = kruskal(self.gc, self.lower_weights)
        lower_edges = set(self.lower_treec)

        for ec in self.gc.edges:
            if ec not in edges:
                self.nontreec_edges.add(ec)
            if ec not in lower_edges:
                self.non_lowertreec_edges.add(ec)

    def lower_bound(self):
        return self.lower_treec.cost

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
                pathu = self.voronoi.paths[xu][u]
                pathv = self.voronoi.paths[xv][v]
            except KeyError:
                pathu = self.voronoi.paths[xu][v]
                pathv = self.voronoi.paths[xv][u]

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
            self.nontreec_edges.add(fc)

        lfc = self.lower_treec.add_edge(ec)
        if lfc is not None:
            self.non_lowertreec_edges.add(lfc)

    def _decrease_edge_key(self, ec, wc, pathlink):
        if ec in self.nontreec_edges:
            self.nontreec_edges.remove(ec)
            self.weights[ec] = wc
            self.nontreec_edges.add(ec)
        else:
            self.weights[ec] = wc
        self.pathslinks[ec] = pathlink

    def _decrease_lower_edge_key(self, ec, lwc):
        if ec in self.non_lowertreec_edges:
            self.non_lowertreec_edges.remove(ec)
            self.lower_weights[ec] = lwc
            self.non_lowertreec_edges.add(ec)
        else:
            self.lower_weights[ec] = lwc

    def _remove_edges(self, rem_edges):
        for ec in rem_edges:
            try:
                self.nontreec_edges.remove(ec)
            except ValueError:
                self.treec.remove_edge(ec)
            del self.weights[ec]
            del self.pathslinks[ec]

            try:
                self.non_lowertreec_edges.remove(ec)
            except ValueError:
                self.lower_treec.remove_edge(ec)

        to_remove_from_non_tree = []
        for ec in self.nontreec_edges:
            remove_edge = self.treec.add_edge(ec, handle_conflict=False)
            if remove_edge is None:
                to_remove_from_non_tree.append(ec)
            if len(self.treec) == len(self.gc) - 1:
                break
        for ec in to_remove_from_non_tree:
            self.nontreec_edges.remove(ec)

        to_remove_from_non_lower_tree = []
        for ec in self.non_lowertreec_edges:
            remove_edge = self.lower_treec.add_edge(ec, handle_conflict=False)
            if remove_edge is None:
                to_remove_from_non_lower_tree.append(ec)
            if len(self.lower_treec) == len(self.gc) - 1:
                break
        for ec in to_remove_from_non_lower_tree:
            self.non_lowertreec_edges.remove(ec)

    def add_sources(self, new_terms):
        self.voronoi.add_sources(new_terms)

        rem_edges = []
        for ec in self.gc.edges:
            vuc, vvc = ec.extremities
            xu = self.nodesback[vuc]
            xv = self.nodesback[vvc]
            u, v, e = self.pathslinks[ec]

            if self.voronoi.closest_sources[u] != xu and self.voronoi.closest_sources[u] != xv or \
               self.voronoi.closest_sources[v] != xu and self.voronoi.closest_sources[v] != xv:
                rem_edges.append(ec)

        nodes = {x: self.gc.add_node() for x in new_terms}
        self.nodes.update(nodes)
        self.nodesback.update({v: x for x, v in nodes.items()})

        add_edges = []
        for x in new_terms:
            xc = self.nodes[x]
            limit_nodes = self.voronoi.limits[x]
            for u, edges in limit_nodes.items():
                for e in edges:
                    v = e.neighbor(u)
                    y = self.voronoi.closest_sources[v]
                    yc = self.nodes[y]
                    wc = self.voronoi.dists[x][u] + self.instance.weights[e] + self.voronoi.dists[y][v]
                    lwc = min(self.voronoi.dists[x][u], self.voronoi.dists[y][v]) + self.instance.weights[e]
                    try:
                        ec = xc.get_incident_edge(yc)
                        if self.weights[ec] > wc:
                            self.weights[ec] = wc
                            self.pathslinks[ec] = (u, v, e)
                        if self.lower_weights[ec] > lwc:
                            self.lower_weights[ec] = lwc
                    except NodeError:
                        ec = self.gc.add_edge(xc, yc)
                        self.weights[ec] = wc
                        self.lower_weights[ec] = lwc
                        self.pathslinks[ec] = (u, v, e)
                        add_edges.append(ec)

        for ec in add_edges:
            self._add_edge(ec)

        self._remove_edges(rem_edges)
        for ec in rem_edges:
            self.gc.remove_edge(ec)

    def rem_sources(self, rem_terms):

        neighbor_sources = self.voronoi.remove_source(rem_terms)

        self.voronoi.sources -= set(rem_terms)
        rem_nodes = set()
        for x in rem_terms:
            xc = self.nodes.pop(x)
            del self.nodesback[xc]
            rem_nodes.add(xc)

        add_edges = set()
        decrease_key_edges = {}
        decrease_key_lower_edges = {}
        for x in neighbor_sources:
            xc = self.nodes[x]
            limit_nodes = self.voronoi.limits[x]
            # print(xc, limit_nodes)
            for u, edges in limit_nodes.items():
                for e in edges:
                    v = e.neighbor(u)
                    y = self.voronoi.closest_sources[v]
                    if y not in neighbor_sources:
                        continue
                    yc = self.nodes[y]

                    wc = self.voronoi.dists[x][u] + self.instance.weights[e] + self.voronoi.dists[y][v]
                    lwc = min(self.voronoi.dists[x][u], self.voronoi.dists[y][v]) + self.instance.weights[e]
                    try:
                        ec = xc.get_incident_edge(yc)
                        if self.weights[ec] > wc:
                            if ec not in add_edges:
                                if ec not in decrease_key_edges or decrease_key_edges[ec][0] > wc:
                                    decrease_key_edges[ec] = (wc, (u, v, e))
                            else:
                                self.weights[ec] = wc
                                self.pathslinks[ec] = (u, v, e)
                        if self.lower_weights[ec] > lwc:
                            if ec not in add_edges:
                                if ec not in decrease_key_lower_edges or decrease_key_lower_edges[ec] > lwc:
                                    decrease_key_lower_edges[ec] = lwc
                            else:
                                self.lower_weights[ec] = lwc
                    except NodeError:
                        ec = self.gc.add_edge(xc, yc)
                        self.weights[ec] = wc
                        self.lower_weights[ec] = lwc
                        self.pathslinks[ec] = (u, v, e)
                        add_edges.add(ec)

        for ec, val in decrease_key_edges.items():
            wc, pathlink = val
            self._decrease_edge_key(ec, wc, pathlink)
        for ec, lwc in decrease_key_lower_edges.items():
            self._decrease_lower_edge_key(ec, lwc)
        for ec in add_edges:
            self._add_edge(ec)
        for xc in rem_nodes:
            self._remove_edges(set(xc.incident_edges))
            self.gc.remove_node(xc)



def compute(instance):
    """Return the Melhorn et al 2-approx algorithm"""

    melhorn = MelhornTwoApprox(instance)
    return melhorn.compute()
