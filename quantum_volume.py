from qiskit import transpile, execute
from qiskit.circuit.library import QuantumVolume as QuantumVolumeCircuit
from qiskit.quantum_info import Statevector

def get_heavy_outputs(counts):
    """Extract heavy outputs from counts dict.
    Args:
        counts (dict): Output of `.get_counts()`
    Returns:
        list: All states with measurement probability greater
              than the mean.
    """
    # sort the keys of `counts` by value of counts.get(key)
    sorted_counts = sorted(counts.keys(), key=counts.get)
    # discard results with probability < median
    heavy_outputs = sorted_counts[len(sorted_counts)//2:]
    return heavy_outputs

def check_threshold(nheavies, ncircuits, nshots):
    """Evaluate adjusted threshold inequality for quantum volume.
    Args:
        nheavies (int): Total number of heavy outputs measured from device
        ncircuits (int): Number of different square circuits run on device
        nshots (int): Number of shots per circuit
    Returns:
        Bool:
            True if heavy output probability is > 2/3 with 97% certainty,
            otherwise False
    """
    from numpy import sqrt
    numerator = nheavies - 2*sqrt(nheavies*(nshots-(nheavies/ncircuits)))
    return bool(numerator/(ncircuits*nshots) > 2/3)


def test_qv(device, nqubits, ncircuits, nshots):
    """Try to achieve 2**nqubits quantum volume on device.
    Args:
        device (qiskit.providers.Backend): Device to test.
        nqubits (int): Number of qubits to use for test.
        ncircuits (int): Number of different circuits to run on the device.
        nshots (int): Number of shots per circuit.
    Returns:
        Bool
            True if device passes test, otherwise False.
    """
    from numpy import sqrt

    def get_ideal_probabilities(circuit):
        """Simulates circuit behaviour on a device with no errors."""
        state_vector = Statevector.from_instruction(
                circuit.remove_final_measurements(inplace=False)
            )
        return state_vector.probabilities_dict()

    def get_real_counts(circuit, backend, shots):
        """Runs circuit on device and returns counts dict."""
        t_circuit = transpile(circuit, backend, optimization_level=3)
        job = backend.run(t_circuit,
                          shots=shots,
                          memory=True)
        return job.result().get_counts(), t_circuit

    # generate set of random circuits
    qv_circuits = [
        QuantumVolumeCircuit(nqubits) for c in range(ncircuits)
    ]

    nheavies = [0]*ncircuits  # number of measured heavy outputs
    cum_HOP = [0]*ncircuits  # cumulant heavy-output percentage
    cum_2sigma = [0]*ncircuits  # cumulant 2-sigma deviation
    transpiled_circuits = []
    for i, circuit in enumerate(qv_circuits):
        # simulate circuit
        ideal_heavy_outputs = get_heavy_outputs(
            get_ideal_probabilities(circuit)
        )
        # run circuit on device
        circuit.measure_all()
        real_counts, t_circuit = get_real_counts(circuit, device, nshots)
        transpiled_circuits.append(t_circuit)
        # record whether device result is in the heavy outputs
        for output, count in real_counts.items():
            if output in ideal_heavy_outputs:
                nheavies[i] += count
        cum_HOP[i] = sum(nheavies[0:i+1]) / nshots / (i+1)
        cum_2sigma[i] = 2 * sqrt( cum_HOP[i] * ( 1 - cum_HOP[i] ) / (i+1) )

    # do statistical check to see if device passes test
    is_pass = check_threshold(sum(nheavies), ncircuits, nshots)
    # calculate percentage of measurements that are heavy outputs
    percent_heavy_outputs = sum(nheavies)*100/(ncircuits*nshots)

    results = {
        "backend":device.name(),
        "n_qubits":nqubits,
        "QV": 2**nqubits, 
        "HOP": percent_heavy_outputs, 
        "success": is_pass, 
        "n_circuits": ncircuits,
        "n_shots": nshots,
        "cum_HOP":cum_HOP,
        "cum_2sigma":cum_2sigma}

    print(f"Quantum Volume: {2**nqubits}\n"
          f"Percentage Heavy Outputs: {percent_heavy_outputs:.1f}%\n"
          f"Passed?: {is_pass}\n")
    return results, qv_circuits, transpiled_circuits