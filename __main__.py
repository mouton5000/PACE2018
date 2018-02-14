
import input_output
from algos import all, twoapprox, flac
import parameters

instance = input_output.read_input()
algo = flac



if parameters.DEBUG:
    print('Instance lue, n = %d, m = %d, k = %d' % (len(instance.g), instance.g.nb_edges, len(instance.terms)))

tree = algo.compute(instance)
tree2 = instance.simplify(tree)

if parameters.DEBUG:
    if tree2 is None:
        print('Infeasible')
    else:
        input_output.print_value(instance, tree)
else:
    if tree2 is None:
        input_output.print_output(instance, tree) # Infeasible solution
    else:
        input_output.print_output(instance, tree2)