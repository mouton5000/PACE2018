import steiner.instances as instances
import itertools


class Tree:
    """Unrooted tree data structure

    That data structure represent a subforest of a steiner instance.
    - add an edge to the tree with add_edge. If adding the edge creates a cycle, the maximum weight edge of that cycle
    is removed from the tree
    - remove an edge of the tree
    - simplify the tree: cut every leaf that is not a terminal (and do it again until every leaf is a terminal)
    - iterate the edges of the tree
    The structure maintain the leaves (with the self.leaves attribute) and the keynodes (with the self.key_nodes
    attribute).
    """

    def __init__(self, g, weights):
        self.cost = 0
        self.nodes = {}
        self.g = g
        self.weights = weights
        self.leaves = set()
        self.key_nodes = set()

    def __iter__(self):
        return iter(tu.father_edge for u, tu in self.nodes.items() if tu.father_edge is not None)

    def add_edge(self, e, handle_conflict=True):
        """ Add the edge e to the tree. If doing so creates a cycle and if handle_conflict is True,
        the maximum weight edge of that cycle is removed from the tree. If handle_conflict is False, the edge is not
        added."""
        u, v = e.extremities
        try:
            tu = self.nodes[u]
        except KeyError:
            tu = _TreeNode(u)
            self.nodes[u] = tu

        try:
            tv = self.nodes[v]
        except KeyError:
            tv = _TreeNode(v)
            self.nodes[v] = tv

        if tu.father == tv or tv.father == tu:
            return False

        we = self.weights[e]
        source = self._conflict(e, tu, tv, handle_conflict)

        if source is None:
            return False

        self.cost += we

        if source == tu:
            self._union(tv, tu)
        else:
            self._union(tu, tv)

        self._check_leaf(tu)
        self._check_leaf(tv)
        self._check_key_node(tu)
        self._check_key_node(tv)

        return True

    def _union(self, tu, tv):
        tv.evert()
        tv.father = tu

    def _conflict(self, e, tu, tv, handle_conflict):
        ru = tu.find()
        rv = tv.find()

        if ru != rv:
            return tu

        if not handle_conflict:
            return None

        f, tu2, source = self._maximum_weight_ancestor_edge(tu, tv)
        we, wf = self.weights[e], self.weights[f]
        if wf > we:
            tu2.father = None
            self.cost -= - wf
            return source
        return None

    def _maximum_weight_ancestor_edge(self, tu, tv):
        ''' Return the maximum weight edge e of the cycle created when we add the (tu-tv) edge, except the edge (tu-tv).
        This is done by a Nearest common ancestor search.
        Return the edge e, the child node of the edge (the node tn such that e = (tn.father - tn) and the node
        source = tu or tv such that e is on the path from source to the common ancestor of tu and tv)
        '''
        best = None
        wbest = None

        def update(e, tn, source):
            nonlocal best, wbest
            we = self.weights[e]
            if wbest is None or wbest < we:
                best = e, tn, source
                wbest = we

        su = set()
        sv = set()
        lu = []
        lv = []

        last_e = None

        def up(tn, sm, ln, sn):
            nonlocal last_e
            e = tn.father_edge
            if e is None:
                return None
            if e in sm:
                last_e = e
                return False
            ln.append((e, tn))
            sn.add(e)
            return True

        alt = True

        while True:
            if alt:
                r = up(tu, sv, lu, su)
                tu = tu.father

            else:
                r = up(tv, su, lv, sv)
                tv = tv.father
            if not r:
                break
            alt = not alt

        if r is None:
            if alt:
                tn, sm, ln, sn = tv, su, lv, sv
            else:
                tn, sm, ln, sn = tu, sv, lu, su

            while True:
                r = up(tn, sm, ln, sn)
                tn = tn.father
                if not r:
                    break

        for l, source in zip([lu, lv], [tu, tv]):
            for e, tn in l:
                if e == last_e:
                    break
                update(e, tn, source)

        return best

    def remove_edge(self, e):
        """Remove edge e from the tree, assume that the edge is in the tree."""
        u, v = e.extremities
        tu = self.nodes[u]
        tv = self.nodes[v]

        if tu.father == tv:
            tu.father = None
            tu.enroot()
        else:
            tv.father = None
            tv.enroot()

        self.cost -= self.weights[e]
        self._check_leaf(tu)
        self._check_leaf(tv)
        self._check_key_node(tu)
        self._check_key_node(tv)

    def _check_leaf(self, tu):
        if tu.is_leaf():
            self.leaves.add(tu)
        else:
            self.leaves.discard(tu)

    def _check_key_node(self, tu):
        if tu.is_key_node():
            self.key_nodes.add(tu)
        else:
            self.key_nodes.discard(tu)

    def simplify(self, terms):
        """Cut every leaf that is not a terminal (and do it again until every leaf is a terminal)"""

        torem = []
        toadd = []

        def simplify_leaf(tn):
            torem.append(tn)
            while tn.node not in terms:
                tv = tn.father
                if tv is not None:
                    e = tn.father_edge
                    tn.father = None
                else:
                    tv = next(iter(tn.children))
                    e = tv.father_edge
                    tv.father = None

                    # If tn is a root of the forest, if can be referenced as tu.root for some node tu
                    # By doing this, any node pointing to tn will then point to the root of tv (currently itself due
                    # to the "tv.father = None" statement).

                    tn.root = tv

                del self.nodes[tn.node]
                self.cost -= self.weights[e]

                if tv.is_leaf():
                    tn = tv
                else:
                    self._check_key_node(tv)
                    break
            else:
                toadd.append(tn)

        for tu in self.leaves:
            if tu.node not in terms:
                simplify_leaf(tu)

        for tu in torem:
            self.leaves.remove(tu)
        for tv in toadd:
            self.leaves.add(tv)


class _TreeNode:
    def __init__(self, node):
        self.root = self
        self.node = node
        self.__father = None
        self.__father_edge = None
        self.children = set()

    def __iter__(self):
        tovisit = [self]
        while len(tovisit) > 0:
            tn = tovisit.pop(0)
            yield tn
            tovisit += tn.children

    def is_leaf(self):
        return len(self.children) == 0 or self.father is None and len(self.children) == 1

    @property
    def father(self):
        return self.__father

    @property
    def father_edge(self):
        if self.__father_edge is None:
            if self.father is None:
                return None
            self.__father_edge = self.father.node.get_incident_edge(self.node)
        return self.__father_edge

    @father.setter
    def father(self, father):
        prev = self.__father
        if prev is not None:
            prev.children.remove(self)

        self.__father = father
        self.__father_edge = None
        if father is not None:
            self.root = father.root
            father.children.add(self)
        else:
            self.root = self

    def find(self):
        root = self

        while root != root.root:
            root = root.root

        node = self
        while node != root:
            node, node.root = node.root, root
        return root

    def evert(self):
        c = self
        f = c.father
        q = c.father
        self.father = None
        while f is not None:
            f = q.father
            q.father = c
            c, q = q, f

        self.father = None

    def enroot(self):
        for v in self:
            v.root = self

    def is_key_node(self):
        s = len(self.children)
        return s >= 3 or self.father is not None and s == 2

    def is_root(self):
        return self.father is None

    def __str__(self):
        return str(self.node)

    def __repr__(self):
        return str(self.node)


if __name__ == '__main__':
    from dynamicgraphviz.graph.undirectedgraph import UndirectedGraph

    g = UndirectedGraph()
    v1, v2, v3, v4, v5, v6, v7, v8 = [g.add_node() for _ in range(8)]
    e0 = g.add_edge(v8, v1)
    e1 = g.add_edge(v1, v2)
    e2 = g.add_edge(v1, v3)
    e3 = g.add_edge(v3, v4)
    e4 = g.add_edge(v3, v5)
    e5 = g.add_edge(v4, v6)
    e6 = g.add_edge(v4, v7)
    e7 = g.add_edge(v2, v6)
    weights = {
        e0: 1,
        e1: 1,
        e2: 1,
        e3: 3,
        e4: 1,
        e5: 1,
        e6: 1,
        e7: 5,
    }
    terms = [v1, v5, v6]
    inst = instances.SteinerInstance(g, terms, weights)

    t = Tree(g, weights)
    for e in g.edges:
        print(e, t.add_edge(e))
    print(t.cost)
    for v in g:
        tv = t.nodes[v] if v in t.nodes else None
        print(v, (tv.father, tv.root) if tv is not None else None)
    print(t.leaves)
    print(t.key_nodes)
    for e in t:
        print(e)

    print()

    print()
    t.simplify(terms)
    print(t.cost)
    for v in g:
        tv = t.nodes[v] if v in t.nodes else None
        print(v, (tv.father, tv.root) if tv is not None else None)
    print(t.key_nodes)

    print()

    for v in g:
        tv = t.nodes[v] if v in t.nodes else None
        print(v, (tv.father, tv.find()) if tv is not None else None)
    print(t.leaves)
    print(t.key_nodes)
    for e in t:
        print(e)
