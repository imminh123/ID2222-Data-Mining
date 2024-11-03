import numpy as np

class MinHash:
    def __init__(self, shingles: set[int], num_hashes: int, seed: int = 42):
        """
        Initializes the MinHash class with a set of shingles, the number of hash functions,
        and an optional seed for reproducibility.

        :param shingles: A set of integers representing the shingles.
        :param num_hashes: Number of hash functions to use for the MinHash signature.
        :param seed: Seed for the random number generator for reproducibility.
        """
        self.shingles = shingles
        self.num_hashes = num_hashes
        self.seed = seed
        self.signature = None  # Placeholder for the computed MinHash signature

        # Generate the MinHash signature upon initialization
        self._generate_signature()

    def _generate_signature(self) -> None:
        """
        Generates the MinHash signature for the set of shingles.
        """
        # Use a random generator with the specified seed for reproducibility
        rng = np.random.default_rng(self.seed)
        
        # Define a large prime number to be used in the hash function (modulo operation)
        c = 2**31 - 1

        # Generate unique (a, b) pairs for each hash function, where 'a' and 'b' are random integers
        hash_parameters = rng.integers(low=1, high=c, size=(self.num_hashes, 2))

        # Initialize the signature array with infinity to ensure any hash value will be smaller
        signature = np.full(self.num_hashes, np.inf)

        # Calculate hash values for each shingle and update the signature with minimum values
        for shingle in self.shingles:
            # Compute hash values using the formula h(x) = (ax + b) % c for each hash function
            hash_values = (hash_parameters[:, 0] * shingle + hash_parameters[:, 1]) % c
            
            # Update the signature with the smallest hash value for each hash function
            signature = np.minimum(signature, hash_values)

        # Store the final signature as integers
        self.signature = signature.astype(int)

    def get_signature(self) -> np.ndarray:
        """
        Returns the computed MinHash signature.

        :return: A NumPy array containing the MinHash signature.
        """
        return self.signature
