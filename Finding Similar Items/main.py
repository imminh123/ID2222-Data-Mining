from shingling import Shingling
from compare_sets import CompareSets
from minhashing import MinHash
from compare_signatures import CompareSignatures
from lsh import LSH
import glob
import os
import pandas as pd
import numpy as np

# read txt file from /data/plagiarism/original
original_file = 'data/plagiarism/original/source-document01503.txt'
suspicious = 'data/plagiarism/suspicious'

shingling = Shingling(3)

with open(original_file, 'r') as file:
    text = file.read()

    original_shingles = shingling.shingle(text.lower())
    minhashing = MinHash(original_shingles, 100)
    signature = minhashing.get_signature()

    # read each file in suspicious folder
    # Loop through all .txt files in the folder
    jaccard_similarites = []
    compare_signatures_list = []

    for file_path in glob.glob(os.path.join(suspicious, '*.txt')):
      
        with open(file_path, 'r') as file:
            content = file.read()

            # print only file name, no path
            print(file.name.split('/')[-1])

            suspicious_shingles = shingling.shingle(content.lower())

            compare_sets = CompareSets(original_shingles, suspicious_shingles)
            jaccard_similarity = compare_sets.jaccard_similarity()
            jaccard_similarites.append(jaccard_similarity)
            
            # Generate minhash signature & compare
            minhashing = MinHash(suspicious_shingles, 100)
            suspicious_signature = minhashing.get_signature()
            compare_signatures = CompareSignatures(signature, suspicious_signature)
            compare_signatures_list.append(compare_signatures.compare())

    df = pd.DataFrame({'Jaccard Similarities': jaccard_similarites, 'Minhasing Signature': compare_signatures_list})
    print(df)


# Test LSH
all_signatures = []
for file_path in glob.glob(os.path.join('data/plagiarism', '**/*.txt'), recursive=True):
    with open(file_path, 'r') as file:
        print(file.name)
        content = file.read()
        shingles = shingling.shingle(content.lower())

        minhashing = MinHash(shingles, 100)
        signature = minhashing.get_signature()
        
        all_signatures.append(signature)

# Create a matrix with all the signatures
M = np.array(all_signatures).T
lsh = LSH(M, 0.55, 20)

# Run the LSH algorithm
similar_pairs = lsh.run()

print("Similar document pairs:", similar_pairs)









