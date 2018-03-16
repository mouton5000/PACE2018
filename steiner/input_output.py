from dynamicgraphviz.graph.undirectedgraph import UndirectedGraph
import steiner.instances as instances
import parameters


def read_input_from_file(f):
    """Read the input from file"""
    f.readline()
    size = int(f.readline().split()[-1])
    nb_edges = int(f.readline().split()[-1])

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
        line = f.readline()
        _, u, v, w = line.split()

        e = g.add_edge(nodes[int(u) - 1], nodes[int(v) - 1])
        weights[e] = int(w)

        edges.append((int(u), int(v), int(w)))

    line = f.readline()
    while 'Terminals' not in line:
        line = f.readline()
    if 'SECTION' in line:
        line = f.readline()
        while 'Terminals' not in line:
            line = f.readline()
    nb_terms = int(line.split()[-1])
    terms = []
    for i in range(nb_terms):
        line = f.readline()
        _, t = line.split()
        terms.append(nodes[int(t) - 1])

    return instances.SteinerInstance(g, terms, weights)


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

    line = input()
    while 'Terminals' not in line:
        line = input()
    if 'SECTION' in line:
        line = input()
        while 'Terminals' not in line:
            line = input()
    nb_terms = int(line.split()[-1])
    terms = []
    for i in range(nb_terms):
        line = input()
        _, t = line.split()
        terms.append(nodes[int(t) - 1])

    return instances.SteinerInstance(g, terms, weights)


def print_value(instance, tree):
    if tree is not None:
        print('VALUE', sum(instance.weights[e] for e in tree))


def print_tree(tree):
    if tree is None:
        print(None)
        return
    for e in tree:
        u, v = e.extremities
        print(u.index, v.index)


def print_output(instance, tree):
    """ Print the solution tree of the given instance."""
    print_value(instance, tree)
    print_tree(tree)


def get_value(instance, tree):
    if tree is not None:
        return 'VALUE %d\n' % sum(instance.weights[e] for e in tree)


def get_tree(tree):
    if tree is None:
        return str(None)

    def str_e(e):
        u, v = e.extremities
        return '%d %d' % (u.index, v.index)

    return '\n'.join(str_e(e) for e in tree)


def get_output(instance, tree):
    """ Return a string representing the solution"""
    return get_value(instance, tree) + get_tree(tree)
