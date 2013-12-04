import itertools

def bicycle(iterable, repeat=1):
	"""
	repeat iterable array, repeat each item the number of repeat value
	example:
	c = bicycle([1,2,3,4],2)
	print [c.next() for _ in xrange(10)]
	[1, 1, 2, 2, 3, 3, 4, 4, 1, 1]
	"""
	for item in itertools.cycle(iterable):
		for _ in xrange(repeat):
			yield item


