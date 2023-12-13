# Build FakeHuayi backend

## Basic Use

Required files:

- ./fake_huayi/
    - \_\_init\_\_.py
    - fake_huayi.py
    - props_huayi.json
    - conf_huayi.json
    - defs_huayi.json (if Pulse Backend is applied, TODO)
- ./
    - qubits_data.csv
    - gates_data.csv

Import FakeHuayi backend

```
from fake_huayi import *
FackHuayi()    # for V1 backend
FackHuayiV2()  # for V2 backend
```

Generate noise model
```
from qiskit_aer.noise.noise_model import NoiseModel
noise_Huayi = NoiseModel.from_backend(FakeHuayi())
```

Create .json files that required to build the backend

```
from fake_huayi.HuayiBacken_build import create
c = create(backend_name="huayi",
           backend_version="x.x.x",
           qubits_data="qubits_data.csv",
           gates_data="gates_data.csv")
```

## File Structure

#### Expriment data

**qubits_data.csv** contains the information of qubits, including
- T1 time (ms)
- T2 time (ms)
- frequency (MHz)
- readout error rate
- Probability of finding 0 when prepared in 1
- Probability of finding 1 when prepared in 0
- readout length (us)

All information should be accompanied with the measurement date and time.

**gates_data.csv** contains the information of gates, including
- qubits
- gate type
- error rate
- length
- gate name (optional)

The gate error and length are measured from experiment, and should be accompanied with the measurement date and time.

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
