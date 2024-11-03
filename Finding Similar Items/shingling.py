class Shingling:
    def __init__(self, k):
        self.k = k

    def shingle(self, text):
        shingles = set()
        for i in range(len(text) - self.k + 1):
            shingle = text[i: i + self.k]

            # hash the shingle
            hash_shingle = hash(shingle)
            shingles.add(abs(hash_shingle)) # the hash collision is negligible
        return shingles


