# randomize (T5)

One swap replaces edges (a,b) and (c,d) with (a,d) and (c,b). Node a still sends one edge, node c still sends one edge, node b still receives one edge and node d still receives one edge. So every in-degree and out-degree stays the same.

An attempt is rejected if a = d, c = b, or (a,d) or (c,b) already exists. Rejected attempts still count as attempts.
