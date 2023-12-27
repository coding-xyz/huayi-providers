import os
from qiskit.providers.fake_provider import fake_qasm_backend, fake_backend

class FakeHuayi32_LE_RZZ(fake_qasm_backend.FakeQasmBackend):
	dirname = os.path.dirname(__file__)
	conf_filename = 'conf_Huayi32_LE_RZZ.json'
	props_filename = 'props_Huayi32_LE_RZZ.json'
	backend_name = 'fake_Huayi32_LE_RZZ'

class FakeHuayi32_LE_RZZV2(fake_backend.FakeBackendV2):
	dirname = os.path.dirname(__file__)
	conf_filename = 'conf_Huayi32_LE_RZZ.json'
	props_filename = 'props_Huayi32_LE_RZZ.json'
	backend_name = 'fake_Huayi32_LE_RZZ'
