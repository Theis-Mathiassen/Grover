from qiskit import *
import numpy as np
from qiskit_aer import AerSimulator
from qiskit.visualization import plot_histogram
from matplotlib import pyplot

input_qubits = list(range(8))           # Qubits 0-7
classical_destination = list(range(8))  # classical bits 0-7
PHASE_ANC_INDEX = 13
OR_RESULT_ANC_INDEX = 14

def compute_OR_fx (circ):
    """Computes OR of input_indices into or_result_anc_idx.
       Assumes or_result_anc_idx is |0> initially.
       Input qubits are restored to their original state by this function.
    """
    # Apply X to all input qubits (to get NOT x_i)
    for i in input_qubits:
        circ.x(i)
    
    # Target is ORPHASE_ANC_INDEX. It now holds AND(NOT x_i).
    circ.mcx(input_qubits, OR_RESULT_ANC_INDEX)

    # Apply X to all input qubits again to restore them to their original state
    for i in input_qubits:
        circ.x(i)
    
    # Apply X to it to get NOT(AND(NOT x_i)) = OR(x_i).
    circ.x(OR_RESULT_ANC_INDEX)

def uncompute_OR_fx(circ):
    """Uncomputes OR_fx. Returns or_result_anc_idx to |0>."""
    # Inverse of compute_OR_fx applied in reverse order
    circ.x(OR_RESULT_ANC_INDEX) # Reverse the final X

    for i in input_qubits: # Reverse the restoration Xs
        circ.x(i)
    
    circ.mcx(input_qubits, OR_RESULT_ANC_INDEX) # Reverse the MCX

    for i in input_qubits: # Reverse the initial Xs
        circ.x(i)

def Z_or (circ):
    """Implements the Z_OR gate acting on INPUT_QUBIT_INDICES."""
    
    # --- Part 1: Compute OR(X) into OR_RESULT_ANC_INDEX ---
    # Ensure OR_RESULT_ANC_INDEX is |0> before computation
    circ.reset(OR_RESULT_ANC_INDEX)
    compute_OR_fx(circ)

    # --- Part 2: Phase Kickback ---
    # Ensure PHASE_ANC_INDEX is |0> before preparing for kickback
    circ.reset(PHASE_ANC_INDEX)
    # Prepare for kickback into |->
    circ.x(PHASE_ANC_INDEX)
    circ.h(PHASE_ANC_INDEX)

    # CNOT from OR_RESULT_ANC_INDEX to PHASE_ANC_INDEX
    circ.cx(OR_RESULT_ANC_INDEX, PHASE_ANC_INDEX)

    # --- Part 3: Uncompute OR(X) ---
    uncompute_OR_fx(circ)
    
    # --- Part 4: Clean up PHASE_ANC_INDEX ---
    # Return PHASE_ANC_INDEX from |-> basis back to |0>
    circ.h(PHASE_ANC_INDEX)
    circ.x(PHASE_ANC_INDEX)
    circ.reset(PHASE_ANC_INDEX)

    circ.barrier()

#def oracle (circ):
def compute_fx(circ):
    ####    Oracle    ####

    # Your provided oracle code performs the forward computation.
    # Note: Resets are for initialization before this block, not part of the unitary.
    # circ.reset(8) # These should be done *before* the Grover oracle block if ancillas are reused.
    # circ.reset(9)
    # circ.reset(10)
    # circ.reset(11)
    # circ.reset(12)

    # Gate 0
    circ.x(0)
    # Gate 1
    circ.x(1)
    # Gate 2
    circ.ccx(2, 3, 8)
    # Gate 3
    circ.ccx(4, 6, 9)
    # Gate 4
    circ.ccx(0,1,10)
    # Gate 5
    circ.ccx(8,9,11)
    # Gate 6
    circ.ccx(10,11,12)
    
def uncompute_fx(circ):
    # Gate 6
    circ.ccx(10,11,12)
    # Gate 5
    circ.ccx(8,9,11)
    # Gate 4
    circ.ccx(0,1,10)
    # Gate 3
    circ.ccx(4, 6, 9)
    # Gate 2
    circ.ccx(2, 3, 8)
    # Gate 1
    circ.x(1)
    # Gate 0
    circ.x(0)

def Z_f (circ):
    compute_fx(circ)


    # Prepare Phase Kickback Ancilla to |->
    circ.x(PHASE_ANC_INDEX)
    circ.h(PHASE_ANC_INDEX)

    circ.cx(12, PHASE_ANC_INDEX)

    uncompute_fx(circ)

    # Return PHASE_ANC_INDEX from |-> basis back to |0>
    circ.h(PHASE_ANC_INDEX)
    circ.x(PHASE_ANC_INDEX)
    # Optionally, if you want to be absolutely sure it's |0> for other potential uses
    circ.reset(PHASE_ANC_INDEX) 

    circ.barrier() # Good practice to separate logical blocks

def Grover (circ, t):

    # Phase 1 prepare all qubits in a super position
    for i in input_qubits: circ.h(i)

    # Phase 2 perform t iterations of Grovers operation
    for j in range(t):
        for i in range(8, 13): circ.reset(i) # Reset ancillas 8,9,10,11 and output 12 for Z_f
        Z_f(circ)
        for i in input_qubits: circ.h(i)
        compute_OR_fx(circ)
        for i in input_qubits: circ.h(i)


    # Phase 3 
    circ.measure(input_qubits, classical_destination)


"""
Truth table ccx as and with ancilla being 0:
a   b   ancilla a   b   result
0	0	0		0	0	0
0	1	0		0	1	0
1	0	0		1	0	0
1	1	0		1	1	1
"""

circ = QuantumCircuit (15, len(input_qubits))

# For testing, assign some qubits to |1>
#circ.x(2)
#circ.x(3)
#circ.x(4)
#circ.x(6)

Grover(circ=circ, t=5)

circuit_diagram = circ.draw ('mpl')
circuit_diagram.savefig("circuit_diagram.png") # Save the circuit diagram to a file

# Setting a backend
backend = AerSimulator ()

# Transpile circuit to work with the current backend .
qc_compiled = transpile(circ, backend)
# Run the job
# This will cause a pop where you have to authenticate with azure .
job_sim = backend.run(qc_compiled, shots=1024)
# Get the result
result_sim = job_sim.result ()
counts = result_sim.get_counts (qc_compiled)

selected_results = {}
threshold = 20 # Define your threshold

for bitstring, num_occurrences in counts.items():
    # bitstring will be like '11001011'
    # num_occurrences will be its corresponding value, e.g., 1
    if num_occurrences > threshold:
        selected_results[bitstring] = num_occurrences

# Plot the result
plot_histogram (counts)
#plot_histogram(selected_results, title=f"Selected Results (Count > {threshold})")
pyplot.savefig("histogram.png") # Save the plot to a file