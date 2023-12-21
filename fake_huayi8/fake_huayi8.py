import os
from qiskit.providers.fake_provider import fake_qasm_backend, fake_backend

class FakeHuayi8(fake_qasm_backend.FakeQasmBackend):
	dirname = os.path.dirname(__file__)
	conf_filename = 'conf_huayi8.json'
	props_filename = 'props_huayi8.json'
	backend_name = 'fake_huayi8'

class FakeHuayi8V2(fake_backend.FakeBackendV2):
	dirname = os.path.dirname(__file__)
	conf_filename = 'conf_huayi8.json'
	props_filename = 'props_huayi8.json'
	backend_name = 'fake_huayi8'
