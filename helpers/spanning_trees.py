from collections import defaultdict


def kruskal(g, weights):
    edges = [e for e in g.edges]
    edges.sort(key=lambda x: weights[x])

    comp = {v: [v] for v in g}

    tree = []

    for e in edges:
        u, v = e.extremities
        if v in comp[u]:
            continue  # remove cycles
        tree.append(e)
        cu = comp[u]
        cv = comp[v]
        merged = cu + cv
        for w in merged:
            comp[w] = merged

    return tree