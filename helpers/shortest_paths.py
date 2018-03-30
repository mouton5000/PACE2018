from helpers.heap_dict import heapdict
from collections import defaultdict


def dijkstra(g, source, weights, destinations=None):
    """Return all the shortest paths from the source."""

    bests = heapdict()
    dists = {}
    paths = {}
    bests[source] = 0
    paths[source] = []

    visited = set([])
    visiteddests = set([])

    while len(bests) != 0:
        u, d = bests.popitem()
        dists[u] = d
        visited.add(u)
        if destinations and u in destinations:
            visiteddests.add(u)
            if len(visiteddests) == len(destinations):
                return dists, paths

        for e in u.incident_edges:
            v = e.neighbor(u)
            if v in visited:
                continue
            if v not in bests or d + weights[e] < bests[v]:
                bests[v] = d + weights[e]
                paths[v] = paths[u] + [e]

    return dists, paths


def all_shp_between_sources(g, sources, weights):
    dists = {}
    paths = {}
    dests = set(sources)
    for x in sources:
        dests.remove(x)
        distsx, pathsx = dijkstra(g, x, weights, destinations=dests)
        dists[x] = {y: distsx[y] for y in dests}
        paths[x] = {y: pathsx[y] for y in dests}
    return dists, paths


class Voronoi:
    def __init__(self, g, sources, weights):

        self.g = g
        self.sources = set(sources)
        self.weights = weights

        # Closest source of each node
        self.closest_sources = {}

        # For each source, list the nodes that are at the limit of the voronoi region centered on that source.
        # For each such node v, list the edges (v, w) such that w is in another region.
        self.limits = defaultdict(lambda: defaultdict(set))

        # Distance from each source to its voronoi region nodes
        self.dists = defaultdict(dict)

        # Shortest path from each source to its voronoi region nodes
        self.paths = {}

        self.__radiuses = {}

    def reinit(self):
        n = len(self.g)

        # Heap of closest nodes of each source
        bests = {}
        current_bests = heapdict()
        for x in self.sources:
            h = heapdict()
            h[x] = 0
            bests[x] = h
            current_bests[x] = (0, x.index)

        for x in self.sources:
            self.paths[x] = {x: []}

        while len(self.closest_sources) != n:
            x, _ = current_bests.popitem()
            h = bests[x]
            u, d = h.popitem()

            if u in self.closest_sources:
                if len(h) != 0:
                    _, d2 = h.peekitem()
                    current_bests[x] = (d2, x.index)
                continue

            self.dists[x][u] = d
            self.closest_sources[u] = x

            for e in u.incident_edges:
                v = e.neighbor(u)
                try:
                    y = self.closest_sources[v]
                    if x != y:
                        self.limits[x][u].add(e)
                        self.limits[y][v].add(e)
                    continue
                except KeyError:
                    pass
                if v not in h or d + self.weights[e] < h[v]:
                    h[v] = d + self.weights[e]
                    self.paths[x][v] = self.paths[x][u] + [e]

            if len(h) != 0:
                _, d2 = h.peekitem()
                current_bests[x] = (d2, x.index)

        self.__radiuses.update({source: self.__radius(source) for source in self.sources})

    @property
    def sum_radius(self):
        return sum(self.__radiuses.values())

    def __radius(self, source):
        return min(self.dists[source][x] + min(self.weights[e] for e in edges) / 2 for x, edges in self.limits[source].items())

    def add_sources(self, new_sources):
        allvisited = set()

        self.sources |= set(new_sources)

        # Heap of closest nodes of each source
        bests = {}
        current_bests = heapdict()
        for x in new_sources:
            h = heapdict()
            h[x] = 0
            bests[x] = h
            current_bests[x] = (0, x.index)

        for x in new_sources:
            self.paths[x] = {x: []}

        limits_edge_candidates = []

        check_radius = set()

        while len(current_bests) > 0:
            x, _ = current_bests.popitem()
            h = bests[x]
            u, d = h.popitem()

            # u was already visited by a new source
            if u in allvisited:
                if len(h) != 0:
                    _, d2 = h.peekitem()
                    current_bests[x] = (d2, x.index)
                continue

            allvisited.add(u)

            y = self.closest_sources[u]

            if y != x:
                del self.dists[y][u]
                del self.paths[y][u]
                try:
                    del self.limits[y][u]
                except KeyError:
                    pass
            self.dists[x][u] = d
            self.closest_sources[u] = x

            for e in u.incident_edges:
                v = e.neighbor(u)
                if v in allvisited:
                    y = self.closest_sources[v]
                    if x != y:
                        self.limits[x][u].add(e)
                        self.limits[y][v].add(e)
                        check_radius.add(x)
                        check_radius.add(y)
                    continue
                if v not in h:
                    dv = d + self.weights[e]
                    y = self.closest_sources[v]
                    if self.dists[y][v] < dv or self.dists[y][v] == dv and y.index < x.index:
                        # Except if there is an other path from x to v that is shorter that dists[y][v]
                        # then u and v are at the limits of the regions of x and y
                        # in that case, when the while loop ends, x and y remains respectively the closest sources of u
                        # and v
                        limits_edge_candidates.append((x, y, u, v, e))
                    else:
                        # dv is striclty better than the distance from y to v or dv equals that distance and x.index is
                        # lower than y.index
                        h[v] = dv
                        self.paths[x][v] = self.paths[x][u] + [e]
                    continue
                if d + self.weights[e] < h[v]:
                    h[v] = d + self.weights[e]
                    self.paths[x][v] = self.paths[x][u] + [e]

            if len(h) != 0:
                _, d2 = h.peekitem()
                current_bests[x] = (d2, x.index)

        for x, y, u, v, e in limits_edge_candidates:
            if x == self.closest_sources[u] and y == self.closest_sources[v]:
                self.limits[x][u].add(e)
                self.limits[y][v].add(e)
                check_radius.add(x)
                check_radius.add(y)

        self.__radiuses.update({source: self.__radius(source) for source in check_radius})

    def remove_source(self, rem_sources):
        """Update the voronoi regions of a graph where a set of sources is removed."""

        self.sources -= set(rem_sources)

        neighbor_sources = set([])

        # Heap of closest nodes of each source
        bests = defaultdict(lambda: heapdict())
        current_bests = heapdict()

        for y in rem_sources:
            del self.dists[y]
            del self.paths[y]
            del self.__radiuses[y]
            for v, edges in self.limits[y].items():
                for e in edges:
                    u = e.neighbor(v)
                    try:
                        x = self.closest_sources[u]
                        if x in rem_sources:
                            continue

                        neighbor_sources.add(x)

                        h = bests[x]
                        d = self.dists[x][u]
                        h[u] = d

                        # Reinit u to start the iteration from u
                        # remove u from the closest sources list
                        # remove u from the limit region of x
                        # and remove every incident edge of u from the limit regions of the neighbors of x
                        # (except e, this is done after the for loop by removing y from the keys of the dict limits)
                        for ep in self.limits[x][u]:
                            if ep == e:
                                continue
                            w = ep.neighbor(u)
                            try:
                                z = self.closest_sources[w]
                                self.limits[z][w].remove(ep)
                            except KeyError:
                                pass
                        del self.closest_sources[u]
                        del self.limits[x][u]

                    except KeyError:
                        pass

            del self.limits[y]

        for x in neighbor_sources:
            _, d2 = bests[x].peekitem()
            current_bests[x] = (d2, x.index)

        while len(current_bests) > 0:
            x, _ = current_bests.popitem()
            h = bests[x]
            u, d = h.popitem()

            try:
                if self.closest_sources[u] in neighbor_sources:
                    if len(h) != 0:
                        _, d2 = h.peekitem()
                        current_bests[x] = (d2, x.index)
                    continue
            except KeyError:
                pass

            self.dists[x][u] = d
            self.closest_sources[u] = x

            for e in u.incident_edges:
                v = e.neighbor(u)
                try:
                    y = self.closest_sources[v]
                    if y not in rem_sources:
                        if x != y:
                            self.limits[x][u].add(e)
                            self.limits[y][v].add(e)
                        continue
                except KeyError:
                    pass
                if v not in h or d + self.weights[e] < h[v]:
                    h[v] = d + self.weights[e]
                    self.paths[x][v] = self.paths[x][u] + [e]

            if len(h) != 0:
                _, d2 = h.peekitem()
                current_bests[x] = (d2, x.index)

        self.__radiuses.update({source: self.__radius(source) for source in neighbor_sources})

        return neighbor_sources
