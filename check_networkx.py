# Only for checking our own code, the results do not use this file.
# 1) triad_class (table version) vs the plain definition: minimum code over all 6 orderings
# 2) our count_triads vs nx.triadic_census on the two department subgraphs
# nx.triadic_census is used ONLY here for checking (it has a different class order,
# so we find the matching names by making a small graph for every class).
#
# run with:  python check_networkx.py

import itertools
import random

import networkx as nx

import motif_project as mp


def triad_class_slow(a, b, c, edge_set):
    codes = []
    for order in itertools.permutations((a, b, c)):
        codes.append(mp.code_of(order, edge_set))
    return mp.CLASS_OF.get(min(codes))


def test_triad_class():
    rng = random.Random(0)
    for _ in range(5000):
        nodes = rng.sample(range(10), 3)
        edge_set = set()
        for u in nodes:
            for v in nodes:
                if u != v and rng.random() < 0.4:
                    edge_set.add((u, v))
        a, b, c = nodes
        assert mp.triad_class(a, b, c, edge_set) == triad_class_slow(a, b, c, edge_set)
    print("triad_class is the same as the slow version on 5000 random triads")


def names_for_classes():
    names = {}
    for code in mp.CONNECTED:
        G = nx.DiGraph()
        G.add_nodes_from([0, 1, 2])
        for k in range(6):
            if code & (1 << k):
                G.add_edge(*mp.EDGE_ORDER[k])
        census = nx.triadic_census(G)
        for name in census:
            if census[name] == 1:
                names[mp.CLASS_OF[code]] = name
    return names


def compare(edges, label, names):
    ours = mp.count_triads(edges)
    G = nx.DiGraph()
    G.add_edges_from(edges)
    theirs = nx.triadic_census(G)
    for cls in range(1, 14):
        assert ours[cls - 1] == theirs[names[cls]], (label, cls)
    print(label + ": all 13 counts are equal to nx.triadic_census")


def main():
    test_triad_class()
    names = names_for_classes()
    print("our class -> networkx name:", names)

    edges, _ = mp.read_edges(mp.EDGE_FILE)
    dept = mp.read_departments(mp.DEPT_FILE)
    top, _ = mp.top20(edges, dept)

    R = sum(int(r) for r in mp.ROLLS)
    pairs = [(i, j) for i in range(20) for j in range(i + 1, 20)]
    i, j = pairs[R % 190]

    for label, d in [("dept A", top[i]), ("dept B", top[j])]:
        nodes, sub = mp.subgraph(edges, dept, d)
        compare(sub, "%s (%d)" % (label, d), names)
        copy = mp.randomize(sub, 5 * len(sub), 123)
        compare(copy, "%s random copy" % label, names)
    print("all checks passed")


if __name__ == "__main__":
    main()
