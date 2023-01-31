# ucsbcs154lab3
# All Rights Reserved
# Copyright (c) 2023 Regents of the University of California
# Distribution Prohibited

import pyrtl
import numpy as np
import struct
import math


# ==== Pyrtl functions ==== #

# counts the number of wires that come before the first 1
def count_zeros_from_end(x, start='msb'):
    if start not in ('msb', 'lsb'):
        raise pyrtl.PyrtlError('Invalid start parameter')

    def _count(x, found):
        end = x[-1] if start == 'msb' else x[0]
        is_zero = end == 0
        to_add = ~found & is_zero
        if len(x) == 1:
            return to_add
        else:
            rest = x[:-1] if start == 'msb' else x[1:]
            rest_to_add = _count(rest, found | ~is_zero)
            return to_add + rest_to_add
    return _count(x, pyrtl.as_wires(False))





# ==== Simulation Functions ==== #

# returns the bits of a float written into a string
def float_to_ieee_hp(n):
  return bin(np.float16(n).view('H'))[2:].zfill(16)

# returns a float given a binary string
def bin_to_float(binary):
    return struct.unpack('!f',struct.pack('!I', int(binary, 2)))[0]

# returns the sum of two float16s using the "round-to-zero" mode
def fp_add_truncate(a,b):
    if math.isnan(a) or math.isnan(b) or math.isinf(a) or math.isinf(b):
        return math.nan
    # force a and b to half-precision
    a = np.float16(a)
    b = np.float16(b)
    # perform double-precision addition
    a = np.float64(a)
    b = np.float64(b)
    out = a+b
    # get fractional and exponent part
    (fr,exp) = math.frexp(out)
    # get sign
    sign = fr<0
    fr = abs(fr)
    # chop off all but 10 bits of the sum
    mantissa = math.floor(fr * 2**11)
    new_fr = mantissa/(2**10)
    return np.float16( (-1 if sign else 1) * new_fr * 2**(exp-1) )

# returns true iff the float value will not be tested in the autograder
def not_tested(n):
  n = np.float16(n)
  # zero is tested
  if n==0:
    return False
  # not testing infinity, NaN, or denormalized values
  if math.isinf(n) or math.isnan(n) or (math.floor(math.log2(abs(n)))<-14):
    return True
  # testing everything else
  return False
