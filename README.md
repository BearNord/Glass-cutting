# Glass-cutting
A repository for solving a glass cutting optimisation problem

## Inputs and defintions
**Item**: an item is a glass piece to cut. An item i is characterized by a pair
	$(w_i, h_i)$ representing its width and height.
	 
**Stack**: a stack $s = (i_1, i_2, \ldots , i_j )$ is an ordered sequence of items such that
	$i_1 <_{cut} i_2 <_{cut} \ldots <_{cut} i_j$ , with $<_{cut}$ the partial order operator. For
	two items $i_1 \text{ and } i_2, i_1 <_{cut} i_2$ means that item $i_1$ has to be cut before
	item $i_2$. This order comes from some scheduling constraints related to the
	deliveries and item processing.
   
**Batch**: a batch $I$ is the set of items to cut. It corresponds to a customer order.
	Using the stack notation, the item set I can be partitioned into $n$ stacks,
	$I = \bigcup_{k = 1}^{n} s_k .$
	 
**Bin**: a bin is a jumbo obtained at the end of the float process. A bin $b$ is
	characterized by its width $W_b$, its height $H_b$ and its defect set $D_b$. Jumbo’s
	are stacked in the factory thus the bin set $B$ is considered as ordered.
	Assume that bins are indexed from $\{0, \ldots , |B|\}$, for two bins $b_1$ and $b_2$,
	$b_1 <_{cut} b_2$ means that bin $b_1$ is used to cut some items before starting
	using bin $b_2$. This implies that $b_1$ is removed from the bin stack before
	starting using bin $b_2$. Bins are assumed in a quantity large enough to
	cut all items and have the same size. The bin size is standardised. The
	difference between them is related to their defect set.
	 
**Defect**: a defect $d$ is a tuple $(x_d, y_d, w_d, h_d)$ with $x_d$ is its coordinates on the
	x-axis, $y_d$ is its coordinates on the y-axis. $w_d$ (resp. $h_d$) is its width (resp. height).

**Guillotine cut**: a guillotine cut on a plate is a cut from one edge of the plate
	to the opposite edge, parallel to the remaining edge. In other words, the
	cut is guillotine if when applied to a rectangular plate it produces two new
	rectangular plates. This type of cut is mandatory to cut glass, it produces
	cracks otherwise.
