from qiskit import *
import numpy as np
from qiskit_aer import AerSimulator
from qiskit.visualization import plot_histogram
from matplotlib import pyplot
circ = QuantumCircuit (3)
circ.h(0)
circ.cx(0 , 1)
circ.cx(0 , 2)
circ.measure_all()
circuit_diagram = circ.draw ('mpl')
circuit_diagram.savefig("circuit_diagram.png") # Save the circuit diagram to a file
# Setting a backend
backend = AerSimulator ()

# Transpile circuit to work with the current backend .
qc_compiled = transpile( circ, backend )
# Run the job
# This will cause a pop where you have to authenticate with azure .
job_sim = backend.run( qc_compiled, shots =1024)
# Get the result
result_sim = job_sim.result ()
counts = result_sim.get_counts ( qc_compiled )
# Plot the result
plot_histogram ( counts )
pyplot.savefig("histogram.png") # Save the plot to a file