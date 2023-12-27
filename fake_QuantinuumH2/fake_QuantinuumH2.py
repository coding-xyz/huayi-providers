import os
from qiskit.providers.fake_provider import fake_qasm_backend, fake_backend

class FakeQuantinuumh2(fake_qasm_backend.FakeQasmBackend):
	dirname = os.path.dirname(__file__)
	conf_filename = 'conf_QuantinuumH2.json'
	props_filename = 'props_QuantinuumH2.json'
	backend_name = 'fake_QuantinuumH2'

class FakeQuantinuumh2V2(fake_backend.FakeBackendV2):
	dirname = os.path.dirname(__file__)
	conf_filename = 'conf_QuantinuumH2.json'
	props_filename = 'props_QuantinuumH2.json'
	backend_name = 'fake_QuantinuumH2'
