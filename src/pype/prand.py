# -*- Mode: Python; tab-width: 4; py-indent-offset: 4; -*-

"""Mersenne Twister based random number generator

This module is intended to provide a reasonable fast random number
generator object that allows for (1) multiple generators running in
parallel and (2) saving/restoring of generator state to allow
easy regeneration of number sequences and (3) use a welll documented
algorithm (Mersenne Twister) that can easily be implemented or
exists in Matlab.

Starting with Matlab 7.1 the built in RAND() function uses the
same Mersenne Twister engine that python's (2.4 on) random.Random()
object uses. This means you can go back and forth pretty easily.
The only catach is that python's state vector is composed of signed
long's, while matlab's is unsigned. This means that to take the
python state vector into matlab you need to add 2^32 to all negative
values in the state vector before passing to the RAND function:

	>> s = [state vector from puthon..]
	>> s(s<0)=s(s<0)+(2^32); rand('twister', s);

Will put the generator at the same state the python generator was
at when the state was saved. RAND(100) in matlab will now generate
the same random sequence the python call:

	>> PypeRandom(seed=statevector).rand(100)

would. At least to about +- 1.0e-11 as far as I can tell..

Author -- Matt Krause (matthew.krause@yale.edu)

"""

class MTRandom(object):
	def __init__(self, seed=None, state=None):
		"""Uniform random number generator object.

		Instantiate a uniform random number generator. This *should*
		be the Mersenne Twister based generator that is standard in
		Python (at least up to version 2.6).

		Generates floating point numbers in the range [0-1].

		If neither seed nor state are supplied, this will use the current
		time to generate a seed.

		*NB* To set the matlab random number generator to the same
		known state as the python generator, you need to convert the
		signed values of the seed into unsigned values as follows:

			>> seed = [get me from file etc..];
			>> seed(seed < 0 ) = seed(seed < 0) + (2^32);
			>> rand('twister', seed);

		:param seed: (int) single integer seed value

		:param state: (int array) length 624 SIGNED 2-byte integer
				vector that completely captures the state of the
				random number generator.  Note that these are SIGNED
				values -- matlab expects UNSIGNED values; see notes
				below. This comes from .getstate() method below

		"""
		import random

		self.mt = random.Random()
		if state and len(state) == 625:
			self.setstate(state)
		elif seed:
			self.mt.seed(seed)
		else:
			import time
			t = time.time()
			seed = int(1e6*(t-int(t)))
			self.mt.seed(seed)

	def getstate(self):
		"""Get signed/unsigned state vector for current generator state.

		:return: (array) state vector

		"""
		(rtype, seed, other) = self.mt.getstate()
		return seed

	def setstate(self, state):
		"""Restore generator to saved state.

		:param state: (array) state vector from getstate()

		:return: nothing

		"""
		self.mt.setstate((2, state, None))

	def rand(self, count=None):
		"""Generate random numbers.

		With no arguments generates a single floating point random
		number on the range [0-1]. If count is specified, then returns
		a list of count random numbers.

		:param count: (None or int) if not None, number of numbers to generate

		:return: (float) random floats on range [0-1]

		"""

		if count:
			return list(map(lambda x,s=self: s.mt.random(), [0] * int(count)))
		else:
			return self.mt.random()

def validate(exit=False):
	"""Valid Mersenne Twister engine.

	Check to see if python is still using the expected Mersenne Twister
	random number generator. This will almost certainly fail if anything
	changes..

	"""
	import sys

	r = MTRandom(seed=31415926)
	for n in range(10000):
		v = r.rand()
	if abs(v-0.603852477186) < 1e-12:
		return True
	else:
		if exit:
			sys.stderr.write('error - Mersenne Twister test failed!\n')
			sys.exit(1)
		else:
			return False

if __name__ == '__main__':
	import time, sys

	if validate():
		sys.stderr.write('Mersenne Twister: OK\n')
	else:
		sys.stderr.write('Mersenne Twister: INVALID!\n')
		sys.exit(1)

