# randomize (T5)

One swap replaces edges (a,b) and (c,d) with (a,d) and (c,b). Node a still sends one edge, node c still sends one edge, node b still receives one edge and node d still receives one edge. So every in-degree and out-degree stays the same.

An attempt is rejected if a = d, c = b, or (a,d) or (c,b) already exists. Rejected attempts still count as attempts.


# Z-scores (T6)

Z = (N - mean) / std, where mean and std are taken over the random networks (population standard deviation). If std is 0 then Z = 0. Z > 2 is a motif and Z < -2 is an anti-motif.

Keeping the degrees the same matters because a node with a large out-degree creates many one-sender-two-receivers triads just by combinatorics. So the real graph must be compared with random graphs that have the same degrees.
