from helpers.heap_dict import heapdict


def dijkstra(g, source, weights):
    """Return all the shortest paths from the source."""

    bests = heapdict()
    dists = {}
    paths = {}
    bests[source] = 0
    paths[source] = []

    visited = set([])

    while len(bests) != 0:
        u, d = bests.popitem()
        dists[u] = d
        visited.add(u)

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
    for x in sources:
        distsx, pathsx = dijkstra(g, x, weights)
        dists[x] = {y: distsx[y] for y in sources}
        paths[x] = {y: pathsx[y] for y in sources}
    return dists, paths
