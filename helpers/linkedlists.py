
class LinkedList:
    def __init__(self):
        self.__first = None
        self.__last = None
        self.__nodes = {}
        self.__size = 0

    @property
    def first(self):
        return self.__first.elem

    @property
    def last(self):
        return self.__last.elem

    def __iter__(self):
        n = self.__first
        while n is not None:
            yield n.elem
            n = n.next

    def __contains__(self, e):
        return e in self.__nodes

    def __len__(self):
        return self.__size

    def add(self, e):
        '''Add e to the end of the list. e must have a next and prev attribute.'''
        if self.__first is None:
            self.__first = self.__last = e
        else:
            self.__last.next = e
            e.prev = self.__last
            self.__last = e

        self.__size += 1

    def add_first(self, e):
        '''Add e to the beginning of the list. e must not be part of the list.'''
        ne = self._new_elem(e)
        if self.__first is None:
            self.__first = self.__last = ne
        else:
            self.__first.prev = ne
            ne.next = self.__first
            self.__first = ne

        self.__size += 1

    def add_after(self, e1, e2):
        '''Add e2 after e1 in the list. e1 must be in the list. e2 must not be part of the list.'''
        ne1 = self.__nodes[e1]
        if ne1 == self.__last:
            self.add(e2)

        ne2 = self._new_elem(e2)
        next1 = ne1.next
        ne1.next = ne2
        ne2.prev = ne1
        ne2.next = next1
        next1.prev = ne2

        self.__size += 1

    def add_before(self, e1, e2):
        '''Add e2 before e1 in the list. e1 must be in the list. e2 must not be part of the list.'''
        ne1 = self.__nodes[e1]
        if ne1 == self.__first:
            self.add_first(e2)

        ne2 = self._new_elem(e2)
        prev1 = ne1.prev
        ne1.prev = ne2
        ne2.next = ne1
        ne2.prev = prev1
        prev1.next = ne2

        self.__size += 1

    def concat(self, l):
        '''Add the list l to the end of this list. This list and l must not be empty.'''
        self.__last.next = l.__first
        l.__first.prev = self.__last
        self.__size += len(l)

    def concat_first(self, l):
        '''Add the list l to the beginning of this list. This list and l must not be empty'''
        self.__first.prev = l.__last
        l.__last.next = self.__first
        self.__size += len(l)

    def concat_after(self, e, l):
        '''Add the list l after e in the list. This list and l must not be empty'''

        ne = self.__nodes[e]
        if ne == self.__last:
            self.concat(l)

        nex = ne.next
        ne.next = l.__first
        l.__first.prev = ne
        l.__last.next = nex
        nex.prev = l.__last
        self.__size += len(l)

    def concat_before(self, e, l):
        '''Add the list l after e in the list. This list and l must not be empty'''

        ne = self.__nodes[e]
        if ne == self.__first:
            self.concat_first(l)

        pre = ne.prev
        ne.prev = l.__last
        l.__last.next = ne
        l.__first.prev = pre
        pre.next = l.__first
        self.__size += len(l)

    def remove(self, e):
        '''Remove e from the list. e must be in the list.'''
        ne = self.__nodes.pop(e)

        if ne == self.__first:
            self.__first = ne.prev
        if ne == self.__last:
            self.__last = ne.next

        if ne.prev is not None:
            ne.prev.next = ne.next
        if ne.next is not None:
            ne.next.prev = ne.prev

        self.__size -= 1

    def clear(self):
        self.__first = self.__last = None
        self.__nodes.clear()
        self.__size = 0