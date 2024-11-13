class Shingling:
    def __init__(self, k):
        # k represents the length of each shingle.
        self.k = k

    def shingle(self, text):
        shingles = set()

        for i in range(len(text) - self.k + 1):
            shingle = text[i: i + self.k]

            # hash the shingle
            hash_shingle = hash(shingle)

            # Use the absolute value of the hash to avoid negative values. Hash collisions are considered negligible in this case.
            shingles.add(abs(hash_shingle)) 
        return shingles


