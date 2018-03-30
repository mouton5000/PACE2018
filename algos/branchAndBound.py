from algos.melhorntwoapprox import MelhornTwoApprox
import parameters

def compute(instance, tree):

    nodes = list(x for x in instance.g if x not in instance.terms)
    k = len(instance.terms)
    upperbound = tree.cost

    melhorn = MelhornTwoApprox(instance)

    nodeindex = 0
    nbkeynodes = 0

    decisions = []

    while nodeindex > -1:
        if nodeindex == len(nodes):
            nodeindex -= 1
        elif nodeindex == len(decisions):
            decisions.append(0)
            melhorn.add_sources([nodes[nodeindex]])
            nbkeynodes += 1

            if melhorn.lower_bound() > upperbound:
                continue

            cost = melhorn.current_cost()
            if parameters.DEBUG:
                print(nodeindex, melhorn.lower_bound(), upperbound, cost - upperbound, melhorn.current_cost() - upperbound)

            if cost < upperbound:
                upperbound = cost
                yield melhorn.current_tree()

            if nbkeynodes < k - 1:
                nodeindex += 1

        elif decisions[-1] == 0:
            decisions[-1] = 1
            melhorn.rem_sources([nodes[nodeindex]])
            nbkeynodes -= 1
            nodeindex += 1

        else:
            decisions.pop()
            nodeindex -= 1
