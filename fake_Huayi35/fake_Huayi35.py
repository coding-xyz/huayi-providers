<<<<<<< HEAD
import os
from qiskit.providers.fake_provider import fake_qasm_backend, fake_backend

class FakeHuayi35(fake_qasm_backend.FakeQasmBackend):
	dirname = os.path.dirname(__file__)
	conf_filename = 'conf_Huayi35.json'
	props_filename = 'props_Huayi35.json'
	backend_name = 'fake_Huayi35'

class FakeHuayi35V2(fake_backend.FakeBackendV2):
	dirname = os.path.dirname(__file__)
	conf_filename = 'conf_Huayi35.json'
	props_filename = 'props_Huayi35.json'
	backend_name = 'fake_Huayi35'
=======
import os
from qiskit.providers.fake_provider import fake_qasm_backend, fake_backend

class FakeHuayi35(fake_qasm_backend.FakeQasmBackend):
	dirname = os.path.dirname(__file__)
	conf_filename = 'conf_Huayi35.json'
	props_filename = 'props_Huayi35.json'
	backend_name = 'fake_Huayi35'

class FakeHuayi35V2(fake_backend.FakeBackendV2):
	dirname = os.path.dirname(__file__)
	conf_filename = 'conf_Huayi35.json'
	props_filename = 'props_Huayi35.json'
	backend_name = 'fake_Huayi35'
>>>>>>> e137d03f7dbbc2f0b2425aade99617c8b7b784a7
