def common_basis_gates(gates_set_name):
    if gates_set_name == "rxrxcz":
        basis_gates = [
            "id",
            "rx",
            "ry",
            "cz",
            "reset"]
    elif gates_set_name == "rrzrzz":
        basis_gates = [
            "id",
            "r",
            "rz",
            "rzz",
            "reset"]
    else:
        basis_gates = []
        print("Basis set's name not found.")
    return basis_gates

def finite_connected_map(n_qubits, radius):
    if radius <= n_qubits:
        coupling_map = [[i,j]
                        for i in range(n_qubits) 
                        for j in list(range(max(0,i-radius),i)) + 
                        list(range(i+1,min(i+1+radius,n_qubits)))]
    else:
        coupling_map = [[i,j]
                        for i in range(n_qubits) 
                        for j in list(range(i))+list(range(i+1,n_qubits))]
    return coupling_map