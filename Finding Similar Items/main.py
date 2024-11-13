from shingling import Shingling
from compare_sets import CompareSets
from minhashing import MinHash
from compare_signatures import CompareSignatures
from lsh import LSH
import glob
import os
import pandas as pd
import numpy as np
import time
import sys

# Save the default standard output
default_stdout = sys.stdout

# Open the file you want to redirect output to
f = open(f"results.txt", "w")

# Change standard output to point to the file
sys.stdout = f

# Paths for original and suspicious files
original_file = "data/plagiarism/original/source-document01503.txt"
suspicious_dir = "data/plagiarism/suspicious"

# Initialize Shingling with k-shingle length of 3
shingling = Shingling(3)

# Measure time for reading and shingling the original document
start_time = time.time()
with open(original_file, "r") as file:
    text = file.read().lower()
    original_shingles = shingling.shingle(text)
print(
    f"Time to read and shingle original document: {time.time() - start_time:.2f} seconds"
)

# Measure time for MinHash generation for the original document
start_time = time.time()
minhashing = MinHash(original_shingles, 100)
original_signature = minhashing.get_signature()
print(
    f"Time to generate MinHash signature for original document: {time.time() - start_time:.2f} seconds"
)

# Initialize lists for storing Jaccard similarities and signature comparisons
jaccard_similarities = []
signature_similarities = []
suspicious_files = []

# Process each file in the suspicious folder
start_total_time = time.time()  # Start timing for the entire suspicious file processing
for file_path in glob.glob(os.path.join(suspicious_dir, "*.txt")):
    with open(file_path, "r") as file:
        # Extract content and file name for display
        content = file.read().lower()
        filename = os.path.basename(file.name)
        suspicious_files.append(filename)

        # Calculate Jaccard Similarity
        start_time = time.time()
        suspicious_shingles = shingling.shingle(content)
        compare_sets = CompareSets(original_shingles, suspicious_shingles)
        jaccard_similarity = compare_sets.jaccard_similarity()
        jaccard_similarities.append(jaccard_similarity)
        print(
            f"Time to calculate Jaccard similarity for {filename}: {time.time() - start_time:.2f} seconds"
        )

        # Generate MinHash signature for the suspicious document and compare
        start_time = time.time()
        suspicious_minhashing = MinHash(suspicious_shingles, 100)
        suspicious_signature = suspicious_minhashing.get_signature()
        compare_signatures = CompareSignatures(original_signature, suspicious_signature)
        signature_similarity = compare_signatures.compare()
        signature_similarities.append(signature_similarity)
        print(
            f"Time to generate and compare MinHash signature for {filename}: {time.time() - start_time:.2f} seconds"
        )

# End timing for suspicious file processing
print(
    f"\nTotal time to process all suspicious files: {time.time() - start_total_time:.2f} seconds"
)

# Create a DataFrame to store results
df = pd.DataFrame(
    {
        "File": suspicious_files,
        "Jaccard Similarity": jaccard_similarities,
        "MinHash Signature Similarity": signature_similarities,
    }
)
# Set pandas display options to show all columns
pd.set_option("display.max_columns", None)
pd.set_option("display.width", None)

# Print the DataFrame with all columns visible
print(df)


# LSH: Collect signatures for all documents (including suspicious and original)
all_signatures = []

start_time = time.time()  # Start timing for LSH signature generation
index = 0
for file_path in glob.glob(os.path.join("data/plagiarism", "**/*.txt"), recursive=True):
    with open(file_path, "r") as file:
        # print processing file name (exclude path) and index auto increment
        print(f"{index}: {os.path.basename(file_path)}")
        index += 1

        content = file.read().lower()
        shingles = shingling.shingle(content)

        # Generate and collect MinHash signature
        minhashing = MinHash(shingles, 100)
        signature = minhashing.get_signature()
        all_signatures.append(signature)
print(f"\nTime to generate signatures for LSH: {time.time() - start_time:.2f} seconds")

# Create signature matrix for LSH
signature_matrix = np.array(all_signatures).T

# Measure time for running LSH
start_time = time.time()
# s = (1/b)^(1/r) = (1/20)^(1/5) = 0.55
lsh = LSH(signature_matrix, threshold=0.55, bands=20)
similar_pairs = lsh.run()
print(
    f"Time to run LSH and find similar document pairs: {time.time() - start_time:.2f} seconds"
)

# Output similar document pairs
print("Similar document pairs:", similar_pairs)

# Change standard output back to default
sys.stdout = default_stdout

# Close the file
f.close()
