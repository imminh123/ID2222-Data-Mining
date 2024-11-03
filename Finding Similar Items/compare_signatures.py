import numpy as np


class CompareSignatures:
    def __init__(self, A: np.ndarray, B: np.ndarray):
        if A.shape != B.shape:
            raise ValueError("Signatures must be of the same length")

        self.A = A
        self.B = B

    def compare(self) -> float:
        return np.mean(self.A == self.B)
