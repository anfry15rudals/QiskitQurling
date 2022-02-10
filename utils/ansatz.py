from qiskit import QuantumCircuit, QuantumRegister
from qiskit.circuit import ParameterVector
import itertools

def add_hadamard(circuit, n_qubits):
    for i in range(n_qubits):
        circuit.h(i)

def add_single_qubit_rotation_base(circuit, Paramvector, n_qubits):
    for i in range(n_qubits):
        circuit.rx(Paramvector[i*3], i)
        circuit.ry(Paramvector[i*3+1], i)
        circuit.rz(Paramvector[i*3+2], i)

def add_encoding_layer_base(circuit, Paramvector, n_qubits):
    for i in range(n_qubits):
        circuit.rx(Paramvector[i], i)

def add_single_qubit_rotation_hw_eff(circuit, Paramvector, n_qubits):
    for i in range(n_qubits):
        circuit.rz(Paramvector[i*2], i)
        circuit.ry(Paramvector[i*2+1], i)

def add_encoding_layer_hw_eff(circuit, Paramvector, n_qubits):
    for i in range(n_qubits):
        circuit.ry(Paramvector[i*2], i)
        circuit.rz(Paramvector[i*2+1], i)

def add_entangling_layer(circuit, n_qubits):
    qubits = [i for i in range(n_qubits)]
    for c in itertools.combinations(qubits, 2):
        circuit.cz(c[0], c[1])
        
def single_qubit_gate_1(circuit, Paramvector, n_qubits=2):
    for i in range(n_qubits):
        circuit.ry(Paramvector[i*2], i)
        circuit.rz(Paramvector[i*2+1], i)

def single_qubit_gate_2(circuit, Paramvector, n_qubits=2):
    for i in range(n_qubits):
        circuit.rz(Paramvector[i*3], i)
        circuit.ry(Paramvector[i*3+1], i)
        circuit.rz(Paramvector[i*3+2], i)

def entangled_gate(circuit, Paramvector):
    circuit.cnot(0, 1)
    circuit.rx(Paramvector[0], 0)
    circuit.rz(Paramvector[1], 1)
    circuit.h(0)
    circuit.cnot(0, 1)
    circuit.h(0)
    circuit.rz(Paramvector[2], 1)
    circuit.cnot(0, 1)

def encoding_layer(circuit, Paramvector, n_qubit=2):
    for i in range(n_qubit):
        circuit.ry(Paramvector[i*2], i)
        circuit.rz(Paramvector[i*2+1], i)
        
def build_circuit(n_qubits, n_layers, opt=None):
    qr = QuantumRegister(n_qubits)
    qc = QuantumCircuit(qr)
    
    if opt == 'base' or opt == None:
        param_rot = ParameterVector('Rot', 3*n_qubits*(n_layers+1))
        param_enc = ParameterVector('Enc', n_qubits*n_layers)
        
        print(len(param_rot))
        
    #     add_hadamard(qc, n_qubits)
        for l in range(n_layers):
            # Variational + Encoding Layer
            add_single_qubit_rotation_base(qc, param_rot[l*(3*n_qubits):(l+1)*(3*n_qubits)], n_qubits)
            qc.barrier()
            add_entangling_layer(qc, n_qubits)
            qc.barrier()
            # Encoding Layer
            add_encoding_layer_base(qc, param_enc[l*n_qubits:(l+1)*n_qubits], n_qubits)
            qc.barrier()
        # Last Variational Layer
        add_single_qubit_rotation_base(qc, param_rot[n_layers*(3*n_qubits):(n_layers+1)*(3*n_qubits)], n_qubits)
        
        return qc, param_rot, param_enc

    elif opt == 'hw_eff':
        param_rot = ParameterVector('Rot', 2*n_qubits*(n_layers+1))
        param_enc = ParameterVector('Enc', 2*n_qubits*n_layers)

        add_hadamard(qc, n_qubits)
        for l in range(n_layers):
            # Variational + Encoding Layer
            add_single_qubit_rotation_hw_eff(qc, param_rot[l*(2*n_qubits):(l+1)*(2*n_qubits)], n_qubits)
            qc.barrier()
            add_entangling_layer(qc, n_qubits)
            qc.barrier()
            # Encoding Layer
            add_encoding_layer_hw_eff(qc, param_enc[l*(2*n_qubits):(l+1)*(2*n_qubits)], n_qubits)
            qc.barrier()
        # Last Variational Layer
        add_single_qubit_rotation_hw_eff(qc, param_rot[n_layers*(2*n_qubits):(n_layers+1)*(2*n_qubits)], n_qubits)
        
        return qc, param_rot, param_enc
    
    elif opt == 'universal':
        param_single = ParameterVector('Rot', 10)
        param_entangle = ParameterVector('Enc', 3)

        single_qubit_gate_1(qc, param_single[0:4], 2)
        qc.barrier()
        entangled_gate(qc, param_entangle)
        qc.barrier()
        single_qubit_gate_2(qc, param_single[4:10], 2)

        return qc, param_single, param_entangle

    elif opt == 'universal_encoding':
        param_universal = ParameterVector('Univ', 13)
        param_enc = ParameterVector('Enc', 4)

        single_qubit_gate_1(qc, param_universal[0:4], 2)
        qc.barrier()
        entangled_gate(qc, param_universal[4:7])
        qc.barrier()
        single_qubit_gate_2(qc, param_universal[7:13], 2)

        qc.barrier()
        encoding_layer(qc, param_enc, 2)

        return qc, param_universal, param_enc
    
    elif opt == 'omega':
        param_phi = ParameterVector('phi', 4)
        param_state = ParameterVector('state', 2)

        qc.h(0)
        qc.h(1)
    
        qc.ry(param_phi[0], 0)
        qc.rz(param_phi[1], 0)
        qc.ry(param_phi[2], 1)
        qc.rz(param_phi[3], 1)
    
        qc.ry(param_state[0], 0)
        qc.ry(param_state[1], 1)
        
        qc.barrier()
    
        qc.cnot(1, 0)
        qc.h(0)
        qc.h(1)
        qc.cnot(1, 0)

        return qc, param_phi, param_state

    elif opt == 'omega2':
        param_phi = ParameterVector('phi', 8)
        param_state = ParameterVector('state', 2)

        qc.h(0)
        qc.h(1)
    
        qc.ry(param_phi[0], 0)
        qc.rz(param_phi[1], 0)
        qc.ry(param_phi[2], 1)
        qc.rz(param_phi[3], 1)
    
        qc.ry(param_state[0], 0)
        qc.ry(param_state[1], 1)
        
        qc.barrier()
    
        qc.cnot(1, 0)
        qc.ry(param_phi[4], 0)
        qc.rz(param_phi[5], 0)
        qc.ry(param_phi[6], 1)
        qc.rz(param_phi[7], 1)
        qc.cnot(1, 0)

        return qc, param_phi, param_state

    else:
        return qc, 0, 0
