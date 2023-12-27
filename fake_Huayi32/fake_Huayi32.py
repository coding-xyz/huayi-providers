import os
from qiskit.providers.fake_provider import fake_qasm_backend, fake_backend

class FakeHuayi32(fake_qasm_backend.FakeQasmBackend):
	dirname = os.path.dirname(__file__)
	conf_filename = 'conf_Huayi32.json'
	props_filename = 'props_Huayi32.json'
	backend_name = 'fake_Huayi32'

class FakeHuayi32V2(fake_backend.FakeBackendV2):
	dirname = os.path.dirname(__file__)
	conf_filename = 'conf_Huayi32.json'
	props_filename = 'props_Huayi32.json'
	backend_name = 'fake_Huayi32'
