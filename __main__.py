
import input_output
from algos import all, twoapprox, flac, melhorntwoapprox, localsearch
import parameters
import signal


class SignalException(Exception):
    pass


def signal_handler(signal, frame):
    raise SignalException()


btree = None
btreestr = None
best = None


def output_tree():
    if parameters.DEBUG:
        input_output.print_value(instance, btree)
    else:
        print(btreestr)


signal.signal(signal.SIGTERM, signal_handler)
signal.signal(signal.SIGINT, signal_handler)


try:
    instance = input_output.read_input()

    if parameters.DEBUG:
        print('Instance lue, n = %d, m = %d, k = %d' % (len(instance.g), instance.g.nb_edges, len(instance.terms)))

    for algo in [melhorntwoapprox, flac]:
        if parameters.DEBUG:
            print(algo)

        tree, cost = instance.simplify(algo.compute(instance))

        if parameters.DEBUG:
            input_output.print_value(instance, tree)

        if best is None or cost < best:
            btree = tree
            btreestr = input_output.get_output(instance, tree)
            best = cost

    for tree in localsearch.compute(instance, btree):
        btreestr = input_output.get_output(instance, tree)
        if parameters.DEBUG:
            btree = tree
            input_output.print_value(instance, btree)

    output_tree()

except SignalException:
    output_tree()
