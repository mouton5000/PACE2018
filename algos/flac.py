import random
from helpers.heap_dict import heapdict
from collections import defaultdict


def compute(instance):

    #
    # "Global" parameters: those parameters are not reinitialized at each iteration
    #

    # The solution to be returned
    tree = set()

    # Copy of the required vertices of the instance. It let the algorithm
    # modify this set without modifiying the instance.
    required_vertices = set(instance.terms)

    # Set arbitrary root
    root = random.choice(instance.terms)
    required_vertices.remove(root)

    # Set of nodes reached by root in the current tree
    reached = {root}

    # For each node, this dict sorts its input arcs by cost.
    sorted_edges = {v: sorted(v.incident_edges, key=lambda e: instance.weights[e]) for v in instance.g}

    #
    # "Local" parameters: those parameters are reinitialized at each iteration
    #

    # Saturated edges (full of water)
    saturated = set()

    # For each node, this dict saves the sources this node is linked to with a path of saturated arcs
    sources = defaultdict(set)

    # For each node, this dict saves SOME OF the sources the ancestors of this node are linked to with a path of
    # saturated arcs. sources_of_ancestors may not contain all those sources. sources_of_ancestors[i] always include
    # sources[i]
    sources_of_ancestors = defaultdict(set)

    # Set of nodes for which one entering arc is saturating. The key of each node in the Fibonacci Heap is a triplet:
    # - the physical time when its next saturating arc will be saturated.
    # - a boolean : False if the input node is already reached by the tree, True otherwise
    # - an integer : the index of the output node of the edge
    # The key are compared using the natural python3 comparison of the triplets (float, boolean, integer)
    sorted_saturating = heapdict()

    #  For each node, this dict saves iterators pointing to the next saturated entering arc of this node.
    next_saturated_entering_arc_iterators = {}

    # For each node, this dict saves the next saturated entering arc of this node.
    next_saturated_entering_arc = {}

    # The actual "physical" time since the beginning of saturation
    time = 0

    def reinit():
        """Clear the maps, sets and lists used by the algorithm FLAC. Reinitialize the parameters used by FLAC."""
        saturated.clear()
        sources.clear()
        sources_of_ancestors.clear()
        sorted_saturating.clear()
        next_saturated_entering_arc_iterators.clear()
        next_saturated_entering_arc.clear()
        time = 0

        for v in required_vertices:
            # Define the sources feeding that terminal as the terminal itself
            sources[v].add(v)
            sources_of_ancestors[v].add(v)

            # define the next saturated arc entering v, and compute the time in seconds needed to saturate it.
            update_next_saturated_arc(v)

    def update_next_saturated_arc(v):
        pass

    def apply_flac():
        """a tree rooted in the root of the instance spanning a part of the terminals, and the set of those
        terminals."""
        pass

    while len(required_vertices) != 0:

        best_tree, reached_nodes, reached_terminals = apply_flac()

        # if best_tree is None:  # Should never happen except if the instance is not feasible
        #     return None

        # For each node reached by tree, add that node to the set reached. As a consequence, the next tree returned by
        # FLAC is preferentially merged by the current partial solution. In addition, this loop add the arc to the
        # current partial solution.

        tree |= best_tree
        reached |= reached_nodes
        required_vertices -= reached_terminals

    return tree
