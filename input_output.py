from dynamicgraphviz.graph.undirectedgraph import UndirectedGraph
import instances
import parameters

def read_input():
    """Read the input and return the corresponding instance."""
    input()
    size = int(input().split()[-1])
    nb_edges = int(input().split()[-1])

    g = UndirectedGraph()

    if parameters.DEBUG:
        print('Build nodes')

    nodes = [g.add_node() for _ in range(size)]

    if parameters.DEBUG:
        print('Build edges')
    edges = []
    weights = {}
    i = 0
    for i in range(nb_edges):
        if parameters.DEBUG:
            i += 1
            if i % 1000 == 0:
                print('Edge %d / %d' % (i, nb_edges))
        line = input()
        _, u, v, w = line.split()

        e = g.add_edge(nodes[int(u) - 1], nodes[int(v) - 1])
        weights[e] = int(w)

        edges.append((int(u), int(v), int(w)))

    input()
    input()
    input()
    nb_terms = int(input().split()[-1])
    terms = []
    for i in range(nb_terms):
        line = input()
        _, t = line.split()
        terms.append(nodes[int(t) - 1])

    return instances.SteinerInstance(g, terms, weights)


def print_value(instance, tree):
    print('VALUE', sum(instance.weights[e] for e in tree))


def print_tree(tree):
    for e in tree:
        u, v = e.extremities
        print(u.index, v.index)


def print_output(instance, tree):
    """ Print the solution tree of the given instance."""
    print_value(instance, tree)
    print_tree(tree)
