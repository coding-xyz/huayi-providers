import pandas
import json
import os
from datetime import datetime, timezone, timedelta

from qiskit.providers.models.backendproperties import BackendProperties, Nduv, GateProperties
from qiskit.providers.models.backendconfiguration import QasmBackendConfiguration, GateConfig

def now_time():
    tz = timezone(timedelta(hours=+8))
    return datetime.now(tz).isoformat(timespec='minutes')

class build_from_file:

    def __init__(self,
                 backend_name:str,
                 backend_version:str,
                 qubits_data:str,
                 gates_data:str,
                 gate_radius=None):

        self.backend_dir = "fake_{}".format(backend_name)
        self.backend_absdir = os.path.join(os.path.dirname(__file__), self.backend_dir)

        if all((
            self.create_init_file(backend_name),
            self.create_props(backend_name,
                          backend_version,
                          qubits_data,
                          gates_data),
            self.create_conf(backend_name,
                         backend_version,
                         gate_radius)
        )):
            print("New backends created, please import the backends with:")
            print("from huayi_providers.{} import {}, {}".format(self.backend_dir, self.backend_names[0], self.backend_names[1]))
    

    def create_props(self,
                     backend_name,
                     backend_version,
                     qubits_data,
                     gates_data) -> bool:
        try:
            qubits_info = pandas.read_csv(qubits_data)
            qubits = []
            for qubit_id,qubit in qubits_info.iterrows():
                qubits.append([
                    Nduv(date=qubit['T1_date'], name='T1', unit='ms', value=qubit['T1']),
                    Nduv(date=qubit['T2_date'], name='T2', unit='ms', value=qubit['T2']),
                    Nduv(date=qubit['frequency_date'], name='frequency', unit='MHz', value=qubit['frequency']),
                    Nduv(date=qubit['readout_error_date'], name='readout_error', unit='', value=qubit['readout_error']),
                    Nduv(date=qubit['prob_meas0_prep1_date'], name='prob_meas0_prep1', unit='', value=qubit['prob_meas0_prep1']),
                    Nduv(date=qubit['prob_meas1_prep0_date'], name='prob_meas1_prep0', unit='', value=qubit['prob_meas1_prep0']),
                    Nduv(date=qubit['readout_length_date'], name='readout_length', unit='us', value=qubit['readout_length'])
                    ])
                
            self.n_qubits = len(qubits)
                
            gates_info = pandas.read_csv(gates_data)
            gates = []
            for gate_id,gate in gates_info.iterrows():
                gates.append(GateProperties(
                    qubits=json.loads(gate['qubits']),
                    gate=gate['gate'],
                    parameters=[
                        Nduv(date=gate['error_date'],name='gate_error',unit='',value=gate['gate_error']),
                        Nduv(date=gate['length_date'],name='gate_length',unit='us',value=gate['gate_length'])
                        ],
                    name=gate['name'])
                )

            props = BackendProperties(
                backend_name=backend_name, 
                backend_version=backend_version, 
                last_update_date=now_time(), 
                qubits=qubits, 
                gates=gates,
                general=[]).to_dict()
            
            props["last_update_date"] = now_time()
            # qiskit will force last_update_date be datetime.datetime, but it must be a str to be dumped

            with open(self.backend_absdir+'/props_'+backend_name+'.json', 'w') as fp:
                json.dump(props, fp)
                self.props = BackendProperties.from_dict(props)
                print("Successfully created props_{}.json".format(backend_name))

            return True

        except IOError as e:
            print("Failed to create props_{}.json".format(backend_name))
            print(e)
            return False


    def create_conf(self,
                    backend_name,
                    backend_version,
                    gates_radius) -> bool:
        
        try:
            n_qubits = self.n_qubits
            # Fully connected map
            if gates_radius:
                coupling_map = [[i,j] for i in range(n_qubits) 
                                for j in list(range(max(0,i-gates_radius),i))+list(range(i+1,min(i+1+gates_radius,n_qubits)))]
            else:
                coupling_map = [[i,j] for i in range(n_qubits) 
                                for j in list(range(i))+list(range(i+1,n_qubits))]

            basis_gates = [
                "id",
                "rx",
                "ry",
                "cz",
                "reset"]

            # Definition of gates configurations requires OpenQASM
            # See Specifications: https://openqasm.com/language/gates.html#defining-gates
            # also: https://dl.acm.org/doi/10.1145/3505636
            gates = []
            gates.append(GateConfig(
                name='id',
                parameters=[],
                qasm_def="gate id q { id q; }",
                coupling_map=[[i] for i in range(n_qubits)]
                ))
            gates.append(GateConfig(
                name='rx',
                parameters=["θ"],
                qasm_def="gate rx(θ) q { U(θ, -pi/2, pi/2) q; }",
                coupling_map=[[i] for i in range(n_qubits)]
                ))
            gates.append(GateConfig(
                name='ry',
                parameters=["θ"],
                qasm_def="gate ry(θ) q { U(θ, 0, 0) q; }",
                coupling_map=[[i] for i in range(n_qubits)]
                ))
            gates.append(GateConfig(
                name='cz',
                parameters=[],
                qasm_def="gate cz q1, q2 { ctrl @ z q1, q2; }",
                coupling_map=coupling_map
                ))

            conf = QasmBackendConfiguration(
                backend_name=backend_name,
                backend_version=backend_version,
                n_qubits=n_qubits,
                basis_gates=basis_gates,
                gates=gates,
                local=True,
                simulator=True,
                conditional=False,
                open_pulse=False,
                memory=True,
                max_shots=6000,
                coupling_map=coupling_map,
                online_date=now_time(), # somehow oneline_date must be defined to create the backend
                ).to_dict()

            with open(self.backend_absdir+'/conf_'+backend_name+'.json', 'w') as fp:
                json.dump(conf, fp)
                self.conf = QasmBackendConfiguration.from_dict(conf)
                print("Successfully created conf_{}.json".format(backend_name))

            return True

        except IOError as e:
            print("Failed to create props_{}.json".format(backend_name))
            print(e)
            return False


    def create_init_file(self, backend_name) -> bool:

        try:
            if not os.path.isdir(self.backend_absdir):
                os.mkdir(self.backend_absdir)
    
            backend_name1 = "Fake{}".format(backend_name.title())
            backend_name2 = "Fake{}V2".format(backend_name.title())
            
            with open(self.backend_absdir+"/__init__.py",'w') as f:
                f.write("from .{0} import {1}\n".format(self.backend_dir, backend_name1))
                f.write("from .{0} import {1}\n".format(self.backend_dir, backend_name2))
    
            with open(self.backend_absdir+"/fake_{}.py".format(backend_name),'w') as f:
                f.write("import os\n")
                f.write("from qiskit.providers.fake_provider import fake_qasm_backend, fake_backend\n")
                
                f.write("\nclass {}(fake_qasm_backend.FakeQasmBackend):\n".format(backend_name1))
                f.write("\tdirname = os.path.dirname(__file__)\n")
                f.write("\tconf_filename = 'conf_{}.json'\n".format(backend_name))
                f.write("\tprops_filename = 'props_{}.json'\n".format(backend_name))
                f.write("\tbackend_name = 'fake_{}'\n".format(backend_name))
                
                f.write("\nclass {}(fake_backend.FakeBackendV2):\n".format(backend_name2))
                f.write("\tdirname = os.path.dirname(__file__)\n".format(backend_name))
                f.write("\tconf_filename = 'conf_{}.json'\n".format(backend_name))
                f.write("\tprops_filename = 'props_{}.json'\n".format(backend_name))
                f.write("\tbackend_name = 'fake_{}'\n".format(backend_name))

                self.backend_names = [backend_name1, backend_name2]

            isimported = False
            with open(os.path.dirname(__file__)+"/__init__.py", 'r') as f:
                lines = f.readlines()
                for line in lines:
                    if "from .{} import *".format(self.backend_dir) in line:
                        isimported = True
            if not isimported:
                with open(os.path.dirname(__file__)+"/__init__.py", 'a') as f:
                    f.write("\nfrom .{} import *".format(self.backend_dir))
            
            return True
            
        except IOError as e:
            print("Failed to create initializing scripts")
            print(e)
            return False

