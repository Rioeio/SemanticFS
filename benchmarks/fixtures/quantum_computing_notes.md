# Quantum Superposition & Entanglement Principles

## Overview of Qubits vs Classical Bits
Unlike a classical bit which remains in a discrete state of `0` or `1`, a qubit exists in a linear superposition state represented by the state vector $|\psi\rangle$:

$$|\psi\rangle = \alpha|0\rangle + \beta|1\rangle$$

where $\alpha$ and $\beta$ are complex probability amplitudes satisfying $|\alpha|^2 + |\beta|^2 = 1$.

## Essential Quantum Logic Gates
- **Hadamard Gate (H)**: Creates an equal probability superposition state from a basis state.
- **Pauli-X Gate**: Acts as a quantum NOT gate, flipping $|0\rangle \rightarrow |1\rangle$.
- **CNOT Gate (Controlled-NOT)**: Entangles two qubits, generating Bell states like $\frac{1}{\sqrt{2}}(|00\rangle + |11\rangle)$.

## Quantum Error Correction
Shor's 9-qubit code protects arbitrary single-qubit errors by encoding logical qubits across 9 physical qubits to counter phase flips and bit flips.
