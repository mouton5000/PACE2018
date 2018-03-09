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
        print(x)
        dests.remove(x)
        distsx, pathsx = dijkstra(g, x, weights, destinations=dests)
        dists[x] = {y: distsx[y] for y in dests}
        paths[x] = {y: pathsx[y] for y in dests}
    return dists, paths


def voronoi(g, sources, weights):
    """Compute voronoi regions by parallely compute a dijkstra from each source. """

    n = len(g)

    # Closest source of each node
    closest_sources = {}

    # Heap of closest nodes of each source
    bests = {}
    current_bests = heapdict()
    for x in sources:
        h = heapdict()
        h[x] = 0
        bests[x] = h
        current_bests[x] = 0

    # Distance from each source to its voronoi region nodes
    dists = defaultdict(dict)

    # Shortest path from each source to its voronoi region nodes
    paths = {}
    for x in sources:
        paths[x] = {x: []}

    while len(closest_sources) != n:
        x, _ = current_bests.popitem()
        h = bests[x]
        u, d = h.popitem()

        if u in closest_sources:
            if len(h) != 0:
                _, d2 = h.peekitem()
                current_bests[x] = d2
            continue

        dists[x][u] = d
        closest_sources[u] = x

        for e in u.incident_edges:
            v = e.neighbor(u)
            if v in closest_sources:
                continue
            if v not in h or d + weights[e] < h[v]:
                h[v] = d + weights[e]
                paths[x][v] = paths[x][u] + [e]

        if len(h) != 0:
            _, d2 = h.peekitem()
            current_bests[x] = d2
    print(len(closest_sources), len(g))
    return dists, paths, closest_sources


def incremental_voronoi(g, sources, weights, dists, paths, closest_sources, new_sources):
    """Update the voronoi regions of a graph where a set of new sources is added."""

    allvisited = set()

    # Heap of closest nodes of each source
    bests = {}
    current_bests = heapdict()
    for x in new_sources:
        h = heapdict()
        h[x] = 0
        bests[x] = h
        current_bests[x] = 0

    for x in new_sources:
        paths[x] = {x: []}

    while len(current_bests) > 0:
        x, _ = current_bests.popitem()
        h = bests[x]
        u, d = h.popitem()

        if u in allvisited:
            if len(h) != 0:
                _, d2 = h.peekitem()
                current_bests[x] = d2
            continue

        cs = closest_sources[u]
        dcs = dists[cs][u]

        if dcs <= d:
            if len(h) != 0:
                _, d2 = h.peekitem()
                current_bests[x] = d2
            continue

        del dists[cs][u]
        dists[x][u] = d
        closest_sources[u] = x
        allvisited.add(u)

        for e in u.incident_edges:
            v = e.neighbor(u)
            if v in allvisited:
                continue
            if v not in h or d + weights[e] < h[v]:
                h[v] = d + weights[e]
                paths[x][v] = paths[x][u] + [e]

        if len(h) != 0:
            _, d2 = h.peekitem()
            current_bests[x] = d2
    return dists, paths, closest_sources
