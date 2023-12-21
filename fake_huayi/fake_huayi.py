import os
from qiskit.providers.fake_provider import fake_qasm_backend, fake_backend

class FakeHuayi(fake_qasm_backend.FakeQasmBackend):
	dirname = os.path.dirname(__file__)
	conf_filename = 'conf_huayi.json'
	props_filename = 'props_huayi.json'
	backend_name = 'fake_huayi'

class FakeHuayiV2(fake_backend.FakeBackendV2):
	dirname = os.path.dirname(__file__)
	conf_filename = 'conf_huayi.json'
	props_filename = 'props_huayi.json'
	backend_name = 'fake_huayi'
