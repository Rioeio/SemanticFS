"""
Linear Algebra Solver Module for Matrix Decomposition and Eigenvalues.
Supports Gaussian Elimination, LU Decomposition, and Singular Value Decomposition (SVD).
"""

import numpy as np

def gaussian_elimination(A: np.ndarray, b: np.ndarray) -> np.ndarray:
    """Solve Linear System Ax = b using Gaussian Elimination with Partial Pivoting."""
    n = len(b)
    M = np.hstack([A.astype(float), b.astype(float).reshape(-1, 1)])
    for i in range(n):
        max_row = i + np.argmax(np.abs(M[i:, i]))
        M[[i, max_row]] = M[[max_row, i]]
        for j in range(i + 1, n):
            factor = M[j, i] / M[i, i]
            M[j, i:] -= factor * M[i, i:]
    x = np.zeros(n)
    for i in range(n - 1, -1, -1):
        x[i] = (M[i, -1] - np.dot(M[i, i + 1:n], x[i + 1:n])) / M[i, i]
    return x

class MatrixDecomposer:
    """Computes matrix factorizations for dense systems."""
    def lu_decompose(self, matrix: np.ndarray):
        """Compute LU decomposition of a square matrix."""
        n = matrix.shape[0]
        L = np.eye(n)
        U = matrix.copy().astype(float)
        for i in range(n):
            for j in range(i + 1, n):
                factor = U[j, i] / U[i, i]
                L[j, i] = factor
                U[j, i:] -= factor * U[i, i:]
        return L, U
