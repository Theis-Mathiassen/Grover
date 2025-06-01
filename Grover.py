import json
import math
import os
from dotenv import load_dotenv
from qiskit import *
import numpy as np
from qiskit_aer import AerSimulator
from qiskit.visualization import plot_histogram
from matplotlib import pyplot

# Load environment variables
output_dir = "./results"
use_local = False

if not os.path.exists(output_dir):
    os.makedirs(output_dir)

load_dotenv()


if use_local:
    # Setting a local simulator backend
    backend = AerSimulator ()
    optimization_level = 1
    num_shots = 1024

else:
    # Setup backend for azure 
    from azure.quantum import Workspace
    from azure.quantum.qiskit import AzureQuantumProvider
    workspace = Workspace(resource_id=os.environ['resource_id'], location=os.environ['location'])
    provider = AzureQuantumProvider(workspace)

    print("This workspace's targets:")
    for backend in provider.backends():
        print("- " + backend.name())
    backend = provider.get_backend('quantinuum.sim.h1-1sc')
    optimization_level = 3
    num_shots = 100



input_qubits = list(range(8))           # Qubits 0-7
classical_destination = list(range(8))  # classical bits 0-7
PHASE_ANC_INDEX = 13
OR_RESULT_ANC_INDEX = 14
known_solutions = False

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

    # The hash function
    # Gate 2
    circ.ccx(2, 3, 8)
    # Gate 3
    circ.ccx(4, 6, 9)

    # Ensure the first 3 bits are zero
    # Gate 0
    circ.x(0)
    # Gate 1
    circ.x(1)
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
    # Gate 1
    circ.x(1)
    # Gate 0
    circ.x(0)
    # Gate 3
    circ.ccx(4, 6, 9)
    # Gate 2
    circ.ccx(2, 3, 8)

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
    for i in input_qubits:
        circ.reset(i)
        circ.h(i)

    # Phase 2 perform t iterations of Grovers operation
    for j in range(t):
        for i in range(8, 13): circ.reset(i) # Reset ancillas 8,9,10,11 and output 12 for Z_f
        Z_f(circ)
        for i in input_qubits: circ.h(i)
        Z_or(circ)
        for i in input_qubits: circ.h(i)


    # Phase 3 Measure to get a candidate solution for the search
    circ.measure(input_qubits, classical_destination)


def classical_f (inputs):
    # The hash function
    gate2 = inputs[2] and  inputs[3]
    gate3 = inputs[4] and  inputs[6]
    # Ensure the first 3 bits are zero
    gate0 = not inputs[0]
    gate1 = not inputs[1]
    gate4 = gate0 and gate1
    gate5 = gate2 and gate3
    gate6 = gate5 and gate4
    return gate6


if known_solutions:
    circ = QuantumCircuit (15, len(input_qubits))
    # Optimal ~4 solutions in 8 qubits
    Grover(circ=circ, t=6)
    # Transpile circuit to work with the current backend .
    qc_compiled = transpile(circ, backend, optimization_level=optimization_level)
    # Run the job
    job = backend.run(qc_compiled, shots=num_shots)
    # Get the result
    result = job.result ()
    counts = result.get_counts(qc_compiled)

    circuit_diagram = circ.draw ('mpl')
    circuit_diagram.savefig(os.path.join(output_dir, "circuit_diagram.png")) # Save the circuit diagram to a file

    # Plot the result
    plot_histogram (counts)
    pyplot.savefig(os.path.join(output_dir, "histogram.png")) # Save the plot to a file
else:
    # Unknown number of solutions
    N = 2**len(input_qubits)
    current_t = 1.0
    max_t = (math.pi/4) * math.sqrt(N)
    growth_factor = 1.5
    candidates_t = []
    while (int(round(current_t)) < max_t):
        t_to_add = int(round(current_t))
        candidates_t.append(t_to_add)
        current_t *= growth_factor
        if int(round(current_t)) <= t_to_add : # Ensure progress if rounding stalls
            current_t = t_to_add + 1


    all_run_results = {}
    for t_value in candidates_t:
        print(f"\n--- Running Grover with t = {t_value} iterations ---")

        circ = QuantumCircuit (15, len(input_qubits))

        Grover(circ=circ, t=t_value)

        # Transpile circuit to work with the current backend .
        qc_compiled = transpile(circ, backend, optimization_level=optimization_level)
        # Run the job
        job = backend.run(qc_compiled, shots=num_shots)
        result = job.result()
        counts = result.get_counts(qc_compiled)

        all_run_results[f"t_{t_value}"] = counts
        print(f"Counts for t={t_value}: {counts}")

        # plot and save histogram for each t
        fig = plot_histogram(counts, title=f"Grover Results (Oracle: custom hash) for t={t_value}")
        pyplot.savefig(os.path.join(output_dir, f"histogram_t_{t_value}.png"))
        print(f"Histogram saved to histogram_t_{t_value}.png")
        pyplot.close(fig) # Close the figure to free memory
    
    # -- SAVING to JSON --
    json_filename = os.path.join(output_dir, "grover_all_run_results.json")
    try:
        with open(json_filename, 'w') as f_json:
            json.dump(all_run_results, f_json, indent=4) # indent for pretty printing
        print(f"\nResults saved to JSON file: {json_filename}")
    except IOError as e:
        print(f"Error saving to JSON: {e}")
