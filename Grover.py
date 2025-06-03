import json
import math
import os
from dotenv import load_dotenv
from qiskit import QuantumCircuit, transpile, ClassicalRegister, QuantumRegister
import numpy as np
from qiskit_aer import AerSimulator
from qiskit.visualization import plot_histogram
from matplotlib import pyplot # pyplot imported for saving figures

# --- Configuration ---
# Load environment variables from .env file for Azure Quantum
load_dotenv()

# Directory to save results
output_dir = "./results"
if not os.path.exists(output_dir):
    os.makedirs(output_dir)

# --- Backend Selection ---
# Set to False to use Azure Quantum, True for local AerSimulator
use_local = True

if use_local:
    # Setting a local AER simulator backend
    backend = AerSimulator()
    optimization_level = 1
    # Number of times to run the circuit
    num_shots = 1024
else:
    # Setup backend for Azure Quantum
    print("Attempting to connect to Azure Quantum backend.")
    from azure.quantum import Workspace
    from azure.quantum.qiskit import AzureQuantumProvider

    # Ensure these environment variables are set in your .env file or system
    resource_id = os.environ.get('resource_id')
    location = os.environ.get('location')

    if not resource_id or not location:
        raise ValueError("Azure Quantum resource_id or location not found in environment variables.")

    workspace = Workspace(resource_id=resource_id, location=location)
    provider = AzureQuantumProvider(workspace)

    print("Available Azure Quantum backends:")
    for backend in provider.backends():
        print("- " + backend.name())
    backend = provider.get_backend('quantinuum.sim.h1-1sc')
    optimization_level = 3
    num_shots = 100


# --- Circuit configuration ---
input_qubits = list(range(8))           # Qubits 0-7
classical_destination = list(range(8))  # classical bits 0-7
PHASE_ANC_INDEX = 13
OR_RESULT_ANC_INDEX = 14
F_RESULT_ANC_INDEX = 12
# Whether or not to pretend to know the number of solutions
known_solutions = False


# --- Helper functions ---

def compute_OR_fx (circ):
    """Computes OR of input_indices into or_result_anc_idx.
       Assumes or_result_anc_idx is |0> initially.
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
    compute_OR_fx(circ)

    # --- Part 2: Phase Kickback ---
    # Prepare for kickback into |->
    circ.x(PHASE_ANC_INDEX)
    circ.h(PHASE_ANC_INDEX)

    # CNOT from OR_RESULT_ANC_INDEX to PHASE_ANC_INDEX
    circ.cx(OR_RESULT_ANC_INDEX, PHASE_ANC_INDEX)

    # --- Part 3: Uncompute OR(X) ---
    #Input qubits are restored to their original state by this function.
    uncompute_OR_fx(circ)
    
    # --- Part 4: Clean up PHASE_ANC_INDEX ---
    # Return PHASE_ANC_INDEX from |-> basis back to |0>
    circ.h(PHASE_ANC_INDEX)
    circ.x(PHASE_ANC_INDEX)

    circ.barrier()


def compute_fx(circ):
    """Computes f of input_indices into F_RESULT_ANC_INDEX.
       Assumes F_RESULT_ANC_INDEX is |0> initially.
    """
    ####    Oracle    ####

    # The hash function
    # Gate 2
    circ.ccx(2, 3, 8)
    # Gate 3
    circ.ccx(4, 6, 9)
    # Gate 5
    circ.ccx(8,9,11)

    # Ensure the first 3 bits are zero
    # Gate 0
    circ.x(0)
    # Gate 1
    circ.x(1)
    # Gate 4
    circ.ccx(0,1,10)
    # Gate 6
    circ.ccx(10,11,F_RESULT_ANC_INDEX)
    
def uncompute_fx(circ):
    """Uncomputes fx. Returns F_RESULT_ANC_INDEX to |0>.
       Input qubits are restored to their original state by this function."""
    
    # Gate 6
    circ.ccx(10,11,F_RESULT_ANC_INDEX)
    # Gate 4
    circ.ccx(0,1,10)
    # Gate 1
    circ.x(1)
    # Gate 0
    circ.x(0)
    # Gate 5
    circ.ccx(8,9,11)
    # Gate 3
    circ.ccx(4, 6, 9)
    # Gate 2
    circ.ccx(2, 3, 8)

def Z_f (circ):
    """Implements the Z_f gate acting on INPUT_QUBIT_INDICES.
       Marks states where f(x)=1 with a phase kickback."""
    
    compute_fx(circ)


    # Prepare Phase Kickback Ancilla to |->
    circ.x(PHASE_ANC_INDEX)
    circ.h(PHASE_ANC_INDEX)

    circ.cx(F_RESULT_ANC_INDEX, PHASE_ANC_INDEX)

    #Input qubits are restored to their original state by this function.
    uncompute_fx(circ)

    # Return PHASE_ANC_INDEX from |-> basis back to |0>
    circ.h(PHASE_ANC_INDEX)
    circ.x(PHASE_ANC_INDEX)

    circ.barrier() # Good practice to separate logical blocks


# --- Grover operation ---

def Grover (circ, t):
    """
    Constructs the Grover's algorithm circuit.
    t: The number of Grover iterations to perform.
    """

    # Step 1 prepare all qubits in a super position
    for i in input_qubits:
        circ.h(i)
    circ.barrier() # Good practice to separate logical blocks

    # Step 2 perform t iterations of Grovers operation
    for j in range(t):
        for i in range(8, 13): circ.reset(i) # Reset ancillas 8,9,10,11 and output F_RESULT_ANC_INDEX for Z_f
        Z_f(circ)
        for i in input_qubits: circ.h(i)
        circ.barrier() # Good practice to separate logical blocks
        Z_or(circ)
        for i in input_qubits: circ.h(i)
        circ.barrier() # Good practice to separate logical blocks


    # Step 3 Measure to get a candidate solution for the search
    circ.measure(input_qubits, classical_destination)



# --- Main ---

if __name__ == "__main__":
    # Main execution block

    if known_solutions:
        # --- KNOWN SOLUTIONS MODE ---
        # Assumes the number of solutions 's' is known, allowing for optimal 't' calculation.
        
        # Initialize quantum circuit: 15 total qubits, 8 classical bits for output.
        circ = QuantumCircuit(15, len(input_qubits))
        
        # Optimal iterations 't' for 4 solutions in 2^8 search space.
        # t = round( (pi/4) * sqrt(N/s) ) = round( (pi/4) * sqrt(256/4) ) ~ 6.
        Grover(circ=circ, t=6)
        
        # Transpile for selected backend and optimization level.
        qc_compiled = transpile(circ, backend, optimization_level=optimization_level)
        
        # Execute the circuit 'num_shots' times.
        job = backend.run(qc_compiled, shots=num_shots)
        result = job.result() # Get execution results.
        counts = result.get_counts(qc_compiled) # Get measurement counts.

        # --- Save Circuit Diagram & Histogram ---
        circuit_diagram = circ.draw('mpl') # Generate circuit diagram.
        circuit_diagram.savefig(os.path.join(output_dir, "circuit_diagram.png")) # Save diagram.

        plot_histogram(counts) # Plot measurement histogram.
        pyplot.savefig(os.path.join(output_dir, "histogram.png")) # Save histogram.
        pyplot.close() # Close plot to free memory.

    else:
        # --- UNKNOWN SOLUTIONS MODE ---
        # Used when 's' is unknown; iterates through different 't' values.
        
        N = 2**len(input_qubits) # Total items in search space.
        current_t = 1.0 # Initial number of iterations.
        # Heuristic maximum for t, roughly pi/4 * sqrt(N) if s=1.
        max_t = (math.pi/4) * math.sqrt(N) 
        growth_factor = 1.5 # Factor to increase 't' in each step.
        candidates_t = [] # List to store 't' values to test.

        # Generate a sequence of 't' values, increasing exponentially.
        while (int(round(current_t)) < max_t):
            t_to_add = int(round(current_t)) # Round to nearest integer.
            if t_to_add not in candidates_t and t_to_add > 0 : # Avoid duplicates and t=0
                 candidates_t.append(t_to_add)
            current_t *= growth_factor # Increase 't'.
            if int(round(current_t)) <= t_to_add and t_to_add > 0 : # Ensure 't' progresses if rounding stalls.
                current_t = t_to_add + 1
        if not candidates_t and max_t >=1 : candidates_t.append(1) # Ensure at least t=1 is run.


        all_run_results = {} # Dictionary to store results for each 't'.
        for t_value in candidates_t:
            # Loop through each candidate 't' value.
            print(f"\n--- Running Grover with t = {t_value} iterations ---")

            # Initialize new circuit for this 't_value'.
            circ = QuantumCircuit(15, len(input_qubits))
            Grover(circ=circ, t=t_value) # Construct Grover circuit.

            # Transpile and run.
            qc_compiled = transpile(circ, backend, optimization_level=optimization_level)
            job = backend.run(qc_compiled, shots=num_shots)
            result = job.result()
            counts = result.get_counts(qc_compiled)

            all_run_results[f"t_{t_value}"] = counts # Store counts for this 't'.
            print(f"Counts for t={t_value}: {counts}")

            # Plot and save histogram for current 't'.
            fig = plot_histogram(counts, title=f"Grover Results (Oracle: custom hash) for t={t_value}")
            pyplot.savefig(os.path.join(output_dir, f"histogram_t_{t_value}.png"))
            print(f"Histogram saved to histogram_t_{t_value}.png")
            pyplot.close(fig) # Close figure to free memory.
        
        # --- Save All Results to JSON ---
        json_filename = os.path.join(output_dir, "grover_all_run_results.json")
        try:
            with open(json_filename, 'w') as f_json:
                # Dump dictionary to JSON file with pretty printing.
                json.dump(all_run_results, f_json, indent=4) 
            print(f"\nResults saved to JSON file: {json_filename}")
        except IOError as e:
            print(f"Error saving to JSON: {e}")
