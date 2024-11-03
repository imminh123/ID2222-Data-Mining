import numpy as np


class MinHash:
    def __init__(self, shingles: set[int], num_hashes: int, seed: int = 42):
        self.shingles = shingles
        self.num_hashes = num_hashes
        self.seed = seed
        self.signature = None
        self._generate_signature()

    def _generate_signature(self) -> None:
        # Use a random generator for reproducibility
        rng = np.random.default_rng(self.seed)
        # Choose a large prime number for the modulo operation to reduce collisions.
        c = 2**31 - 1

        # Generate unique pairs (a, b) for each hash function
        hash_parameters = rng.integers(low=1, high=c, size=(self.num_hashes, 2))

        # Initialize the signature with inf
        signature = np.full(self.num_hashes, np.inf)

        # Compute the minHash signature
        for shingle in self.shingles:
            # Vectorized computation of hash values for the current shingle
            # h(x) = (ax + b) % c where x is the shingle
            hash_values = (hash_parameters[:, 0] * shingle + hash_parameters[:, 1]) % c
            # Update the signature with the minimum hash values
            signature = np.minimum(signature, hash_values)

        self.signature = signature.astype(int)

    def get_signature(self) -> np.ndarray:
        return self.signature
