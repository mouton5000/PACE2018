from dynamicgraphviz.graph.undirectedgraph import UndirectedGraph
import instances


def read_input():
    """Read the input and return the corresponding instance."""
    input()
    size = int(input().split()[-1])
    input()

    edges = []
    while True:
        line = input()
        if line == 'END':
            break
        _, u, v, w = line.split()
        edges.append((int(u), int(v), int(w)))

    input()
    input()
    terms = []
    while True:
        line = input()
        if line == 'END':
            break
        _, t = line.split()
        terms.append(int(t))

    return build_instance_from(size, edges, terms)


def build_instance_from(size, edges_int, terms_int):
    """Build an instance from the pretreated input"""
    g = UndirectedGraph()
    nodes = [g.add_node() for _ in range(size)]
    weights = {}

    for u, v, w in edges_int:
        e = g.add_edge(nodes[u - 1], nodes[v - 1])
        weights[e] = w

    terms = [nodes[x - 1] for x in terms_int]

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
