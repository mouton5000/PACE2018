import dynamicgraphviz
from collections import defaultdict
import parameters


class SteinerInstance:
    def __init__(self, g, terms, weights):
        self.g = g
        self.terms = terms
        self.weights = weights

    def simplify(self, t):
        """Simplify the solution or return None if not all the terminals are connected. """

        # Build connected components of t
        # Remove cycles

        if parameters.DEBUG:
            print('Simplify step')

        newcost = 0
        remcost = 0

        comp = {v: i for i, v in enumerate(self.g)}
        degs = defaultdict(int)

        toremove = []

        for e in t:
            newcost += self.weights[e]
            u, v = e.extremities
            if comp[u] == comp[v]:
                toremove.append(e)  # remove cycles
                remcost += self.weights[e]
            else:
                cu = comp[u]
                cv = comp[v]
                degs[u] += 1
                degs[v] += 1
                for w in self.g:
                    if comp[w] == cv:
                        comp[w] = cu

        # Check if terminals are connected

        cx = comp[self.terms[0]]
        # for x in self.terms[1:]:
        #     if cx != comp[x]:
        #         return None

        # Remove edges closing cycles
        t = [e for e in t if e not in toremove]

        del toremove[:]

        # Remove edges not in the component of the terminals
        for e in t:
            u, v = e.extremities
            if comp[u] != cx:
                toremove.append(e)
                remcost += self.weights[e]
                degs[u] = 0
                degs[v] = 0

        t = [e for e in t if e not in toremove]
        del toremove[:]

        # Remove edges attached to non terminal leaves and iteratively restart until all leaves are terminals
        tocheck = [v for v in self.g if degs[v] == 1 and v not in self.terms]

        while tocheck:
            for e in t:
                u, v = e.extremities
                if u in tocheck:
                    toremove.append(e)
                    remcost += self.weights[e]
                    degs[v] -= 1
                    degs[u] -= 1
                elif v in tocheck:
                    toremove.append(e)
                    remcost += self.weights[e]
                    degs[u] -= 1
                    degs[v] -= 1

            del tocheck[:]
            t = [e for e in t if e not in toremove]
            del toremove[:]
            tocheck = [v for v in self.g if degs[v] == 1 and v not in self.terms]

        newcost -= remcost

        return t, newcost
