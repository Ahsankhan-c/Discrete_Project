# CS1005 Discrete Structures - Fall 2026
# Course project: finding network motifs in an email network
#
# Group:
#   Fida Hussain (25i-0689, B) - leader
#   Muhammad Shamir Ali Shah (25i-0717, A)
#   Ahsan Khan (25i-0535, B)
#   Syed Hamza Haider (25i-1035, A)
#
# R = 689 + 717 + 535 + 1035 = 2976
# pair number = 2976 % 190 = 126 -> (i, j) = (8, 11)
# department A = top20[8] = 15, department B = top20[11] = 13
# random networks = 20 + 2976 % 31 = 20
# swap attempts = (5 + 2976 % 6) * edges = 5 * edges
# seed = 2976
#
# run with:  python motif_project.py

import os
import math
import random
import itertools

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

# last 4 digits of our roll numbers (strings because of the leading zeros)
ROLLS = ["0689", "0717", "0535", "1035"]

EDGE_FILE = "data/email-Eu-core.txt"
DEPT_FILE = "data/email-Eu-core-department-labels.txt"
OUT_DIR = "results"

# ---------------------------------------------------------------
# the 6 possible edges of a triad, bit k is 1 if edge k is there
# ---------------------------------------------------------------
EDGE_ORDER = [(0, 1), (0, 2), (1, 0), (1, 2), (2, 0), (2, 1)]

# canonical codes of the 13 connected classes (class 1 .. class 13)
CONNECTED = [3, 6, 7, 10, 11, 15, 21, 23, 25, 27, 30, 31, 63]
CLASS_OF = {}
for n in range(13):
    CLASS_OF[CONNECTED[n]] = n + 1


# ---------------- T1 ----------------

def read_edges(filename):
    edges = []
    seen = set()
    lines = 0
    for line in open(filename):
        p = line.split()
        if len(p) != 2:
            continue
        lines += 1
        u = int(p[0])
        v = int(p[1])
        if u == v:
            continue            # self loop
        if (u, v) in seen:
            continue            # duplicate edge
        seen.add((u, v))
        edges.append((u, v))
    return edges, lines


def read_departments(filename):
    dept = {}
    for line in open(filename):
        p = line.split()
        if len(p) == 2:
            dept[int(p[0])] = int(p[1])
    return dept


def top20(edges, dept):
    # count internal edges of every department
    internal = {}
    for d in dept.values():
        internal[d] = 0
    for u, v in edges:
        if dept[u] == dept[v]:
            internal[dept[u]] += 1
    # most edges first, smaller id wins a tie
    ranked = sorted(internal, key=lambda d: (-internal[d], d))
    return ranked[:20], internal


# ---------------- T2 ----------------

def subgraph(edges, dept, d):
    nodes = [n for n in dept if dept[n] == d]
    nodeset = set(nodes)
    sub = []
    for u, v in edges:
        if u in nodeset and v in nodeset:
            sub.append((u, v))
    return sorted(nodes), sub


# ---------------- T3 ----------------

def code_of(order, edge_set):
    # order is a tuple of the 3 nodes, returns the 6 bit number
    code = 0
    for k in range(6):
        i, j = EDGE_ORDER[k]
        if (order[i], order[j]) in edge_set:
            code += 2 ** k
    return code


def relabel(code, perm):
    # rename the 3 positions with perm and give back the new code
    new = 0
    for k in range(6):
        if code & (1 << k):
            i, j = EDGE_ORDER[k]
            new += 2 ** EDGE_ORDER.index((perm[i], perm[j]))
    return new


# for each of the 64 codes we keep the smallest code we can get by
# relabelling the 3 nodes in all 6 ways
CANON = []
for code in range(64):
    smallest = code
    for perm in itertools.permutations(range(3)):
        if relabel(code, perm) < smallest:
            smallest = relabel(code, perm)
    CANON.append(smallest)

# 64 codes -> 16 orbits, 13 of them are connected
assert len(set(CANON)) == 16
assert sorted(c for c in set(CANON) if c in CLASS_OF) == CONNECTED


def triad_class(a, b, c, edge_set):
    # returns 1..13, or None if the three nodes are not connected
    code = code_of((a, b, c), edge_set)
    return CLASS_OF.get(CANON[code])


def hand_example():
    # the directed cycle 0->1->2->0
    edge_set = {(0, 1), (1, 2), (2, 0)}
    text = ["hand example: edges 0->1, 1->2, 2->0"]
    best = 63
    for order in itertools.permutations((0, 1, 2)):
        c = code_of(order, edge_set)
        text.append("  order %s gives code %d" % (str(order), c))
        if c < best:
            best = c
    text.append("  smallest code is %d, so this is class %d" % (best, CLASS_OF[best]))
    return text


# ---------------- T4 ----------------

def count_triads(edges):
    edge_set = set(edges)
    # neighbours in either direction
    nbrs = {}
    for u, v in edges:
        if u not in nbrs:
            nbrs[u] = set()
        if v not in nbrs:
            nbrs[v] = set()
        nbrs[u].add(v)
        nbrs[v].add(u)

    counts = [0] * 13
    counted = set()
    for x in nbrs:
        for a, b in itertools.combinations(sorted(nbrs[x]), 2):
            t = tuple(sorted([x, a, b]))
            if t in counted:
                continue            # already found from another node
            counted.add(t)
            k = triad_class(t[0], t[1], t[2], edge_set)
            assert k is not None
            counts[k - 1] += 1
    return counts


# ---------------- T5 ----------------

def randomize(edges, attempts, seed):
    rng = random.Random(seed)
    cur = list(edges)
    present = set(cur)
    m = len(cur)
    for _ in range(attempts):
        i = rng.randrange(m)
        j = rng.randrange(m)
        if i == j:
            continue
        a, b = cur[i]
        c, d = cur[j]
        if a == d or c == b:
            continue
        if (a, d) in present or (c, b) in present:
            continue
        present.remove((a, b))
        present.remove((c, d))
        present.add((a, d))
        present.add((c, b))
        cur[i] = (a, d)
        cur[j] = (c, b)
    return cur


def degrees(edges):
    out_d = {}
    in_d = {}
    for u, v in edges:
        out_d[u] = out_d.get(u, 0) + 1
        in_d[v] = in_d.get(v, 0) + 1
    return out_d, in_d


def check_same_degrees(old, new):
    assert len(old) == len(new)
    assert len(set(new)) == len(new)          # no parallel edges
    for u, v in new:
        assert u != v                         # no self loops
    out1, in1 = degrees(old)
    out2, in2 = degrees(new)
    assert out1 == out2
    assert in1 == in2


# ---------------- T6 ----------------

def mean_std(runs):
    n = len(runs)
    means = []
    stds = []
    for k in range(13):
        vals = [r[k] for r in runs]
        mu = sum(vals) / n
        var = sum((x - mu) ** 2 for x in vals) / n     # population variance
        means.append(mu)
        stds.append(math.sqrt(var))
    return means, stds


def zscores(real, runs):
    means, stds = mean_std(runs)
    z = []
    for k in range(13):
        if stds[k] < 1e-12:
            z.append(0.0)
        else:
            z.append((real[k] - means[k]) / stds[k])
    return z


# ---------------- T7 ----------------

def draw_chart(zA, zB, R, dA, dB, filename):
    xs = range(1, 14)
    w = 0.38
    plt.figure(figsize=(11, 5.5))
    plt.bar([x - w / 2 for x in xs], zA, w, label="Department %d (A)" % dA)
    plt.bar([x + w / 2 for x in xs], zB, w, label="Department %d (B)" % dB)
    plt.axhline(2, linestyle="--", color="black", linewidth=1)
    plt.axhline(-2, linestyle="--", color="black", linewidth=1)
    plt.axhline(0, color="gray", linewidth=0.8)
    plt.xticks(list(xs))
    plt.xlabel("Triad class")
    plt.ylabel("Z-score")
    plt.title("Triad Z-scores of Department %d vs Department %d (R = %d)" % (dA, dB, R))
    plt.legend()
    plt.tight_layout()
    plt.savefig(filename, dpi=200)
    plt.close()


# ---------------- main ----------------

out = []   # everything we print also goes in here, saved to a file at the end

def log(text=""):
    print(text)
    out.append(text)


def verdict(z):
    if z > 2:
        return "motif"
    if z < -2:
        return "anti-motif"
    return "-"


def run_department(label, d, edges, dept, num_random, swap_factor, seed):
    nodes, sub = subgraph(edges, dept, d)
    log("Department %s = %d: %d nodes, %d edges" % (label, d, len(nodes), len(sub)))

    real = count_triads(sub)
    attempts = swap_factor * len(sub)

    master = random.Random(seed)
    runs = []
    for r in range(num_random):
        s = master.randrange(2 ** 32)
        new_edges = randomize(sub, attempts, s)
        check_same_degrees(sub, new_edges)
        runs.append(count_triads(new_edges))
    log("  made %d random networks, degree check passed for all of them" % num_random)

    means, stds = mean_std(runs)
    z = zscores(real, runs)
    return real, z, means, stds


def main():
    os.makedirs(OUT_DIR, exist_ok=True)

    # T1
    R = 0
    for r in ROLLS:
        R += int(r)
    edges, lines = read_edges(EDGE_FILE)
    dept = read_departments(DEPT_FILE)
    log("T1: data")
    log("lines in file: %d, edges after cleaning: %d" % (lines, len(edges)))
    log("nodes: %d, departments: %d" % (len(dept), len(set(dept.values()))))
    log()

    top, internal = top20(edges, dept)
    log("top 20 departments (index, department, internal edges):")
    for idx in range(20):
        log("  %2d   %2d   %d" % (idx, top[idx], internal[top[idx]]))
    log()

    pairs = []
    for i in range(20):
        for j in range(i + 1, 20):
            pairs.append((i, j))
    pair_no = R % 190
    i, j = pairs[pair_no]
    dA = top[i]
    dB = top[j]
    num_random = 20 + R % 31
    swap_factor = 5 + R % 6
    seed = R

    log("R = %d" % R)
    log("pair number = %d -> (i, j) = (%d, %d)" % (pair_no, i, j))
    log("department A = %d, department B = %d" % (dA, dB))
    log("random networks = %d" % num_random)
    log("swap attempts = %d x edges" % swap_factor)
    log("seed = %d" % seed)
    log()

    # T3
    for line in hand_example():
        log(line)
    log()

    # T2, T4, T5, T6
    log("T2, T4, T5, T6")
    realA, zA, meanA, stdA = run_department("A", dA, edges, dept, num_random, swap_factor, seed)
    realB, zB, meanB, stdB = run_department("B", dB, edges, dept, num_random, swap_factor, seed)
    log()

    log("T4: triad counts   (class, code, dept A, dept B)")
    for k in range(13):
        log("  %2d  %2d  %5d  %5d" % (k + 1, CONNECTED[k], realA[k], realB[k]))
    log()

    for name, d, mean, std, z in [("A", dA, meanA, stdA, zA), ("B", dB, meanB, stdB, zB)]:
        log("T6: department %s (%d)   (class, mean, std, Z, result)" % (name, d))
        for k in range(13):
            log("  %2d  %8.1f  %7.2f  %6.2f  %s" % (k + 1, mean[k], std[k], z[k], verdict(z[k])))
        log()

    # T7
    chart = os.path.join(OUT_DIR, "zscore_chart_R%d.png" % R)
    draw_chart(zA, zB, R, dA, dB, chart)
    log("chart saved: " + chart)

    # save files
    f = open(os.path.join(OUT_DIR, "triad_counts.csv"), "w")
    f.write("class,code,dept_A_%d,dept_B_%d\n" % (dA, dB))
    for k in range(13):
        f.write("%d,%d,%d,%d\n" % (k + 1, CONNECTED[k], realA[k], realB[k]))
    f.close()

    f = open(os.path.join(OUT_DIR, "z_scores.csv"), "w")
    f.write("class,Z_dept_A_%d,Z_dept_B_%d\n" % (dA, dB))
    for k in range(13):
        f.write("%d,%.4f,%.4f\n" % (k + 1, zA[k], zB[k]))
    f.close()

    f = open(os.path.join(OUT_DIR, "parameters.txt"), "w")
    f.write("R = %d\npair_number = %d\ni = %d\nj = %d\n" % (R, pair_no, i, j))
    f.write("dept_A = %d\ndept_B = %d\nnum_random = %d\n" % (dA, dB, num_random))
    f.write("swap_factor = %d\nseed = %d\n" % (swap_factor, seed))
    f.close()

    f = open(os.path.join(OUT_DIR, "run_output.txt"), "w")
    f.write("\n".join(out) + "\n")
    f.close()


if __name__ == "__main__":
    main()
