import random
from helpers.heap_dict import heapdict
from collections import defaultdict
from steiner.tree import Tree


def compute(instance):

    #
    # "Global" parameters: those parameters are not reinitialized at each iteration
    #

    # The solution to be returned
    tree = Tree(instance.g, instance.weights)

    # Associate the couples of nodes (u,v) and (v,u) to the edge {u,v}
    couple_to_edges = {}
    for e in instance.g.edges:
        u, v = e.extremities
        couple_to_edges[(u, v)] = e
        couple_to_edges[(v, u)] = e

    def get_weight(u,  v):
        """ Return the weight of the couple associated with the couple (u, v). """
        return instance.weights[couple_to_edges[(u, v)]]

    # Copy of the required vertices of the instance. It let the algorithm
    # modify this set without modifiying the instance.
    required_vertices = set(instance.terms)

    # Set arbitrary root
    root = random.choice(instance.terms)
    required_vertices.remove(root)

    # Set of nodes reached by root in the current tree
    reached = {root}

    # For each node, this dict sorts its input arcs by cost.
    sorted_input_arcs = defaultdict()
    def get_sorted_input_arcs(v):
        try:
            return sorted_input_arcs[v]
        except KeyError:
            def edge_to_arc(e):
                u, w = e.extremities
                if v == u:
                    return w, v
                else:
                    return u, v
            arcs = sorted_input_arcs[v] = list(map(edge_to_arc, sorted(v.incident_edges, key=lambda e: instance.weights[e])))
            return arcs

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
    next_saturated_entering_arcs = {}

    # The actual "physical" time since the beginning of saturation
    time = 0

    def update_next_saturated_arc(v):

        # print('Update', v, end=' ')

        # Iterator over the entering arcs of v sorted by weights
        try:
            it = next_saturated_entering_arc_iterators[v]
        except KeyError:
            it = next_saturated_entering_arc_iterators[v] = iter(get_sorted_input_arcs(v))
            # print(list(get_sorted_input_arcs(v)))

        # Last saturated arc entering v, may be None if the saturation in v just started
        b = next_saturated_entering_arcs.get(v, None)

        try:
            # If b was not the arc entering v with biggest cost, a exists
            # print('b:', b, 'v:', v, end=' ')
            next_saturated_entering_arcs[v] = a = next(it)
            # print('a:', a)
        except StopIteration:
            # Else, all arcs entering v are already saturated
            # print('No a available')
            del next_saturated_entering_arcs[v]
            del next_saturated_entering_arc_iterators[v]
            return

        # Compute saturated time of a
        if b is None:
            satTime = get_weight(*a) / len(sources[v])
        else:
            satTime = (get_weight(*a) - get_weight(*b)) / len(sources[v])
        sorted_saturating[v] = (time + satTime, a[0] not in reached, v.index)

    def reinit():
        nonlocal time
        """ Clear the maps, sets and lists used by the algorithm FLAC. Reinitialize the parameters used by FLAC. """
        saturated.clear()
        sources.clear()
        sources_of_ancestors.clear()
        sorted_saturating.clear()
        next_saturated_entering_arc_iterators.clear()
        next_saturated_entering_arcs.clear()
        time = 0

        for v in required_vertices:
            # Define the sources feeding that terminal as the terminal itself
            sources[v].add(v)
            sources_of_ancestors[v].add(v)

            # define the next saturated arc entering v, and compute the time in seconds needed to saturate it.
            update_next_saturated_arc(v)

    def next_saturated_arc():
        """ Return the next saturated time entering the first node if the fibonnacci heap. """
        nonlocal time
        v, k = sorted_saturating.popitem()
        time = k[0]
        return next_saturated_entering_arcs[v]

    def update_ancestor_sources(w, successors):
        """
        Update, for each node v which is a descendant of w in the list of successors, the set of sources
        an ancestor of v can reach with a path of saturated arcs :
        put all the sources an ancestor of w can reach into the vector of the successor v of w
        and then recursively do it with v and all the descendant until the successor of v is null.
        """
        srcs = sources_of_ancestors[w]

        toUpdate = successors.get(w, None)
        while toUpdate is not None:
            sources_of_ancestors[toUpdate] |= srcs
            srcs = sources_of_ancestors[toUpdate]
            toUpdate = successors.get(toUpdate, None)

    def find_conflict(u, v):
        """ Return true if the saturation of arc (u,v) implies a conflict. """
        # Will contain the list of nodes linked to u with a saturated path including u
        to_check = [u]

        # If one of those nodes is already linked to one of the sources linked to v there is a conflict.
        vsrcs = sources[v]

        # Contain, for each node w, the successor of w in in path of saturated arc from w to u, if such a path exists.
        successors = {}

        # print('>', u, v)

        while len(to_check) != 0:
            w = to_check.pop(0)
            # print('>>', w)
            # If the sources reaching w intersect the sources reaching v there is a conflict
            if not sources_of_ancestors[w].isdisjoint(vsrcs):
                update_ancestor_sources(w, successors)
                return True

            saturated_input_arc = next_saturated_entering_arcs.get(w, None)
            for u, _ in get_sorted_input_arcs(w):
                if saturated_input_arc is not None and u == saturated_input_arc[0]:
                    break
                if (u, w) in saturated:
                    to_check.append(u)
                    successors[w] = u

    def saturate_arc_and_update(u, v):
        # This list will contain the set of node for which the flow rate will change after the saturation of a
        to_update = [u]

        vsrcs = sources[v]

        # print('Start sat', u, v)

        while len(to_update) != 0:
            w = to_update.pop(0)
            # print('Check', w)

            # The current flow rate inside each entering arc of w, before a is saturated
            previous_volume_flow_rate = len(sources[w])
            sources[w] |= vsrcs  # disjoint union, because there is no conflict
            sources_of_ancestors[w] |= vsrcs

            if previous_volume_flow_rate != 0:
                # if w already received flow before a became saturated
                # the time the next entering arc of w is saturated is accelerated like this:
                try:
                    previous_sat_time, is_reached, index = sorted_saturating[w]
                    new_volume_flow_rate = previous_volume_flow_rate + len(vsrcs)
                    new_sat_time = time + (previous_sat_time - time) * previous_volume_flow_rate / new_volume_flow_rate
                    sorted_saturating[w] = (new_sat_time, is_reached, index)
                except KeyError:
                    # All arcs entering w are fully saturated
                    pass
            else:
                # if w did not receive any flow from the source, we initialize its saturation like this
                update_next_saturated_arc(w)

            # For each node linked to w with a saturated arc, we insert it in the list
            # of nodes we have to update

            saturating_input_arc = next_saturated_entering_arcs.get(w, None)
            for input_arc in get_sorted_input_arcs(w):
                if input_arc == saturating_input_arc:
                    break
                if input_arc in saturated:
                    to_update.append(input_arc[0])

        # print('Sat', (u, v))
        saturated.add((u, v))

    def build_tree(u):
        to_check = [u]
        tree = set()
        reached = set()
        leaves = set()

        while len(to_check) != 0:
            v = to_check.pop(0)
            reached.add(v)
            if v in required_vertices:
                leaves.add(v)

            for u, _ in get_sorted_input_arcs(v):
                # We search for the "ouptut arcs" of v, as each "input arc" is an edge, if (u, v) is in the graph,
                # (v, u) is too.
                if not (v, u) in saturated:
                    continue
                tree.add(couple_to_edges[(v, u)])
                to_check.append(u)
        return tree, reached, leaves

    def apply_flac():
        """a tree rooted in the root of the instance spanning a part of the terminals, and the set of those
        terminals."""
        reinit()
        while True:
            # Check which arc will be the next saturated one
            u, v = next_saturated_arc()
            # print(a, end=' ')

            # If the root is reached by the terminals, we can return a tree
            if u in reached:
                saturated.add((u, v))
                return build_tree(u)

            # We now check if a node is linked to the root with two paths of saturated arcs: it is called a conflict
            conflict = find_conflict(u, v)
            # print(conflict)

            # Whatever the case, we have to check which arc of v will be its next saturated entering arc, and when
            # it will be saturated
            update_next_saturated_arc(v)

            # If there is a conflict, we just ignore the arc saturation, as if it was never added to the arc
            if not conflict:
                # If there is no conflict, we have to update the flow rate of other arcs as a new arc is saturated.
                saturate_arc_and_update(u, v)

    while len(required_vertices) != 0:

        best_tree, reached_nodes, reached_terminals = apply_flac()

        # if best_tree is None:  # Should never happen except if the instance is not feasible
        #     return None

        # For each node reached by tree, add that node to the set reached. As a consequence, the next tree returned by
        # FLAC is preferentially merged by the current partial solution. In addition, this loop add the arc to the
        # current partial solution.

        for e in best_tree:
            tree.add_edge(e)
        reached |= reached_nodes
        required_vertices -= reached_terminals

    tree.simplify(instance.terms)
    return tree
