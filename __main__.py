
import input_output
from algos import all, twoapprox, flac
import parameters
import signal


class SigtermException(Exception):
    pass


def signal_term_handler(signal, frame):
    raise SigtermException()


btree = None
best = None


def output_tree():
    if parameters.DEBUG:
        input_output.print_value(instance, btree)
    else:
        input_output.print_output(instance, btree)


signal.signal(signal.SIGTERM, signal_term_handler)


try:
    instance = input_output.read_input()

    if parameters.DEBUG:
        print('Instance lue, n = %d, m = %d, k = %d' % (len(instance.g), instance.g.nb_edges, len(instance.terms)))

    for algo in [all, twoapprox, flac]:
        tree, cost = instance.simplify(algo.compute(instance))

        if parameters.DEBUG:
            print(algo)
            input_output.print_value(instance, tree)

        if best is None or cost < best:
            btree = tree
            best = cost

    output_tree()

except SigtermException:
    output_tree()
