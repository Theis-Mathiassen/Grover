import math
from qiskit import QuantumCircuit
from qiskit.quantum_info import Statevector
from qiskit.visualization import plot_bloch_multivector
from qiskit_aer import AerSimulator
from matplotlib import pyplot
 
qc = QuantumCircuit(2)
qc.x(0)
qc.h(0)
#qc.x(0)
qc.h(1)
qc.p(math.pi/2, 1) # Apply a phase gate (P-gate) with an angle of pi/2 (1.57 radians) to qubit 0


#qc.cx(1, 0)



qc.remove_final_measurements()  # no measurements allowed
statevector = Statevector(qc)

# Backend for statevector simulation
sv_simulator = AerSimulator(method='statevector') # Specify statevector method for clarity

job_sv = sv_simulator.run(qc)

# Execute and get statevector
result_sv = job_sv.result()


# Interpret and print the statevector
alpha = statevector[0] # Amplitude for |0>
beta = statevector[1]  # Amplitude for |1>

print(f"Statevector: {statevector}")
print(f"Alpha (amplitude of |0>): {alpha:.3f}") # Using .3f for cleaner printing
print(f"Beta (amplitude of |1>): {beta:.3f}")
print(f"Qubit state: ({alpha:.3f})|0> + ({beta:.3f})|1>")

plot_bloch_multivector(statevector) # Pass the actual statevector
pyplot.savefig("bloch_sphere_from_statevector.png")
pyplot.clf() # Clear the figure for the next plot if any

# Draw the circuit with measurements
#print("\nCircuit with measurements:")
#print(circ_for_measurement.draw(output='text'))
circuit_diagram = qc.draw('mpl')
circuit_diagram.savefig("circuit_diagram.png")
pyplot.clf()