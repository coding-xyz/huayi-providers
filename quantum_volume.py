import os
import json
import pandas as pd

from qiskit import transpile, execute
from qiskit.circuit.library import QuantumVolume as QuantumVolumeCircuit
from qiskit.quantum_info import Statevector

import matplotlib.pyplot as plt
import numpy as np

def get_heavy_outputs(counts):
    """Extract heavy outputs from counts dict.
    Args:
        counts (dict): Output of `.get_counts()`
    Returns:
        list: All states with measurement probability greater than the mean.
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
        "backend":device.name() if callable(device.name) else device.name,
        "n_qubits":nqubits,
        "QV": 2**nqubits, 
        "HOP": percent_heavy_outputs, 
        "2sigma": cum_2sigma[-1]*100,
        "success": is_pass, 
        "n_circuits": ncircuits,
        "n_shots": nshots,
        "cum_HOP":cum_HOP,
        "cum_2sigma":cum_2sigma}

    print(f"Quantum Volume: {2**nqubits}\n"
          f"Percentage Heavy Outputs: {percent_heavy_outputs:.1f}%\n"
          f"Passed?: {is_pass}\n")
    return results, qv_circuits, transpiled_circuits



def qv_for_depth(backend, depths, n_circuits, n_shots, filename,
                 dirname="QV_Results"):
    """Sweep the QV for different depths

    Args:
        backend: backend containing the noise model
        depths: list of depths to sweep
        n_circuits: number of random circuits for testing
        n_shots: number of shots for each random circuit
        filename: filename for the stored results
        dirname: (default: QV_Results) automatically create a folder to save the results

    Returns:
        results: A dataframe including the qv_test results as well as the random circuits
    """
    if not os.path.isdir(f"./{dirname}"):
        os.mkdir(f"./{dirname}")

    results_df = pd.DataFrame()

    for depth in depths:
        result, qv_circs, tr_circs = test_qv(backend, 
                                             depth, 
                                             ncircuits=n_circuits, 
                                             nshots=n_shots)
        results_df = pd.concat([results_df, 
                                pd.DataFrame(result, 
                                             columns=["backend", "n_qubits", "QV", "HOP", "success", "n_circuits", "n_shots", "2sigma"], 
                                             index=[0])],
                               ignore_index=True)
        qv_export = result | {"QV_circuits": [c.qasm() for c in qv_circs]} | {"transpiled_circuits": [c.qasm() for c in tr_circs]}
        
        with open(f"{dirname}/{filename}_{depth}.json", 'w') as f:
            json.dump(qv_export, f)

    return results_df


def qv_plot(result):
    """Show the convergence plot of qv_test

    Args:
        result (dict): result of qv_test
    """

    fig, ax = plt.subplots()
    ax.scatter(range(result["n_circuits"]), result["cum_HOP"], s=6, c='r')
    ax.fill_between(range(result["n_circuits"]), 
                    np.array(result["cum_HOP"]) - np.array(result["cum_2sigma"]), 
                    np.array(result["cum_HOP"]) + np.array(result["cum_2sigma"]), color='b', alpha=0.4)
    ax.hlines(2/3, ax.get_xlim()[0], ax.get_xlim()[1], linestyle='dashed', color='k')
    ax.set_ylim([0.4,1])
    
    fig.show()
    
    
def qv_list_plot(backend_list: str | list[str],
                 depths: list[int],
                 dirname="QV_Results"):
    """Show the QV test results for different depths

    Args:
        backend_list (str | list[str]): name of the backends
        depths (list[int]): depths that have been calculated
        dirname (str, optional): directory that stores the calculation results. Defaults to "QV_Results".
        
    Note:
        The data should be strored as "{dirname}/QV_{backend}_{depth}.json"
    """
    
    if isinstance(backend_list, str):
        backend_list = [backend_list]
    
    fig = plt.figure()
    
    for backend in backend_list:
        hop = []
        h_low = []
        h_high = []
        for d in depths:
            with open(f"{dirname}/QV_{backend}_{d}.json", 'r') as f:
                data = json.load(f)
                hop.append(data['HOP'])
                h_low.append(data['HOP'] - data['2sigma'])
                h_high.append(data['HOP'] + data['2sigma'])
        p_hop = plt.plot( depths, hop, label=backend )
        p_err = plt.fill_between( depths, h_low, h_high, color=p_hop[0].get_color(), alpha=0.2)
        plt.legend()

    plt.hlines(2/3*100, depths[0]-1, depths[-1]+1, color='k', linestyle='dashed' )
    plt.xlabel('num qubits (log_2 QV)')
    plt.ylabel('HOP (%)')
    plt.show() 

            