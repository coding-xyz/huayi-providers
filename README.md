# Huayi Providers


## Basic Use

Import backend

```
from huayi_providers.fake_{backend_name} import *
Fake{backend_name}()    # for V1 backend
Fake{backend_name}V2()  # for V2 backend
```

Generate noise model
```
from qiskit_aer.noise.noise_model import NoiseModel
noise_model = NoiseModel.from_backend(Fake{backend_name}())
```

Build backends from ``.csv`` files

```
from huayi_providers.backend_build import build_from_file
c = build_from_file(backend_name,
                    backend_version,
                    qubits_data,
                    gates_data)
```

## File Structure

### Experiment data

Qubits properties are Stored in ``./data/qubits_data_{backend_name}.csv`` and gates information in ``./data/gates_data_{backend_name}.csv``.

``qubits_data_{}.csv`` contains the information of qubits, including
- T1 time (ms)
- T2 time (ms)
- frequency (MHz)
- readout error rate
- Probability of finding 0 when prepared in 1
- Probability of finding 1 when prepared in 0
- readout length (us)

All information should be accompanied with the measurement date and time.

``gates_data_{}.csv`` contains the information of gates, including
- qubits
- gate type
- error rate
- length
- gate name (optional)

The gate error and length are measured from experiment, and should be accompanied with the measurement date and time.

### Backend files

``from backend_build import build_from_file`` to generate the files for the backend.

- ./fake_{backend_name}/
    - \_\_init\_\_.py
    - fake_{backend_name}.py
    - props_{backend_name}.json
    - conf_{backend_name}.json
    - defs_{backend_name}.json (if Pulse Backend is applied, TODO)


#### Dictionaries of the backend properties and configurations

**props_huayi.json**
```
{'backend_name': 'fakehuayi',
 'backend_version='0.0.1',
 'last_update_date': now_time(),
 'qubits': [q1, q2, ...],
 'gates': [g1, g2, ...],
 'general': []}
```
 qubit info (q):
```
 [{'date': ['T1_date'], 'name': 'T1', 'unit': 'ms', 'value': ['T1']},
  {'date': ['T2_date'], 'name': 'T2', 'unit': 'ms', 'value': ['T2']},
  {'date': ['frequency_date'], 'name': 'frequency', 'unit': 'MHz', 'value': ['frequency']},
  {'date': ['readout_error_date'], 'name': 'readout_error', 'unit': '', 'value': ['readout_error']},
  {'date': ['prob_meas0_prep1_date'], 'name': 'prob_meas0_prep1', 'unit': '', 'value': ['prob_meas0_prep1']},
  {'date': ['prob_meas1_prep0_date'], 'name': 'prob_meas1_prep0', 'unit': '', 'value': ['prob_meas1_prep0']},
  {'date': ['readout_length_date'], 'name': 'readout_length', 'unit': 'us', 'value': ['readout_length']}]
```
gate info (g):
```
{'qubits': ['qubits'],
 'gate': ['gate'],
 'parameters': [{'date': ['error_date'],
                 'name': 'gate_error',
                 'unit': '',
                 'value': ['gate_error']},
                {'date': ['length_date'],
                 'name': 'gate_length',
                 'unit': 'ms',
                 'value': ['gate_length']}],
 'name': ['name']}
```

**conf_huayi.json**

#### Dictionary of the Noise Model

The keys in NoiseModel are
- basis gates ({'id', 'x', 'sx', 'rz', 'cx'})
- noise instructions ({'id', 'x', 'sx', 'cx', 'measure', 'reset', ''})
- noise qubits ({0, ... , 26})
- default quantum errors (set None by default)
- default readout errors (set None by default)
- local quantum errors
- local readout errors
- custom noise passes (set None by default)


**local readout errors**

```
noise_model._local_readout_errors = {(0,):ReadoutError, 
                                     (1,):ReadoutError, 
                                     (2,):ReadoutError, ...}
```

``ReadoutError`` is essentially a matrix, the off-diagonal terms corresponds to ``prob_meas0_prep1`` and ``prob_meas1_prep0``

If ``prob_meas0_prep1`` and ``prob_meas1_prep0`` are given, ``readout_error`` will be ignored.


**local quantum errors**

The errors of ``gate`` applied to indices ``ind = (i,) for one-bit gate, (i,j) for two-bit gate`` are stored in

```
noise_model._local_quantum_errors[gate][ind] = {
  '_id': xxxx,
  '_probs': list_of_probs,
  '_circs': list_of_circs,
  '_qargs': None,
  '_op_shape': OpShape(num_qargs_l, num_qargs_r)}
```

``_circs`` includes all possible matrices with the same shape of the corresponding gate

``_probs`` is the corresponding probability of each circ

For one-bit gate, ``_circ`` includes `I`, `X`, `Y`, `Z`. The probs of nonidentity matrices are ``gate_error/2``. ``gate_error`` in `.csv` file refers to the measurement of `1-(I+Z)`.

For two-bit gate, ``_circ`` includes `II`, `IX`, `IY`, `IZ`, `XI`, `XX`, `XY`, `XZ`, `YI`, `YX`, `YY`, `YZ`, `ZI`, `ZX`, `ZY`, `ZZ`. The probs of nonidentity matrices are ``gate_error/12``. The ``gate_error`` in `.csv` file refers to the measurement of `1-(II+IZ+ZI+ZZ)`.