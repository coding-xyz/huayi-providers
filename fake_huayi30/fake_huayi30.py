import os
from qiskit.providers.fake_provider import fake_qasm_backend, fake_backend

class FakeHuayi30(fake_qasm_backend.FakeQasmBackend):
	dirname = os.path.dirname(__file__)
	conf_filename = 'conf_huayi30.json'
	props_filename = 'props_huayi30.json'
	backend_name = 'fake_huayi30'

class FakeHuayi30V2(fake_backend.FakeBackendV2):
	dirname = os.path.dirname(__file__)
	conf_filename = 'conf_huayi30.json'
	props_filename = 'props_huayi30.json'
	backend_name = 'fake_huayi30'
