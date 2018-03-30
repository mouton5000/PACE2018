from collections import defaultdict
import random
import copy
from algos.melhorntwoapprox import MelhornTwoApprox
import parameters

ADD_PROBA = 0.5
REM_PROBA = 0.5


def compute(instance, tree):

    deg = defaultdict(int)
    for e in tree:
        u, v = e.extremities
        deg[u] += 1
        deg[v] += 1

    melhorn = MelhornTwoApprox(instance)

    key_vertices = [u for u in deg if deg[u] >= 3 and u not in instance.terms]
    key_vertices.sort(key=lambda v: v.index)  # to fix the order of the vertices, otherwise non determinism appear
    cost = sum(instance.weights[e] for e in tree)
    melhorn.add_sources(key_vertices)

    if parameters.DEBUG:
        import time
        starttime = time.time()

    it = 0
    while True:

        it += 1

        if parameters.DEBUG:
            if it % 100 == 0:
                print(it, it / (time.time() - starttime))

        if it > parameters.LOCAL_SEARCH_MAX_ITERATION:
            return

        # if parameters.DEBUG and parameters.timer_end():
        #     break
        r = random.random()

        if len(key_vertices) < len(instance.g) - len(instance.terms) and r < ADD_PROBA:
            v = random.choice([v for v in instance.g if v not in key_vertices and v not in instance.terms])
            key_vertices.append(v)
            melhorn.add_sources([v])
        elif len(key_vertices) > 0 and r < ADD_PROBA + REM_PROBA:
            v = random.choice(key_vertices)
            key_vertices.remove(v)
            melhorn.rem_sources([v])

        if melhorn.current_cost() < cost:
            yield melhorn.current_tree()
            cost = melhorn.current_cost()
            it = 0
        else:
            if len(key_vertices) < len(instance.g) - len(instance.terms) and r < ADD_PROBA:
                del key_vertices[-1]
                melhorn.rem_sources([v])
            elif len(key_vertices) > 0 and r < ADD_PROBA + REM_PROBA:
                key_vertices.append(v)
                melhorn.add_sources([v])
