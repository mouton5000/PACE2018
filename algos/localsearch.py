from collections import defaultdict
import random
import copy
from algos import melhorntwoapprox

ADD_PROBA = 0.5
REM_PROBA = 0.5


def compute(instance, tree):

    deg = defaultdict(int)
    for e in tree:
        u, v = e.extremities
        deg[u] += 1
        deg[v] += 1

    key_vertices = [u for u in deg if deg[u] >= 3]
    cost = sum(instance.weights[e] for e in tree)
    instance.terms += key_vertices

    while True:
        r = random.random()

        if len(key_vertices) < len(instance.g) - len(instance.terms) and r < ADD_PROBA:
            v = random.choice([v for v in instance.g if v not in key_vertices])
            key_vertices.append(v)
            instance.terms.append(v)
        elif len(key_vertices) > 0 and r < ADD_PROBA + REM_PROBA:
            v = random.choice(key_vertices)
            key_vertices.remove(v)
            instance.terms.remove(v)

        tree2 = melhorntwoapprox.compute(instance)
        cost2 = sum(instance.weights[e] for e in tree2)

        if cost2 < cost:
            yield tree2
            cost = cost2
        else:
            if len(key_vertices) < len(instance.g) - len(instance.terms) and r < ADD_PROBA:
                del key_vertices[-1]
                del instance.terms[-1]
            elif len(key_vertices) > 0 and r < ADD_PROBA + REM_PROBA:
                key_vertices.append(v)
                instance.terms.append(v)
