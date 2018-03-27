
import steiner.input_output as input_output
from algos import all, twoapprox, flac, melhorntwoapprox, localsearch
import parameters
import signal
import sys


btree = None
btreestr = None
best = None


def output_tree():
    if parameters.DEBUG:
        input_output.print_value(btree)
    else:
        print(btreestr)


def signal_handler(signal, frame):
    output_tree()
    sys.exit(0)


signal.signal(signal.SIGTERM, signal_handler)
signal.signal(signal.SIGINT, signal_handler)

if parameters.DEBUG:
    import sys
    if len(sys.argv) > 1:
        with open(sys.argv[1], 'r') as f:
            instance = input_output.read_input_from_file(f)
    else:
        instance = input_output.read_input()
else:
    instance = input_output.read_input()

if parameters.DEBUG:
    print('Instance lue, n = %d, m = %d, k = %d' % (len(instance.g), instance.g.nb_edges, len(instance.terms)))

for algo in [melhorntwoapprox, flac]:
    if parameters.DEBUG:
        print(algo)

    tree = algo.compute(instance)
    if parameters.DEBUG:
        print('Tree is feasible:', instance.check(tree))

    if parameters.DEBUG:
        input_output.print_value(tree)

    if best is None or tree.cost < best:
        btree = tree
        btreestr = input_output.get_output(tree)
        best = tree.cost

if parameters.DEBUG:
    print(localsearch)

for tree in localsearch.compute(instance, btree):
    btreestr = input_output.get_output(tree)
    if parameters.DEBUG:
        btree = tree
        input_output.print_value(btree)

        with open('out.txt', 'w') as f:
            f.write(input_output.get_output(btree))

        if not instance.check(btree):
            print('not check')
            import sys
            sys.exit(-1)

output_tree()
