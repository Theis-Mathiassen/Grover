from Grover import *

if __name__ == "__main__":

    # --- KNOWN SOLUTIONS MODE ---
    # Assumes the number of solutions 's' is known, allowing for optimal 't' calculation.

    # Initialize quantum circuit: 15 total qubits, 8 classical bits for output.
    circ = QuantumCircuit(15, len(input_qubits))

    # Optimal iterations 't' for 4 solutions in 2^8 search space.
    # t = round( (pi/4) * sqrt(N/s) ) = round( (pi/4) * sqrt(256/4) ) ~ 6.
    Grover(circ=circ, t=1)

    # Transpile for selected backend and optimization level.
    qc_compiled = transpile(circ, backend, optimization_level=optimization_level)

    # Execute the circuit 'num_shots' times.
    job = backend.run(qc_compiled, shots=num_shots)
    result = job.result() # Get execution results.
    counts = result.get_counts(qc_compiled) # Get measurement counts.

    # --- Save Circuit Diagram & Histogram ---
    circuit_diagram = circ.draw('mpl') # Generate circuit diagram.
    circuit_diagram.savefig(os.path.join(output_dir, "circuit_diagram_1.png")) # Save diagram.

    selected_results = {}
    threshold = 20 # Define your threshold

    print("Assume \"11111100\", \"11011100\", \"01111100\", \"01011100\" are found in the solutions.")
    for bitstring, num_occurrences in counts.items():
        # bitstring will be like '11001011'
        # num_occurrences will be its corresponding value, e.g., 1
        if num_occurrences > threshold:
            print(f"Bitstring: {bitstring} with number of occurences above threshold: {threshold}")
            selected_results[bitstring] = num_occurrences


