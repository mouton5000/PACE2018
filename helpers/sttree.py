import math


class STTRee:
    def __init__(self):
        self.__path_nodes = {}
        self.__cost = 0

    def __iter__(self):
        for node in self.__path_nodes:
            parent = self.parent(node)
            if parent is not None:
                yield node.get_incident_edge(parent)

    def __str__(self):
        s = ''
        for node in sorted(list(self.__path_nodes), key=lambda x: str(x)):
            n1 = node
            while n1 is not None:
                s += str(n1) + ' --' + str(self.cost_of_node(n1)) + '--> '
                n1 = self.parent(n1)
            s += '\\\n'
        return s

    def __repr__(self):
        return str(self)

    def parent(self, v):
        n = self.__path_node(v)
        p = n.root
        t = p.tail

        if t == n:
            return n.dparent.node if n.dparent is not None else None
        else:
            a = n.after
            return a.node if a is not None else None

    def root(self, v):
        return self.__expose(v).tail.node

    @property
    def cost(self):
        return self.__cost

    def cost_of_node(self, v):
        n = self.__path_node(v)
        p = n.root
        t = p.tail

        if t == n:
            return n.dcost
        else:
            return n.pcost

    def mincost(self, v):
        return self.__expose(v).pmincost

    def __update(self, v, delta):
        self.__expose(v).pupdate(delta)

    def update_edge(self, v, delta):
        w = self.parent(v)
        if w is not None:
            self.evert(w)
            self.__update(v, delta)
            self.__cost += delta

    def link(self, v, w, cost):
        self.evert(v)
        p = self.__path(v)
        q = self.__expose(w)
        self.__concatenate(p, q, cost)
        self.__cost += cost

    def cut(self, v):
        self.__expose(v)
        p, q, x, y = self.__split(v)
        v.dparent = None
        v.dcost = None
        self.__cost -= y
        return y

    def evert(self, v):
        p = self.__expose(v)
        p.reverse()
        v.dparent = None
        v.dcost = None

    def min_cost_nca(self, v, w):
        '''Return the node u such that, if a is the minimum common ancestor of v and w, the edge (u, parent(u)) is the
        minimum cost edge over the edges on the paths from v to a and w to a. Return also the cost of the edge
        (u, parent(u)).'''
        pv = self.__expose(v)
        leafw = self.__path_node(w)

        def compare_generator():

            if leafw.root == pv:
                common_ancestor = w
            else:
                # Expose w until pv is splitted, the split node is the common ancestor
                q, r, x, y = self.__split(w)
                if q is not None:
                    t = q.tail
                    t.dparent, t.dcost = leafw, x

                p = self.__path(w)
                if r is not None:
                    p = self.__concatenate(p, r, y)

                t = p.tail
                while t.dparent is not None:
                    if t.dparent.root == pv:
                        common_ancestor = t.dparent.node

                        yield t.node,  t.dcost

                        if not p.is_leaf():
                            n1 = p.pmincost
                            c1 = n1.pcost
                            yield n1.node, c1

                        break
                    p = self.__splice(p)
                    t = p.tail
                else:
                    return

            if common_ancestor != v:

                q, r, x, y = self.__split(common_ancestor)
                if q is not None:
                    t = q.tail
                    nca = self.__path_node(common_ancestor)
                    t.dparent, t.dcost = nca, x
                    if r is not None:
                        nca.dparent, nca.dcost = r.head, y


                yield q.tail.node, x

                if not q.is_leaf():
                    n1 = q.pmincost
                    c1 = n1.pcost
                    yield n1.node, c1

        try:
            return min(compare_generator(), key=lambda x: x[1])
        except ValueError:
            return None

    def __path_node(self, v):
        try:
            return self.__path_nodes[v]
        except KeyError:
            n = _STTreePathLeaf(v)
            self.__path_nodes[v] = n
            return n

    def __path(self, v):
        return self.__path_node(v).root

    def __splice(self, p):
        leafv = p.tail.dparent
        if leafv is None:
            return

        q, r, x, y = leafv.psplit()

        if q is not None:
            t = q.tail
            t.dparent, t.dcost = leafv, x

        p = self.__concatenate(p, leafv.root, p.tail.dcost)
        if r is None:
            return p
        else:
            return self.__concatenate(p, r, y)

    def __expose(self, v):
        leafv = self.__path_node(v)
        q, r, x, y = self.__split(v)
        if q is not None:
            t = q.tail
            t.dparent, t.dcost = leafv, x
        p = self.__path(v)
        if r is not None:
            p = self.__concatenate(p, r, y)
        while p.tail.dparent is not None:
            p = self.__splice(p)
        return p

    def __split(self, v):
        return self.__path_node(v).psplit()

    def __concatenate(self, p1, p2, cost):
        p1.tail.dparent = None
        p1.tail.dcost = None
        return _STTreePathInternal(p1, p2, cost).root


class _STTreePathNode:
    def __init__(self):
        self._bparent = None
        self.height = 1

    @property
    def root(self):
        for node in self.ancestors():
            pass
        return node

    def ancestors(self):
        node = self
        while node is not None:
            yield node
            node = node._bparent


class _STTreePathLeaf(_STTreePathNode):
    def __init__(self, node):
        super().__init__()
        self.__node = node
        self.dparent = None
        self.dcost = None

    @property
    def node(self):
        return self.__node

    def is_leaf(self):
        return True

    @property
    def size(self):
        return 1

    @property
    def head(self):
        return self

    @property
    def tail(self):
        return self

    @property
    def before(self):
        ancestors = self.ancestors()
        node = next(ancestors)
        parent = node._bparent
        while parent is not None:
            if parent.bright == node:
                left = parent.bleft
                return left.tail
            node, parent = parent, parent._bparent
        else:
            return None

    @property
    def after(self):
        ancestors = self.ancestors()
        node = next(ancestors)
        parent = node._bparent
        while parent is not None:
            if parent.bleft == node:
                right = parent.bright
                return right.head
            node, parent = parent, parent._bparent
        else:
            return None

    @property
    def pcost(self):
        ancestors = self.ancestors()
        node = next(ancestors)
        parent = node._bparent
        while parent is not None:
            if parent.bleft == node:
                return parent.grosscost
            node, parent = parent, parent._bparent
        else:
            return None

    def pupdate(self, delta):
        pass

    def reverse(self):
        pass

    def psplit(self):
        if self._bparent is None:
            return None, None, None, None

        u = self.node

        node1 = self._bparent
        selfleft = (node1.bleft == self)

        ancestors = node1.ancestors()
        next(ancestors)

        for node2 in ancestors:
            e = node2.edge
            if u.is_incident_to(e):
                break
        else:
            node2 = None

        if node2 is not None:
            node2.move_to_root()
            p21, p22, cost2 = node2.destroy()
            p2 = p21 if selfleft else p22
        else:
            p2, cost2 = None, None

        node1.move_to_root()
        p11, p12, cost1 = node1.destroy()

        if selfleft:
            return p2, p12, cost2, cost1
        else:
            return p11, p2, cost1, cost2

    def __str__(self):
        return str(self.node)

    def __repr__(self):
        return str(self)


class _STTreePathInternal(_STTreePathNode):
    def __init__(self, left, right, cost):
        super().__init__()

        self.__reversed = False

        self.__bleft = left
        left._bparent = self
        self.__bright = right
        right._bparent = self

        u = left.tail.node
        v = right.head.node
        self.__edge = u.get_incident_edge(v)

        self.__bhead = left.head
        self.__btail = right.tail

        lleaf = left.is_leaf()
        rleaf = right.is_leaf()

        self.__netmin = min(cost, left.__netmin if not lleaf else math.inf, right.__netmin if not rleaf else math.inf)
        self.__netcost = cost - self.__netmin

        if not lleaf:
            left.__netmin -= self.__netmin
        if not rleaf:
            right.__netmin -= self.__netmin

        self.height = max(left.height, right.height) + 1
        self.balance()

    def destroy(self):
        # print('Destroy :', self)
        cost = self.grosscost
        left = self.bleft
        right = self.bright
        lleaf = left.is_leaf()
        rleaf = right.is_leaf()
        selfreversed = self.reversed

        if self._bparent is not None:
            if self._bparent.__bleft == self:
                self._bparent.__bleft = None
            else:
                self._bparent.__bright = None
            self._bparent = None

        self.__bleft = None
        self.__bright = None
        left._bparent = None
        right._bparent = None

        if selfreversed:
            left.reverse()
            right.reverse()

        if not lleaf:
            left.__netmin += self.__netmin
        if not rleaf:
            right.__netmin += self.__netmin

        return left, right, cost

    @property
    def edge(self):
        return self.__edge

    def balance(self):
        lh = self.bleft.height
        rh = self.bright.height
        while abs(lh - rh) > 1:
            if lh > rh:
                self.rotate_right()
            else:
                self.rotate_left()
            lh = self.bleft.height
            rh = self.bright.height

    def move_to_root(self):
        while self._bparent is not None:

            p = self._bparent
            selfleft = (p.bleft == self)

            if p._bparent is None:
                if selfleft:
                    p.rotate_right()
                else:
                    p.rotate_left()
                continue

            gp = p._bparent
            pleft = (gp.bleft == p)
            if pleft:
                gp.rotate_right()
                if selfleft:
                    p.rotate_right()
                else:
                    gp.rotate_right()
            else:
                gp.rotate_left()
                if selfleft:
                    gp.rotate_left()
                else:
                    p.rotate_left()

    @property
    def reversed(self):
        return sum(node.__reversed for node in self.ancestors()) % 2 == 1

    @property
    def local_reversed(self):
        return self.__reversed

    @property
    def bleft(self):
        return self.__bright if self.reversed else self.__bleft

    @property
    def bright(self):
        return self.__bleft if self.reversed else self.__bright

    def bleftr(self, reversed):
        return self.__bright if reversed else self.__bleft

    def brightr(self, reversed):
        return self.__bleft if reversed else self.__bright

    @bleft.setter
    def bleft(self, left):
        if self.reversed:
            self.__bright = left
        else:
            self.__bleft = left
        left._bparent = self

    @bright.setter
    def bright(self, right):
        if self.reversed:
            self.__bleft = right
        else:
            self.__bright = right
        right._bparent = self

    def is_leaf(self):
        return False

    @property
    def grosscost(self):
        return self.__netcost + self.grossmin

    @property
    def grossmin(self):
        return sum(node.__netmin for node in self.ancestors())

    @property
    def head(self):
        return self.__btail if self.reversed else self.__bhead

    @property
    def tail(self):
        return self.__bhead if self.reversed else self.__btail

    @head.setter
    def head(self, head):
        if self.reversed:
            self.__btail = head
        else:
            self.__bhead = head

    @tail.setter
    def tail(self, tail):
        if self.reversed:
            self.__bhead = tail
        else:
            self.__btail = tail

    @property
    def pmincost(self):
        node = self
        reverse = False
        while True:
            if node.local_reversed:
                reverse = not reverse
            if node.__netcost == 0:
                break

            left = node.bleftr(reverse)
            right = node.brightr(reverse)

            if left.is_leaf():
                node = right
            elif right.is_leaf():
                node = left
            elif left.__netmin < right.__netmin:
                node = left
            else:
                node = right

        node = node.bleft
        return node.tail

    def pupdate(self, delta):
        self.__netmin += delta

    def reverse(self):
        self.__reversed = not self.__reversed

    def rotate_left(self):
        parent = self._bparent

        right = self.bright
        if right.is_leaf():
            return False
        rright = right.bright
        lright = right.bleft

        left = self.bleft

        rrtail = rright.tail
        lrtail = lright.tail
        shead = self.head

        grossmin_parent = parent.grossmin if parent is not None else None
        grossmin_left = left.grossmin if not left.is_leaf() else math.inf
        grossmin_rright = rright.grossmin if not rright.is_leaf() else math.inf
        grossmin_lright = lright.grossmin if not lright.is_leaf() else math.inf
        grosscost_right = right.grosscost
        grosscost_self = self.grosscost

        right._bparent = parent
        if parent is not None:
            if parent.__bleft == self:
                parent.__bleft = right
            else:
                parent.__bright = right

        right.bright = rright
        right.bleft = self
        right.tail = rrtail.tail
        right.head = shead

        self.bright = lright
        self.bleft = left
        self.tail = lrtail
        self.head = shead

        if right.local_reversed:
            left.reverse()
        if self.local_reversed:
            rright.reverse()

        grossmin_self_2 = min(grosscost_self, grossmin_lright, grossmin_left)
        grossmin_right_2 = min(grosscost_right, grossmin_rright, grossmin_self_2)

        self.__netcost = grosscost_self - grossmin_self_2
        right.__netcost = grosscost_right - grossmin_right_2

        right.__netmin = grossmin_right_2
        if parent is not None:
            right.__netmin -= grossmin_parent
        self.__netmin = grossmin_self_2 - grossmin_right_2

        if not left.is_leaf():
            left.__netmin = grossmin_left - grossmin_self_2
        if not lright.is_leaf():
            lright.__netmin = grossmin_lright - grossmin_self_2
        if not rright.is_leaf():
            rright.__netmin = grossmin_rright - grossmin_right_2

        self.check_height()

    def rotate_right(self):
        parent = self._bparent

        left = self.bleft
        if left.is_leaf():
            return False
        lleft = left.bleft
        rleft = left.bright

        right = self.bright

        llhead = lleft.head
        rlhead = rleft.head
        stail = self.tail

        grossmin_parent = parent.grossmin if parent is not None else None
        grossmin_right = right.grossmin if not right.is_leaf() else math.inf
        grossmin_lleft = lleft.grossmin if not lleft.is_leaf() else math.inf
        grossmin_rleft = rleft.grossmin if not rleft.is_leaf() else math.inf
        grosscost_left = left.grosscost
        grosscost_self = self.grosscost

        left._bparent = parent
        if parent is not None:
            if parent.__bright == self:
                parent.__bright = left
            else:
                parent.__bleft = left

        left.bleft = lleft
        left.bright = self
        left.head = llhead.head
        left.tail = stail

        self.bleft = rleft
        self.bright = right
        self.head = rlhead
        self.tail = stail

        if left.local_reversed:
            right.reverse()
        if self.local_reversed:
            lleft.reverse()

        grossmin_self_2 = min(grosscost_self, grossmin_rleft, grossmin_right)
        grossmin_left_2 = min(grosscost_left, grossmin_lleft, grossmin_self_2)

        self.__netcost = grosscost_self - grossmin_self_2
        left.__netcost = grosscost_left - grossmin_left_2

        left.__netmin = grossmin_left_2
        if parent is not None:
            left.__netmin -= grossmin_parent
        self.__netmin = grossmin_self_2 - grossmin_left_2

        if not right.is_leaf():
            right.__netmin = grossmin_right - grossmin_self_2
        if not rleft.is_leaf():
            rleft.__netmin = grossmin_rleft - grossmin_self_2
        if not lleft.is_leaf():
            lleft.__netmin = grossmin_lleft - grossmin_left_2

        self.check_height()

    def check_height(self):
        self.height = 1 + max(self.bleft.height, self.bright.height)
        if self._bparent is not None:
            self._bparent.check_height()

    def __str__(self):
        return str(self.edge)

    def __repr__(self):
        return str(self)
