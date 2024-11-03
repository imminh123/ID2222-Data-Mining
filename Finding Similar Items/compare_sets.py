"""
CompareSets computes the Jaccard similarity of two sets of shingles
"""

class CompareSets:
    def __init__(self, set_1: set, set_2: set):
        self.set_1 = set_1
        self.set_2 = set_2

    def jaccard_similarity(self):
        intersection = len(self.set_1.intersection(self.set_2))
        union = len(self.set_1.union(self.set_2))
        return intersection / union