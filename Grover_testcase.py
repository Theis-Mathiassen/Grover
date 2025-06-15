from Grover import *

backend = AerSimulator()
optimization_level = 1


def testGrover():
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

def testOracle():
    def classicalalgorithm(input):
        # Hash
        var3 = input[3] and input[2]
        var5 = input[6] and input[4]
        var4 = var5 and var3
        var2 = not var4

        # Eval
        input[1] = input[1] or input[0]
        var2 = var2 or input[1]
        var2 = not var2

        return var2

    print("Assume \"11111100\", \"11011100\", \"01111100\", \"01011100\" are the only inputs that classical algorithm and compute_fx return 1 for.")
    for i in range(256):
        input = [False]*8        
        for j in range(8):
            input[j] = (i >> j) & 1

        classic = classicalalgorithm(input)

        circ = QuantumCircuit(15, 1)

        for j in range(8):
            if input[j]:
                circ.x(j)
        compute_fx(circ)
        circ.measure(F_RESULT_ANC_INDEX, 0)
        # Transpile for selected backend and optimization level.
        qc_compiled = transpile(circ, backend, optimization_level=optimization_level)
        # Execute the circuit 'num_shots' times.
        job = backend.run(qc_compiled, shots=1)
        result = job.result() # Get execution results.
        counts = result.get_counts(qc_compiled) # Get measurement counts.
        quantum = -1
        measured_outcome_str = list(counts.keys())[0]
        if measured_outcome_str == '1':
            quantum = 1
        elif measured_outcome_str == '0':
            quantum = 0
        else:
            print("Something has gone terrible wrong")
        qc_compiled = transpile(circ, backend, optimization_level=optimization_level)

        if classic == 1 and quantum == 1:
            input.reverse()
            print(f"Both the classical and the quantum algorithm gave 1 for inputs: {input}.")
        else:
            if classic == 1:
                print(f"Error: Only classic gave 1 for inputs: {input}.")
            if quantum == 1:
                print(f"Error: Only quantum gave 1 for inputs: {input}.")


if __name__ == "__main__":
    testGrover()
    testOracle()

    


"""
Result:

Assume "11111100", "11011100", "01111100", "01011100" are found in the solutions.
Bitstring: 11111100 with number of occurences above threshold: 20
Bitstring: 11011100 with number of occurences above threshold: 20
Bitstring: 01111100 with number of occurences above threshold: 20
Bitstring: 01011100 with number of occurences above threshold: 20
Assume "11111100", "11011100", "01111100", "01011100" are the only inputs that classical algorithm and compute_fx return 1 for.
Both the classical and the quantum algorithm gave 1 for inputs: [0, 1, 0, 1, 1, 1, 0, 0].
Both the classical and the quantum algorithm gave 1 for inputs: [0, 1, 1, 1, 1, 1, 0, 0].
Both the classical and the quantum algorithm gave 1 for inputs: [1, 1, 0, 1, 1, 1, 0, 0].
Both the classical and the quantum algorithm gave 1 for inputs: [1, 1, 1, 1, 1, 1, 0, 0].

"""