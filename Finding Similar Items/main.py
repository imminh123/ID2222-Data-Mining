from shingling import Shingling
from compare_sets import CompareSets
from minhashing import MinHash
from compare_signatures import CompareSignatures
import glob
import os

text = "The quick brown fox jumps over the lazy dog"
text_2 = "The quick brown dog jumps over the lazy fox"

# read txt file from /data/plagiarism/original
original_file = 'data/plagiarism/original/source-document01501.txt'
suspicious = 'data/plagiarism/suspicious'

with open(original_file, 'r') as file:
    text = file.read()

    shingling = Shingling(5)
    original_shingles = shingling.shingle(text.lower())

    # read each file in suspicious folder
    # Loop through all .txt files in the folder
    for file_path in glob.glob(os.path.join(suspicious, '*.txt')):
        with open(file_path, 'r') as file:
            content = file.read()
            suspicious_shingles = shingling.shingle(content.lower())

            compare_sets = CompareSets(original_shingles, suspicious_shingles)
            jaccard_similarity = compare_sets.jaccard_similarity()
            print(jaccard_similarity)

    minhashing = MinHash(original_shingles, 100)
    signature = minhashing.get_signature()
    print(signature)






