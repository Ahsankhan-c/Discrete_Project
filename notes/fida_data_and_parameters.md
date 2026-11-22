# Data cleaning (T1)

The edge file has 25,571 lines. After removing self-loops and duplicate edges there are 24,929 edges. There are 1005 nodes and 42 departments.

We clean the data because the graph must be simple: no self-loops and no parallel edges.
# Parameters

R = 689 + 717 + 535 + 1035 = 2976
Pair number = 2976 mod 190 = 126, which is (i, j) = (8, 11)
Department A = 15, Department B = 13
Random networks = 20 + (2976 mod 31) = 20
Swap attempts = (5 + (2976 mod 6)) x edges = 5 x edges
Seed = 2976
