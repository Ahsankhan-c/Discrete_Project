# triad_class (T3)

A triad is written as a 6-bit number. Bit 0 is edge 0->1, bit 1 is 0->2, bit 2 is 1->0, bit 3 is 1->2, bit 4 is 2->0 and bit 5 is 2->1.

The 64 possible numbers fall into 16 groups when we relabel the 3 nodes in all 6 ways. 13 of these groups are connected, and these are the 13 triad classes. The canonical code of a triad is the smallest code over all 6 orderings.


# Hand example

Triad 0->1, 1->2, 2->0. Some orderings give code 25 and the others give code 38. The smallest is 25, so this triad is class 9, the directed cycle.
