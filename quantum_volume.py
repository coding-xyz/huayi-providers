import os
import json
import pandas as pd

from qiskit import transpile, execute
from qiskit.circuit.library import QuantumVolume as QuantumVolumeCircuit
from qiskit.quantum_info import Statevector

import matplotlib.pyplot as plt
import numpy as np

from timeit import default_timer as timer
from datetime import timedelta
from IPython.display import display, clear_output


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

def check_threshold(n_heavies, n_circuits, n_shots):
    """Evaluate adjusted threshold inequality for quantum volume.
    Args:
        n_heavies (int): Total number of heavy outputs measured from device
        n_circuits (int): Number of different square circuits run on device
        n_shots (int): Number of shots per circuit
    Returns:
        Bool:
            True if heavy output probability is > 2/3 with 97% certainty,
            otherwise False
    """
    from numpy import sqrt
    numerator = n_heavies - 2*sqrt(n_heavies*(n_shots-(n_heavies/n_circuits)))
    return bool(numerator/(n_circuits*n_shots) > 2/3)

def test_qv(device, n_qubits, n_circuits, n_shots, outputdir=None):
    """Try to achieve 2**n_qubits quantum volume on device.
    Args:
        device (qiskit.providers.Backend): Device to test.
        n_qubits (int): Number of qubits to use for test.
        n_circuits (int): Number of different circuits to run on the device.
        n_shots (int): Number of shots per circuit.
    Returns:
        Dictonary of the results
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
        # Somehow the optimization_level cannot be 3
        t_circuit = transpile(circuit, backend, optimization_level=2)
        job = backend.run(
            t_circuit, shots=shots, memory=True
            )
        return job.result().get_counts(), t_circuit

    # time it
    start_time = timer()

    # generate set of random circuits
    qv_circuits = [
        QuantumVolumeCircuit(n_qubits) for c in range(n_circuits)
    ]

    n_heavies = [0]*n_circuits  # number of measured heavy outputs
    cum_HOP = [0]*n_circuits  # cumulant heavy-output percentage
    cum_2sigma = [0]*n_circuits  # cumulant 2-sigma deviation
    transpiled_circuits = []

    circ_results = []
    circ_timer_in_sec = 0.0
    for i, circuit in enumerate(qv_circuits):
        
        start_time_circ = timer()
        
        # simulate circuit
        ideal_heavy_outputs = get_heavy_outputs(
            get_ideal_probabilities(circuit)
        )

        circuit.measure_all()
        real_counts, t_circuit = get_real_counts(circuit, device, n_shots)
        transpiled_circuits.append(t_circuit)
        # record whether device result is in the heavy outputs
        for output, count in real_counts.items():
            if output in ideal_heavy_outputs:
                n_heavies[i] += count
                
        elapsed_time_circ = timedelta( seconds = timer() - start_time_circ )
        circ_timer_in_sec += elapsed_time_circ.total_seconds()
        
        circ_result = {
            "ideal_heavy_outputs" : ideal_heavy_outputs,
            "n_heavy" : n_heavies[i],
            "n_shots" : n_shots,
            "HOP" : n_heavies[i] / n_shots,
            "elapsed_time" : str(elapsed_time_circ),
        }
        
        # export circuit and test results to <circuit_#.json>
        if outputdir != None:
            with open(f"{outputdir}/circuit_{i}.json", "w") as f:
                json.dump(
                    circ_result | {
                        "qv_circuit" : circuit.qasm(),
                        "transpiled_circuit" : t_circuit.qasm()},
                    f)
        
        circ_results.append( circ_result | { 
            "circuit_data_file": f"circuit_{i}.json"} )        
        cum_HOP[i] = sum(n_heavies[0:i+1]) / n_shots / (i+1) * 100
        cum_2sigma[i] = 2 * sqrt( cum_HOP[i] * ( 100.0 - cum_HOP[i] ) / (i+1) )

    # export the summary results to <summary.csv>
    if outputdir != None:
        result_df = pd.DataFrame(
            circ_results, 
            columns=[
                "ideal_heavy_outputs",
                "n_heavy", "n_shots", "HOP", 
                "elapsed_time", "circuit_data_file"]
        )
        with open(f"{outputdir}/summary.csv", "w") as f:
            result_df.to_csv(f)

    # do statistical check to see if device passes test
    is_pass = bool( (cum_HOP[-1]-cum_2sigma[-1]) > (100*2/3) )

    elapsed_time = timedelta( seconds = timer() - start_time )

    results = {
        "backend":device.name() if callable(device.name) else device.name,
        "n_qubits":n_qubits,
        "QV": 2**n_qubits, 
        "HOP": cum_HOP[-1], 
        "2sigma": cum_2sigma[-1],
        "success": is_pass, 
        "n_circuits": n_circuits,
        "n_shots": n_shots,
        "cum_HOP":cum_HOP,
        "cum_2sigma":cum_2sigma,
        "elapsed_time": str(elapsed_time),
        "elapsed_time_per_circuit": str(timedelta(
            seconds=circ_timer_in_sec/n_circuits)),
    }

    print(
        f"Quantum Volume: {2**n_qubits}\n"
        f"Percentage Heavy Outputs: {cum_HOP[-1]:.1f}%\n"
        f"Passed?: {is_pass}\n"
    )
    return results, qv_circuits, transpiled_circuits



def test_qv_for_depths(
    backend, depths, n_circuits, n_shots, 
    subdirname, dirname="QV_Results"):
    """Sweep the QV for different depths

    Args:
        backend: backend containing the noise model
        depths: list of depths to sweep
        n_circuits: number of random circuits for testing
        n_shots: number of shots for each random circuit
        filename: filename for the stored results
        dirname: (default: QV_Results) automatically create a folder to save the results

    Returns:
        results_df: A dataframe including the qv_test results as well as the random circuits
    """
    if not os.path.isdir(f"./{dirname}"):
        os.mkdir(f"./{dirname}")
    if not os.path.isdir(f"./{dirname}/{subdirname}"):
        os.mkdir(f"./{dirname}/{subdirname}")

    results_device_df = pd.DataFrame()

    for depth in depths:
        dir_depth = f"./{dirname}/{subdirname}/depth_{depth}"
        if not os.path.isdir(dir_depth):
            os.mkdir(dir_depth)
        result = test_qv(
            backend, depth, n_circuits, n_shots,
            outputdir=dir_depth)
        
        results_device_df = pd.concat([
            results_device_df,
            pd.DataFrame(
                result, 
                columns=[
                    "backend", "n_qubits", "QV", "HOP", 
                    "2sigma", "success", "n_circuits",
                    "n_shots", "elapsed_time",
                    "elapsed_time_per_circuit"],
                index=[0])],
            ignore_index=True)
        
    # export summary filr for each device test
    with open(f"{dirname}/{subdirname}/summary.csv","w") as f:
        results_device_df.to_csv(f, index=None)
        
    return results_device_df


def qv_plot(result):
    """Show the convergence plot of qv_test
    x-axis: circuit number
    y-axis: cumulant HOP, 2sigma, 2/3 threshold

    Args:
        result (dict): result of qv_test for one depth
    """
    
    x = np.array( range(result["n_circuits"]) )
    y = np.array( result["cum_HOP"] )
    yerr = np.array( result["cum_2sigma"] )

    fig, ax = plt.subplots()
    ax.scatter(x, y, s=6, c='r')
    ax.fill_between(x, y-yerr,  y+yerr, color='b', alpha=0.4)
    ax.hlines(2/3*100, ax.get_xlim()[0], ax.get_xlim()[1], linestyle='dashed', color='k')
    ax.set_ylim([40,100])
    plt.xlabel('num circs')
    plt.ylabel('HOP (%)')
    
    fig.show()
    
    
def qv_list_plot(
    backend_list: str | list[str],
    depths=None,
    dirname="QV_Results"):
    """Show the QV test results for different depths
    x-axis: depths being tested
    y-axis: HOP, 2sigma, 2/3 threshold

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
        with open(f"{dirname}/QV_{backend}/summary.csv", 'r') as f:
            df = pd.read_csv(f, index_col=0)
        if depths == None: depths = df['n_qubits'].values
        hop = df['HOP'].values
        h_low = df['HOP'].values - df['2sigma'].values
        h_high = df['HOP'].values + df['2sigma'].values
        p_hop = plt.plot( depths, hop, label=backend )
        p_err = plt.fill_between( depths, h_low, h_high, color=p_hop[0].get_color(), alpha=0.2)
        plt.legend()

    plt.hlines(2/3*100, depths[0]-1, depths[-1]+1, color='k', linestyle='dashed' )
    plt.xlabel('num qubits (log_2 QV)')
    plt.ylabel('HOP (%)')
    plt.show()
    
    display(df)
