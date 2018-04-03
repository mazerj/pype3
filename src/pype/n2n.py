#!/usr/bin/env pypenv
# -*- Mode: Python; tab-width: 4; py-indent-offset: 4; -*-

"""Numeric backward compatibility module

Interim Numeric-to-numpy conversion/compatibility module.
Import this instead of Numeric to aid migration to numpy.

"""


# warning: there's also a uniform() in pype_aux.py -- this will be masked
# warning: python has a native random module -- this will be masked
import numpy as np
from numpy.random import uniform, random
from numpy import newaxis as NEWAXIS
from numpy import ndarray as ARRAYTYPE
from numpy import int as INT
from numpy import float as FLOAT
from numpy import uint8 as UINT8
from numpy import int16 as INT16
from numpy import int32 as INT32
from numpy import float64 as FLOAT64

if 1:
	# for backward compat in old tasks only... will vanish eventually!!
	from numpy import float64 as Float64
	from numpy import uint8 as UnsignedInt8
