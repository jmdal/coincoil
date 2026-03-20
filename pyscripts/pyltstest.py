import PyLTSpice

sim = PyLTSpice.SimRunner(output_folder="./output",simulator="D:\\ProgramFiles\\LTspice\\LTspice.exe")

net = PyLTSpice.SpiceEditor("../ltspice/coilgunauto.asc")

net.set_parameters(mu0="1257n", slen=0.04, turns=100, cdia=39.68e-3, cres=103.5754e-3, coil=1554.4203e-6)
raw, log = sim.run_now(net)

data = PyLTSpice.LTSpiceLogReader(log)

print(data.step_count)

print(data["current"][0])