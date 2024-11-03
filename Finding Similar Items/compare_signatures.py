import numpy as np

class CompareSignatures:
    def __init__(self, A: np.ndarray, B: np.ndarray):
        """
        Initializes the CompareSignatures class with two MinHash signatures.
        
        :param A: The first MinHash signature as a NumPy array.
        :param B: The second MinHash signature as a NumPy array.
        :raises ValueError: If the signatures do not have the same shape.
        """
        # Check if the signatures have the same length, raise error if not
        if A.shape != B.shape:
            raise ValueError("Signatures must be of the same length")
        
        # Store the signatures for comparison
        self.A = A
        self.B = B

    def compare(self) -> float:
        """
        Compares the two signatures to estimate their similarity.
        
        :return: A float representing the Jaccard similarity estimate between 
                 the two signatures, computed as the mean of matching entries.
        """
        # Calculate the proportion of elements that are equal between A and B
        return np.mean(self.A == self.B)
