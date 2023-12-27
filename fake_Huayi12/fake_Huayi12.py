import os
from qiskit.providers.fake_provider import fake_qasm_backend, fake_backend

class FakeHuayi12(fake_qasm_backend.FakeQasmBackend):
	dirname = os.path.dirname(__file__)
	conf_filename = 'conf_Huayi12.json'
	props_filename = 'props_Huayi12.json'
	backend_name = 'fake_Huayi12'

class FakeHuayi12V2(fake_backend.FakeBackendV2):
	dirname = os.path.dirname(__file__)
	conf_filename = 'conf_Huayi12.json'
	props_filename = 'props_Huayi12.json'
	backend_name = 'fake_Huayi12'
