import random


def compute(instance):

    # The solution to be returned
    tree = []

    # Copy of the required vertices of the instance. It let the algorithm
    # modify this set without modifiying the instance.
    terms_to_cover = set(instance.terms)

    # Set arbitrary root
    root = random.choice(instance.terms)
    terms_to_cover.remove(root)

    # Set of nodes reached by root in the current tree
    reached = {root}

    # For each node, this dict sorts its input arcs by cost.
    sorted_edges = {v: sorted(v.incident_edges, key=lambda e: instance.weights[e]) for v in instance.g}


    return tree
