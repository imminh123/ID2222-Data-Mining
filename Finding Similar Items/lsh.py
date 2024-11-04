from math import ceil
from collections import defaultdict
import numpy as np
from itertools import combinations
from compare_signatures import CompareSignatures


class LSH:
    def __init__(self, M: np.ndarray, threshold: float, bands: int):
        """
        Initialize the LSH class with minhash signatures, similarity threshold, and the number of bands.
        
        :param M: Matrix having as columns the signatures of the documents.
        :param threshold: Threshold for the similarity.
        :param bands: Number of bands.
        """
        self.M = M
        self.threshold = threshold
        self.bands = bands
        self.num_hashes = M.shape[0]

    def hash_band(self, band: np.ndarray) -> np.ndarray:
        """
        Hashes the band of each document using the sum of the rows of the band.
        The idea is that similar documents will have similar hash values hence identical sum of the rows in some of the bands.
        
        :param band: Matrix of shape (band_length, documents).
        :return: An array of shape (documents,) containing the hashed band for each document.
        """
        return np.sum(a=band, axis=0)


    def find_candidates(self) -> set[tuple[int, int]]:
        """
        Identifies all pairs of documents with estimated similarity above the threshold.
        
        :return: Set of candidate document pairs.
        """
        # Number of rows in each band
        band_length = ceil(self.num_hashes / self.bands)
        candidates = set()

        for start in range(0, self.num_hashes, band_length):
            end = min(start + band_length, self.num_hashes)
            band = self.M[start:end, :]
            hashed_band = self.hash_band(band)
            
            # Documents with the same hash value in a band are likely to be similar, group them in collision sets
            collisions = defaultdict(set)
            for doc_id, hash_val in enumerate(hashed_band):
                collisions[hash_val].add(doc_id)
            
            # Generate candidate pairs from documents with the same hash
            for collision in collisions.values():
                candidates.update(combinations(collision, 2))

        return candidates

    def filter_candidates(self, candidates: set[tuple[int, int]]) -> set[tuple[int, int]]:
        """
        Filters candidate pairs based on a similarity threshold.
        
        :param candidate_pairs: Set of candidate index pairs.
        :return: Set of index pairs with similarity above the threshold.
        """
        def is_similar_enough(pair):
            sig1 = self.M[:, pair[0]]
            sig2 = self.M[:, pair[1]]
            return CompareSignatures(sig1, sig2).compare() >= self.threshold

        return set(filter(is_similar_enough, candidates))



    def run(self) -> set[tuple[int, int]]:
        """
        Runs the LSH algorithm to find similar document pairs.
        
        :return: Set of pairs of document indices with similarity larger than the threshold.
        """
        candidates = self.find_candidates()
        return self.filter_candidates(candidates)
    