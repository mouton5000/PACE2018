from helpers.sttree import STTRee


def kruskal(g, weights):
    edges = [e for e in g.edges]
    edges.sort(key=lambda x: weights[x])

    tree = STTRee()
    non_tree = []
    for e in edges:
        u, v = e.extremities
        if tree.root(u) != tree.root(v):
            tree.link(u, v, -weights[e])
        else:
            non_tree.append(e)

    return tree, non_tree


class DynamicSpanningTree:
    def __init__(self):
        self.__weights = {}
        self.__tree = STTRee()
        self.__non_tree = []

    @property
    def cost(self):
        return self.__tree.cost

    def reset(self, tree, non_tree, weights):
        self.__weights = weights
        self.__tree = tree
        self.__non_tree = non_tree

    def __iter__(self):
        return iter(self.__tree)

    def decrease_edge_cost(self, e, delta):
        self.__weights[e] += delta

        if e not in self.__non_tree:
            u, v = e.extremities
            pu = self.__tree.parent(u)
            pv = self.__tree.parent(v)
            if pu != v and pv != u:
                return
            elif pu == v:
                self.__tree.update_edge(u, -delta)
            else:
                self.__tree.update_edge(v, -delta)

    def link(self, e, cost):
        self.__weights[e] = cost

        u, v = e.extremities
        ru = self.__tree.root(u)
        rv = self.__tree.root(v)

        if ru == rv:
            w, mincost = self.__tree.min_cost_nca(u, v)
            if -mincost <= cost:
                print('NTA', e)
                self.__non_tree.append(e)
                return

            f = w.get_incident_edge(self.__tree.parent(w))
            self.__tree.cut(w)
            self.__non_tree.append(f)

        print('NTL', e)
        self.__tree.link(u, v, -cost)

    def remove(self, e):
        try:
            self.__non_tree.remove(e)
        except ValueError:
            u, v = e.extremities
            pu = self.__tree.parent(u)
            pv = self.__tree.parent(v)
            if pu != v and pv != u:
                print('Ici', u, v, pu, pv)
                return
            elif pu == v:
                self.__tree.cut(u)
            else:
                self.__tree.cut(v)

            ru = self.__tree.root(u)
            rv = self.__tree.root(v)
            self.__non_tree.sort(key=lambda x: self.__weights[x])
            for f in self.__non_tree:
                fu, fv = f.extremities
                rfu = self.__tree.root(fu)
                rfv = self.__tree.root(fv)
                if (rfu == ru and rfv == rv) or (rfu == rv and rfv == ru):
                    self.__tree.link(fu, fv, self.__weights[f])
                    self.__non_tree.remove(f)
                    break

            self.__non_tree.append(e)
