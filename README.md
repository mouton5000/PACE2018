
# PACE 2018 Track 3 : DoubleDoubleU team

The [PACE 2018](https://pacechallenge.wordpress.com/pace-2018/) (The Parameterized Algorithms and Computational Experiments Challenge) is about solving 
the NP-hard graph problem Steiner Tree on undirected edge-weighted graphs.

We participated to track 3 (Heuristic).

## Use the code

There are two ways to use the code:

First of all, Download the source code and go to the root folder
- Then, either run:
```
python3 __main__.py < instanceXYZ.gr
```

- Or:
```
./build_zip.sh
cd ..
./pace2018.zip < instanceXYZ.gr
```

where instanceXYZ.gr is an input file of PACE2018

## Quick description of the algorithm

The algorithm is mostly local search. 

The first step consists in computing two feasible solutions
- firstly, using the Melhorn 2-approximation ([A faster approximation algorithm for the Steiner problem in graphs](https://dl.acm.org/citation.cfm?id=46244))
- secondly, using the Watel and Weisser k-approximation for the Directed Steiner Tree problem ([A practical greedy approximation for the directed Steiner tree problem](https://link.springer.com/article/10.1007/s10878-016-0074-0)) 

The second step consists in adding and removing key branching nodes to the tree (a branching node is a node with degree at least 3), a technique inspired by
the paper [Fast Local Search for Steiner Trees in Graphs](https://dl.acm.org/citation.cfm?id=2790232) by Uchoa and Werneck.
The idea is that, in an optimal steiner tree, any path linking two terminals/branching nodes is a shortest path. If we know which nodes are branching nodes in the
tree, the tree can be computed in polynomial time. In order to *tell* the algorithm that a node becomes a branching node, we simply force it to be in the tree by adding it
to the terminals set. We then use the Melhorn 2-approximation algorithm to get a solution. Note that, instead of recomputing all the voronoi regions of the approximation 
at each iteration, we update them. This can be done by adapting the Dijkstra algorithm to the cases where a region appears and where a region vanishes. 

This way we can do some local search. We start from the best of the two first solutions found at the beginning and, at each iteration, 
we randomly add or delete a branching node, compute the 2-approximation solutions. Each time a better solution is found, we register it.


