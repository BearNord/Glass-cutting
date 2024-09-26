# Glass-cutting
A repository for solving a glass cutting optimisation problem

## Inputs and defintions
Item: an item is a glass piece to cut. An item i is characterized by a pair
			(wi, hi) representing its width and height.
	 
Stack: a stack s = (i_1, i_2, . . . , i_j ) is an ordered sequence of items such that
			i1 <cut i2 <cut . . . <cut ij , with <cut the partial order operator. For
			two items i1 and i2, i1 <cut i2 means that item i1 has to be cut before
			item i2. This order comes from some scheduling constraints related to the
			deliveries and item processing.
			Batch: a batch I is the set of items to cut. It corresponds to a customer order.
			Using the stack notation, the item set I can be partitioned into n stacks,
			I = \bigcup_{k = 1}^{n} s_k.
	 
Bin: a bin is a jumbo obtained at the end of the float process. A bin b is
			characterized by its width Wb, its height Hb and its defect set Db. Jumbo’s
			are stacked in the factory thus the bin set B is considered as ordered.
			Assume that bins are indexed from {0, . . . , |B|}, for two bins b1 and b2,
			b1 <cut b2 means that bin b1 is used to cut some items before starting
			using bin b2. This implies that b1 is removed from the bin stack before
			starting using bin b2. Bins are assumed in a quantity large enough to
			cut all items and have the same size. The bin size is standardised. The
			difference between them is related to their defect set.
	 
Defect: a defect d is a tuple (xd, yd, wd, hd) with xd is its coordinates on the
			x-axis, yd is its coordinates on the y-axis. wd (resp. hd) is its width (resp.
			height).
	 
Guillotine cut: a guillotine cut on a plate is a cut from one edge of the plate
			to the opposite edge, parallel to the remaining edge. In other words, the
			cut is guillotine if when applied to a rectangular plate it produces two new
			rectangular plates. This type of cut is mandatory to cut glass, it produces
			cracks otherwise.
