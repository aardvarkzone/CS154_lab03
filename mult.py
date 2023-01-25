import pyrtl

start = pyrtl.Input(bitwidth=1, name="start")
m = pyrtl.Input(bitwidth=4, name="m")
n = pyrtl.Input(bitwidth=4, name="n")

p = pyrtl.Output(bitwidth=4, name="p")

busy_reg = pyrtl.Register(bitwidth = 1, name = "busy_reg")
m_reg = pyrtl.Register(bitwidth=8, name = "m_reg")
n_reg = pyrtl.Register(bitwidth=4, name = "n_reg")
p_reg = pyrtl.Register(bitwidth=8, name = "p_reg")

complete = pyrtl.WireVector(bitwidth=1, name = "complete")
write_p = pyrtl.WireVector(bitwidth=1, name = "write_p")

with pyrtl.conditional_assignment:
    with (start == 1) & (busy_reg == 0):
        m_reg.next |= m
        n_reg.next |= n
        busy_reg.next |= 1
        p |= 0
    with (busy_reg == 1):
        with (m_reg == 0):
            complete |= 1
            write_p |= 0
            busy_reg.next |= 0
            p |= p_reg
        with (m_reg != 0):
            write_p |= n_reg[0]
            n_reg.next |= pyrtl.corecircuits.shift_right_arithmetic(n_reg, 1)
            m_reg.next |= pyrtl.corecircuits.shift_left_arithmetic(m_reg, 1)
            p |= 0

with pyrtl.conditional_assignment:
    with write_p == 1:
        p_reg.next |= p_reg + m_reg

simvals = {
    'start':    [1,0,0,0,0,0,0,0,0,0],
    'm':        [3,0,0,0,0,0,0,0,0,0],
    'n':        [5,0,0,0,0,0,0,0,0,0]
}

# Simulate and test your "alu" design
sim_trace = pyrtl.SimulationTrace()
sim = pyrtl.Simulation(tracer=sim_trace)
for cycle in range(10):
    sim.step({
        'start' : int(simvals['start'][cycle]),
        'm' : int(simvals['m'][cycle]),
        'n': int(simvals['n'][cycle])
        }) 
sim_trace.render_trace()
