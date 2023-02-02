# ucsbcs154lab3
# All Rights Reserved
# Copyright (c) 2023 Regents of the University of California
# Distribution Prohibited

import pyrtl
import ucsbcs154lab3_util as util

# Inputs
a = pyrtl.Input(bitwidth=16, name='A')
b = pyrtl.Input(bitwidth=16, name='B')

# Outputs
c = pyrtl.Output(bitwidth=16, name='C')

# ---   Declare all necessary Registers and WireVectors   ---
# Hint 1: You will want to split inputs into useful components
# Hint 2: The sum will take one cycle to compute. Be sure to write your result to the
# .next value of a register.

a_sign = pyrtl.WireVector(bitwidth=1, name='A_sign')
a_exp = pyrtl.WireVector(bitwidth=5, name='A_exp')
a_significand = pyrtl.WireVector(bitwidth=10, name='A_significand')
a_mant = pyrtl.WireVector(bitwidth=41, name='A_mantissa')
a_norm_mant = pyrtl.WireVector(bitwidth=41, name='A_normalized_mantissa')
a_signed_mant = pyrtl.WireVector(bitwidth=42, name='A_signed_normalized_mantissa')

b_sign = pyrtl.WireVector(bitwidth=1, name='B_sign')
b_exp = pyrtl.WireVector(bitwidth=5, name='B_exp')
b_significand = pyrtl.WireVector(bitwidth=10, name='B_significand')
b_mant = pyrtl.WireVector(bitwidth=41, name='B_mantissa')
b_norm_mant = pyrtl.WireVector(bitwidth=41, name='B_normalized_mantissa')
b_signed_mant = pyrtl.WireVector(bitwidth=42, name='B_signed_normalized_mantissa')

# Additional regs/wires ...
max_exp = pyrtl.WireVector(bitwidth=5, name='max_exp')
shifter = pyrtl.WireVector(bitwidth=42, name='shifter')
sum_43 = pyrtl.WireVector(bitwidth=43, name='43_bit_sum')
sum_abs = pyrtl.WireVector(bitwidth=42, name='sum_abs')
sum_abs_norm = pyrtl.WireVector(bitwidth=42, name='sum_abs_normalized')
sum_abs_register = pyrtl.Register(bitwidth=42, name='sum_abs_register')
c_mant = pyrtl.WireVector(bitwidth=10, name='C_mantissa')
c_sign = pyrtl.WireVector(bitwidth=1, name='C_sign')
c_sign_register = pyrtl.Register(bitwidth=1, name='c_sign_register')
c_exp_register = pyrtl.Register(bitwidth=5, name='c_exp_register')
c_exp_final = pyrtl.WireVector(bitwidth=5, name='c_exp_final')
one = pyrtl.WireVector(bitwidth=1,name='one')
thirty = pyrtl.WireVector(bitwidth=30,name='thirty')
output = pyrtl.Register(bitwidth=16, name="output")

# ---       End of Register/WireVector declarations       ---

# Step 1: Split up inputs A and B into useful components
# use big endian 
a_sign <<= a[15]
a_exp <<= a[10:15]
a_significand <<= a[0:10]
b_sign <<= b[15]
b_exp <<= b[10:15]
b_significand <<= b[0:10]

# Step 2: Find maximum exponent. This will help you normalize the mantissas
with pyrtl.conditional_assignment:
  with (a_exp > b_exp):
    max_exp |= a_exp
  with pyrtl.otherwise:
    max_exp |= b_exp

# Step 3: Compose the mantissas.
# a. The IEEE standard assumses an implicit "1". Prepend the mantissas with a "1".
#    Hint: If both the mantissa and exponent are 0, then the given input is 0, so
#    We DONT want to prepend a "1"
#    https://pyrtl.readthedocs.io/en/latest/helpers.html#pyrtl.corecircuits.concat
#
# b. In the worst case, one of the mantissas must be shifted right 30 times. Append
#    30 zeros to your mantissa so we don't lose precision

one <<= 1
thirty <<= 0

with pyrtl.conditional_assignment:
  with a_exp != 0:
    with a_significand != 0: 
      a_mant |= pyrtl.concat(one, a_significand, thirty)
    with a_significand == 0: 
      a_mant |= pyrtl.concat(one, a_significand, thirty)
  with a_exp == 0:
    with a_significand != 0: 
      a_mant |= pyrtl.concat(one, a_significand, thirty)
    with a_significand == 0: 
      a_mant |= 0

with pyrtl.conditional_assignment:
  with b_exp != 0:
    with b_significand != 0: 
      b_mant |= pyrtl.concat(one, b_significand, thirty)
    with b_significand == 0:
      b_mant |= pyrtl.concat(one, b_significand, thirty)
  with b_exp == 0: 
    with b_significand != 0:
      b_mant |= pyrtl.concat(one, b_significand, thirty)
    with b_significand == 0: 
      b_mant |= 0

# Step 4: Normalize the mantissas
# - Use the maximum exponent to determine which mantissa has to be shifted and shift
#   it right (max_exponent - min_exponent) times.

a_norm_mant <<= pyrtl.shift_right_logical(a_mant, max_exp - a_exp)
b_norm_mant <<= pyrtl.shift_right_logical(b_mant, max_exp - b_exp)

# Step 5: Compute the sum of the mantissas. Be sure to use the correct sign of A and B
# in the calculation. To do that, apply the signs to A and B’s normalized mantissas
# and put those values in two new 42-bit wires. Then, sum those values to get a
# 43-bit signed wire.

with pyrtl.conditional_assignment:
  with a_sign == 0:
    a_signed_mant |= a_norm_mant
  with pyrtl.otherwise: 
    a_signed_mant |= ~a_norm_mant + 1

with pyrtl.conditional_assignment:
  with b_sign == 0:
    b_signed_mant |= b_norm_mant
  with pyrtl.otherwise: 
    b_signed_mant |= ~b_norm_mant + 1 

sum_43 <<= a_signed_mant + b_signed_mant

# Step 6: Record the sign of the sum into C
# Hint: You may want to handle two different cases: (1) A and B have the same sign
# and (2) A and B have opposite signs, as this may affect your results for steps 7
# and 8

with pyrtl.conditional_assignment:
  with a_sign == b_sign:
    # same sign, you don't need to worry about overflow, just take a_sign
    c_sign_register.next |= a_sign    
  with pyrtl.otherwise: 
    # different signs or no overflow
    c_sign_register.next |= ~sum_43[-2]
      
# Step 7: Calculate absolute value of sum from the previous step

# Get the absolute value of the sum (this will form the mantissa of your result). 
# We do this because the value stored in the mantissa is unsigned.

# (1) same signs --> check overflow bit
# (2) different signs --> remove overflow bit, shift sum left by 1

with pyrtl.conditional_assignment: 
  with a_sign == b_sign: 
    with a_sign == 1: 
      sum_abs |= ~sum_43[0:42] + 1
    with a_sign == 0: 
      sum_abs |= sum_43[0:42]
  with a_sign != b_sign: 
    with sum_43[-2] == 0:
      sum_abs |= ~sum_43[0:42] + 1
      #sum_abs |= sum_43[0:42]
    with sum_43[-2] == 1:
      sum_abs |= sum_43[0:42]
      #sum_abs |= ~sum_43[0:42] + 1

# Step 8: Normalize C's mantissa. Determine how many times to shift the mantissa left
# so that the MSB is 1

with pyrtl.conditional_assignment: 
  with a_sign == b_sign:
    with sum_abs[-1] == 0:
      sum_abs_register.next |= pyrtl.shift_left_logical(sum_abs, 1)
    with sum_abs[-1] == 1:
      sum_abs_register.next |= sum_abs
  with a_sign != b_sign:
    sum_abs_register.next |= pyrtl.shift_left_logical(sum_abs, 1)

#util.count_zeros_from_end() from util 
shifter <<= util.count_zeros_from_end(sum_abs_register) 
sum_abs_norm <<= pyrtl.shift_left_logical(sum_abs_register, shifter)

# Step 9: Determine C's mantissa by using result from Step 8
with pyrtl.conditional_assignment:
  with sum_abs == 0:
    c_mant |= 0
  with pyrtl.otherwise:
    c_mant |= sum_abs_norm[31:]

# Step 10: If mantissa was shifted in Step 9, this must be accounted for in the
# result's exponent as well.
# Use the number of times a shift was performed as well as the initial values of 
# the exponent parts to find the exponent part for C.
# (1) if the signs are different, use max exponent 
# (2) if the signs are same, account for overflow by adding OV bit to abs of max exponent

with pyrtl.conditional_assignment:
  with sum_abs_register == 0: 
    c_sign |= 0
    c_exp_final |= 0
  with sum_abs_register != 0: 
    c_sign |= c_sign_register
    c_exp_final |= c_exp_register - shifter

with pyrtl.conditional_assignment: 
  with a_sign != b_sign:
    c_exp_register.next |= max_exp 
  with a_sign == b_sign:
    c_exp_register.next |= max_exp + sum_abs[-1]

  # with (max_exp[-1] == 0):
    # c_exp |= (sum_abs_norm[41] + max_exp)
  # with (max_exp[-1] == 1):
    # c_exp |= (sum_abs_norm[41] + ~(max_exp) + 1)
    

# Step 11: Produce output C. Concatenate your results for the output's sign, exponent,
# and mantissa components. Note that you may have to select only a limited set of bits
# from the sign, exponent, and fractional part WireVectors that you have in use.

# Careful: Make sure your implementation handles the case where C = 0.0
output.next <<= pyrtl.concat(c_sign, c_exp_final, c_mant)
c <<= pyrtl.concat(c_sign, c_exp_final, c_mant)

############################## SIMULATION ######################################

# Inputs to test
a_inputs = [-1.0, 0, 6.326687285936606, 1.0, -1.0, 1.0]
b_inputs = [1.125, 0, 2.975162439552353, 0.125, -0.125, -1.0]
# This is not an exhaustive list of inputs. The autograder will test against more inputs.
assert(len(a_inputs) == len(b_inputs))

# Generate expected results
expected_results = []
for i in range(len(a_inputs)):
  expected_results.append(util.fp_add_truncate(a_inputs[i],b_inputs[i]))

# Run simulation using specified inputs
# Note: The design must be a 2-stage pipeline.
#       So it should receive new input every cycle.
sim_trace = pyrtl.SimulationTrace()
sim = pyrtl.Simulation(tracer=sim_trace)
for i in range(len(a_inputs)):
  sim.step({
    'A':int(util.float_to_ieee_hp(a_inputs[i]), base=2),
    'B':int(util.float_to_ieee_hp(b_inputs[i]), base=2),
  })



# Print trace
sim_trace.render_trace()



# Verify results against expected results
passed = True
num_tests_ran = 0
for i in range(1, len(a_inputs)):
  # if input or expected result is invalid
  if util.not_tested(expected_results[i - 1]):
    print(" {} will not be tested. Skipping test...".format(expected_results[i - 1]))
    continue
  if util.not_tested(a_inputs[i - 1]):
    print(" {} will not be tested. Skipping test...".format(a_inputs[i - 1]))
    continue
  if util.not_tested(b_inputs[i - 1]):
    print(" {} will not be tested. Skipping test...".format(b_inputs[i - 1]))
    continue
  # if output matched expected result
  if util.float_to_ieee_hp(expected_results[i - 1]) == bin(sim_trace.trace['C'][i])[2:].zfill(16):
    print("Passed case:", util.float_to_ieee_hp(a_inputs[i - 1]), "+", util.float_to_ieee_hp(b_inputs[i - 1]), "=", util.float_to_ieee_hp(expected_results[i - 1]))
    pass
  else:
    passed = False
    print("Failed case:", util.float_to_ieee_hp(a_inputs[i - 1]), "+", util.float_to_ieee_hp(b_inputs[i - 1]))
    print(" expected :", util.float_to_ieee_hp(expected_results[i - 1]))
    print(" actual   :", bin(sim_trace.trace['C'][i])[2:].zfill(16))
    print()
  num_tests_ran += 1

if passed:
  print("All {} test cases passed!".format(num_tests_ran))
else:
  print("Some test cases failed.")
