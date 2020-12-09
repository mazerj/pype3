# -*- Mode: Python; tab-width: 4; py-indent-offset: 4; -*-

"""Useful tools for implementing tasks

Author -- James A. Mazer (mazerj@gmail.com)

"""

import numpy as np

class CondBlock(object):
    """Class for managing a list of conditions.

    The idea is that you instantiate a CondBlock and fill it
    with conditions and then call pick() method to get the
    next condition and pop it off the list of conditions
    with the pop() method.  Takes care of randomizing
    each time through the block.

    Conditions can be anything you like that tells the task
    how to implement the current trial - list or dict
    of parmaters etc.

    """
    
	def __init__(self, randomize=True):
        self._randomize = randomize
		self._available = []
		self._nblocks = 0

        # task must fill conds after instantiation
		self.conds = []

	def shuffle(self, reset=True):
		"""Shuffle (re-randomize) the block.

		Shuffle conditions. If `reset` is true, then refill
        the list of available conditions first. If you want to
        have error trials get put back into the mix, the call
        shuffle() after an error with `reset=False` instead of
        pop().

        This automatically gets called first time task calls
        pick().

		"""
        
		if reset:
			self._available = range(len(self.conds))
        if self._randomize:
            # np.random.shuffle does in-place shuffle
            np.random.shuffle(self._available)

	def pick(self):
		"""Get next condition.

        If no more conditions are available, reshuffle and then
        return condition. Note that this doesn't remove the
        condition from the table -- you need to call pop() to
        actually consume the condition.

		"""
		if len(self._available) == 0:
			self.shuffle()
			self._nblocks += 1
		return self.conds[self._available[-1]]

	def pop(self):
		"""Consume current condition (for use after correct trial).

        Returns the number of available conditions left in the block.

		"""
		self._available.pop()
        return len(self._available)

	def statestr(self):
		return '%d/%d conds; %d blocks' % \
			   (len(self._available), len(self.conds), self._nblocks,)
