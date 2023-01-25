import pyrtl
import util

# Inputs
a = pyrtl.Input(bitwidth=16, name='A')
b = pyrtl.Input(bitwidth=16, name='B')

# Outputs
c = pyrtl.Output(bitwidth=16, name='C')

'''   Declare all necessary Registers and WireVectors   '''

# Hint 1: You will want to split inputs into useful components


# Hint 2: The sum will take one cycle to compute. Be sure to write your result to the
# .next value of a register.


# Additional regs/wires ...


'''       End of Register/WireVector declarations       '''

# Step 1: Split up inputs A and B into useful components


# Step 2: Find maximum exponent. This will help you normalize the mantissas


# Step 3: Compose the mantissas.
# a. The IEEE standard assumses an implicit "1". Prepend the mantissas with a "1".
#    Hint: If both the mantissa and exponent are 0, then the given input is 0, so
#    We DONT want to prepend a "1"
#    https://pyrtl.readthedocs.io/en/latest/helpers.html#pyrtl.corecircuits.concat
#
# b. In the worst case, one of the mantissas must be shifted right 30 times. Append
#    30 zeros to your mantissa so we don't lose precision

# Step 4: Normalize the mantissas
# - Use the maximum exponent to determine which mantissa has to be shifted and shift
#   it right (max_exponent - min_exponent) times.


# Step 5: Compute the sum of the mantissas. Be sure to use the correct sign of A and B
# in the calculation. To do that, apply the signs to A and B’s normalized mantissas
# and put those values in two new 42-bit wires. Then, sum those values to get a
# 43-bit signed wire.

# Step 6: Record the sign of the sum into C
# Hint: You may want to handle two different cases: (1) A and B have the same sign
# and (2) A and B have opposite signs, as this may affect your results for steps 7
# and 8

# Step 7: Calculate absolute value of sum from the previous step

# Step 8: Normalize C's mantissa. Determine how many times to shift the mantissa left
# so that the MSB is 1

# Step 9: Determine C's mantissa by using result from Step 9

# Step 10: If mantissa was shifted in Step 9, this must be accounted for in the
# result's exponent as well.

# Step 11: Produce output C. Concatenate your results for the output's sign, exponent,
# and mantissa components. Note that you may have to select only a limited set of bits
# from the sign, exponent, and fractional part WireVectors that you have in use.


# Careful: Make sure your implementation handles the case where C = 0.0



############################## SIMULATION ######################################

# Inputs to test
a_inputs = [-1.0, 0, 6.326687285936606, 1.0, -1.0]
b_inputs = [1.125, 0, 2.975162439552353, 0.125, -0.125]
# This is not an exhaustive list of inputs. The autograder will test against more inputs.
assert(len(a_inputs) == len(b_inputs))



# Generate expected results
expected_results = []
for i in range(len(a_inputs)):
  expected_results.append(util.fp_add_truncate(a_inputs[i],b_inputs[i]))



# Run simulation using specified inputs
sim_trace = pyrtl.SimulationTrace()
sim = pyrtl.Simulation(tracer=sim_trace)
for i in range(len(a_inputs)):
  for j in range(2):
    sim.step({
      'A':int(util.float_to_ieee_hp(a_inputs[i]), base=2),
      'B':int(util.float_to_ieee_hp(b_inputs[i]), base=2),
    })



# Print trace
sim_trace.render_trace()



# Verify results against expected results
passed = True
num_tests_ran = 0
for i in range(len(expected_results)):
  # if input or expected result is invalid
  if util.not_tested(expected_results[i]):
    print(" {} will not be tested. Skipping test...".format(expected_results[i]))
    continue
  if util.not_tested(a_inputs[i]):
    print(" {} will not be tested. Skipping test...".format(a_inputs[i]))
    continue
  if util.not_tested(b_inputs[i]):
    print(" {} will not be tested. Skipping test...".format(b_inputs[i]))
    continue
  # if output matched expected result
  if util.float_to_ieee_hp(expected_results[i]) == bin(sim_trace.trace['C'][i*2 + 1])[2:].zfill(16):
    print("Passed case:", util.float_to_ieee_hp(a_inputs[i]), "+", util.float_to_ieee_hp(b_inputs[i]), "=", util.float_to_ieee_hp(expected_results[i]))
    pass
  else:
    passed = False
    print("Failed case:", util.float_to_ieee_hp(a_inputs[i]), "+", util.float_to_ieee_hp(b_inputs[i]))
    print(" expected :", util.float_to_ieee_hp(expected_results[i]))
    print(" actual   :", bin(sim_trace.trace['C'][i*2 + 1])[2:].zfill(16))
    print()
  num_tests_ran += 1

if passed:
  print("All {} test cases passed!".format(num_tests_ran))
else:
  print("Some test cases failed.")
