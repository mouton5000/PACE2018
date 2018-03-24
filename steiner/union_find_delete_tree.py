from matplotlib.cbook import is_writable_file_like


class Tree:
    def __init__(self):
        self.nodes = {}

    def get_node(self, u):
        try:
            return self.nodes[u]
        except KeyError:
            tnu = _TreeNode(u)
            self.nodes[u] = tnu
            return tnu

    def add_edge(self, e, handle_conflict=True):
        u, v = e.extremities
        tnu = self.get_node(u)
        tnv = self.get_node(v)

        ru = self._ufd_find(tnu)
        rv = self._ufd_find(tnv)

        if ru == rv and handle_conflict:
            self._conflict(tnu, tnv)
        else:
            self._ufd_union(ru, rv)

    def _conflict(self, tnu, tnv):
        pass

    def _udf_union_small_size(self, ru, rv):

        # Set every node of the tree of rv as a child of ru
        for tnv in list(rv.iter_udf_children):
            tnv.ufd_father = ru
            tnv.ufd_rank = 0

        ru.ufd_rank = max(ru.ufd_rank, 1)

        # Maintain the children list
        # Put the node of the tree of rv on the right of the children of u
        leftu, rightu = ru.ufd_children
        leftv, rightv = rv.ufd_children

        rv.ufd_children[0] = rv.ufd_children[1] = None

        if leftv is not None:
            if leftu is not None:
                leftv.ufd_left_sibling = rightu
                rightu.ufd_right_sibling = leftv
            else:
                ru.ufd_children[0] = leftv
            rv.ufd_left_sibling = rightv
            rightv.ufd_right_sibling = rv
        else:
            if leftu is not None:
                rv.ufd_left_sibling = rightu
                rightu.ufd_right_sibling = rv
            else:
                ru.ufd_children[0] = rv
        ru.ufd_children[1] = rv

        # Maintain the dfs trees, insert rv and its children just after ru in the list
        firstu = ru.ufd_dfs_tree_next_node
        lastv = rv.ufd_dfs_tree_previous_node

        ru.ufd_dfs_tree_next_node = rv
        rv.ufd_dfs_tree_previous_node = ru
        lastv.ufd_dfs_tree_next_node = firstu
        firstu.ufd_dfs_tree_previous_node = lastv

    def _udf_union_big_size(self, ru, rv):
        rv.ufd_father = ru
        if rv.ufd_rank == ru.ufd_rank:
            ru.ufd_rank += 1

        # Add rv to the right of the children of u
        leftu, rightu = ru.ufd_children
        if rightu is None:
            ru.ufd_children[0] = rv
        else:
            rightu.ufd_right_sibling = rv
        rv.ufd_left_sibling = rightu
        ru.ufd_children[1] = rv

        # Add rv to the right of the non leaves children of u
        leftu, rightu = ru.ufd_not_leaves_children
        if rightu is None:
            ru.ufd_not_leaves_children[0] = rv
        else:
            rightu.ufd_right_not_leaves_children = rv
        rv.ufd_left_not_leaves_children = rightu
        ru.ufd_not_leaves_children[1] = rv

        # rv is not a root anymore
        rv.ufd_not_leaves_children[0] = rv.ufd_not_leaves_children[1] = None

        # Maintain the dfs trees, insert rv and its children just after ru in the list
        firstu = ru.ufd_dfs_tree_next_node
        lastv = rv.ufd_dfs_tree_previous_node

        ru.ufd_dfs_tree_next_node = rv
        rv.ufd_dfs_tree_previous_node = ru
        lastv.ufd_dfs_tree_next_node = firstu
        firstu.ufd_dfs_tree_previous_node = lastv

    def _ufd_union(self, ru, rv):
        sizeu = ru.ufd_size
        sizev = rv.ufs_size

        if sizeu < sizev:
            ru, rv = rv, ru
            sizeu, sizev, = sizev, sizeu

        if sizev < 4:
            self._udf_union_small_size(ru, rv)
        else:
            self._udf_union_big_size(ru, rv)

        ru.ufd_size += rv.ufd_size

    def _ufd_find(self, tnu):
        while tnu.ufd_father.ufd_father != tnu.ufd_father:
            self._ufd_relink(tnu)
            tnu = tnu.ufd_father
        return tnu.ufd_father

    def _ufd_relink(self, tnu):

        ftnu = tnu.ufd_father
        fftnu = ftnu.ufd_father

        # remove from the list of ftnu
        left, right = ftnu.ufd_left_sibling, ftnu.ufd_right_sibling
        if ftnu.ufd_children[0] == tnu:
            ftnu.ufd_children[0] = right
        if ftnu.ufd_children[1] == tnu:
            ftnu.ufd_children[1] = left

        if left is not None:
            left.ufd_right_sibling = right
        if right is not None:
            right.ufd_left_sibling = left

        # insert tnu to the list of children of fftnu
        # On the right of ftnu if tnu has a left sibling
        if left is not None:
            fright = ftnu.ufd_right_sibling
            ftnu.ufd_right_sibling = tnu
            tnu.ufd_left_sibling = ftnu
            if fright is not None:
                fright.ufd_left_sibling = tnu
            else:
                fftnu.ufd_children[1] = tnu
            tnu.ufd_right_sibling = fright

            # On that case, change the dfs list of fftnu

            lasttnu = left.ufd_dfs_tree_previous_node
            prevtnu = tnu.ufd_dfs_tree_previous_node
            prevftnu = ftnu.ufd_dfs_tree_previous_node

            # Remove the segment [tnu - lasttnu]
            left.ufd_dfs_tree_previous_node = prevtnu
            prevtnu.ufd_dfs_tree_next_node = left

            # and put it before ftnu
            ftnu.ufd_dfs_tree_previous_node = lasttnu
            lasttnu.ufd_dfs_tree_next_node = ftnu
            prevftnu.ufd_dfs_tree_next_node = tnu
            tnu.ufd_dfs_tree_next_node = prevftnu

        # On the left of ftnu otherwise
        else:
            fleft = ftnu.ufd_left_sibling
            ftnu.ufd_left_sibling = tnu
            tnu.ufd_right_sibling = ftnu
            if fleft is not None:
                fleft.ufd_right_sibling = tnu
            else:
                fftnu.ufd_children[0] = tnu
            tnu.ufd_left_sibling = fleft
            # The dfs list should not be changed

        if ftnu.is_leaf:
            ftnu.ufd_rank = 0
            if fftnu.ufd_not_leaves_children[0] is not None:
                # Remove ftnu from the ufd_not_leaves_children list of fftnu
                left, right = ftnu.ufd_left_not_leaves_children, ftnu.ufd_right_not_leaves_children
                if fftnu.ufd_not_leaves_children[0] == ftnu:
                    fftnu.ufd_not_leaves_children[0] = left
                if fftnu.ufd_not_leaves_children[1] == ftnu:
                    fftnu.ufd_not_leaves_children[1] = right

                if left is not None:
                    left.ufd_right_not_leaves_children = right
                if right is not None:
                    right.ufd_left_not_leaves_children = left

                # if the ufd_not_leaves_children list becames empty
                if fftnu.ufd_not_leaves_children[0] is None:
                    fftnu.ufd_rank = 1


class _TreeNode:
    def __init__(self, u):
        self.node = u
        self.ufd_father = self
        self.ufd_rank = 0

        self.ufd_left_sibling = None  # left child (from the list ufd_children) of its father node
        self.ufd_right_sibling = None  # right child (from the list ufd_children) of its father node
        self.ufd_children = [None, None]  # left and right nodes of the list of nodes this node is the father of

        self.ufd_left_not_leaves_children = None  # if its father is a root, left non leaf child of its father node
        self.ufd_right_not_leaves_children = None  # if its father is a root, right non leaf child of its father node
        # if this node is a root, left and right node of the list of children that are not leaves
        self.ufd_not_leaves_children = [None, None]

        # Each node is in a dfs order of its tree (the rightmost child first).
        self.ufd_dfs_tree_previous_node = self  # previous node in the tree containing this node
        self.ufd_dfs_tree_next_node = self  # next node in the tree containing this node
        self.ufd_size = 1  # if this node is a root, size of the corresponding subtree

    @property
    def iter_udf_children(self):
        left, right = self.ufd_children
        tv = right
        while tv is not None:
            yield tv
            tv = tv.ufd_left_sibling

    @property
    def iter_ufd_dfs_tree(self):
        yield self
        tv = self.ufd_dfs_tree_next_node
        while tv != self:
            yield tv
            tv = tv.ufd_dfs_tree_next_node

    def is_leaf(self):
        return self.ufd_children[0] is None
