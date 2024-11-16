import itertools
from time import time
import sys

# Save the default standard output
default_stdout = sys.stdout

# Open the file you want to redirect output to
f = open(f"results.txt", "w")

# Change standard output to point to the file
sys.stdout = f


def read_dataset(path):
    """
    Reads the dataset and converts it into a list of transactions.
    Each transaction (row) is represented as a list of integers.

    Args:
        path (str): Path to the dataset file.

    Returns:
        list: A list of transactions, where each transaction is a list of integers.
    """
    transactions = []
    with open(path, "r") as file:
        for line in file:
            # Convert each line to a list of integers
            transaction = [int(num) for num in line.strip().split()]
            transactions.append(transaction)
    return transactions


def get_frequent_itemsets(transactions, support):
    """
    Finds frequent itemsets of size 1 (single items) that meet the support threshold.

    Args:
        transactions (list): List of transactions, where each transaction is a list of integers.
        support (int): Minimum support threshold.

    Returns:
        dict: Dictionary of frequent itemsets of size 1 with their support counts.
    """
    item_counts = {}

    # Count occurrences of each individual item
    for transaction in transactions:
        for item in transaction:
            if item not in item_counts:
                item_counts[item] = 1
            else:
                item_counts[item] += 1

    # Filter items based on the support threshold
    frequent_items = {}
    for item, count in item_counts.items():
        if count >= support:
            frequent_items[frozenset([item])] = count

    return frequent_items


def generate_candidates(frequent_itemsets, k):
    """
    Generates candidate itemsets of size k by combining frequent itemsets of size (k-1).

    Args:
        frequent_itemsets (dict): Frequent itemsets of size (k-1) with their support counts.
        k (int): Desired size of candidate itemsets.

    Returns:
        list: List of candidate itemsets of size k.
    """
    items = list(frequent_itemsets.keys())
    candidates = []

    # Combine pairs of itemsets to create candidates
    for i in range(len(items)):
        for j in range(i + 1, len(items)):
            candidate = items[i] | items[j]  # Union of two itemsets

            # Ensure the candidate is of the desired size
            if len(candidate) == k:
                # Validate that all subsets of size (k-1) are frequent
                valid_candidate = True
                for subset in itertools.combinations(candidate, k - 1):
                    if frozenset(subset) not in frequent_itemsets:
                        valid_candidate = False
                        break
                if valid_candidate:
                    candidates.append(candidate)
    return candidates


def filter_candidates(candidates, transactions, support_threshold):
    """
    Filters candidate itemsets based on their support in the dataset.

    Args:
        candidates (list): List of candidate itemsets to be evaluated.
        transactions (list): List of transactions, where each transaction is a list of integers.
        support_threshold (int): Minimum support threshold.

    Returns:
        dict: Dictionary of frequent itemsets with their support counts.
    """
    candidate_counts = {}

    # Initialize support counts for each candidate
    for candidate in candidates:
        candidate_counts[frozenset(candidate)] = 0

    # Count occurrences of each candidate in transactions
    for transaction in transactions:
        transaction_set = set(transaction)  # Convert to a set for efficient lookup
        for candidate in candidate_counts:
            if candidate.issubset(transaction_set):  # Check if candidate is a subset
                candidate_counts[candidate] += 1

    # Retain only candidates meeting the support threshold
    filtered_candidates = {}
    for candidate, count in candidate_counts.items():
        if count >= support_threshold:
            filtered_candidates[candidate] = count

    return filtered_candidates


def apriori(transactions, support, max_k):
    """
    Implements the A-Priori algorithm to find frequent itemsets of sizes up to max_k.

    Args:
        transactions (list): List of transactions, where each transaction is a list of integers.
        support (int): Minimum support threshold.
        max_k (int): Maximum size of itemsets to consider.

    Returns:
        dict: Dictionary of all frequent itemsets with their support counts.
    """
    # Get frequent itemsets of size 1
    frequent_itemsets = get_frequent_itemsets(transactions, support)

    # Store all frequent itemsets
    all_frequent_itemsets = frequent_itemsets.copy()

    # Generate and filter larger itemsets
    for k in range(2, max_k + 1):
        candidate_itemsets = generate_candidates(frequent_itemsets, k)
        frequent_itemsets = filter_candidates(candidate_itemsets, transactions, support)

        # Stop if no frequent itemsets are found for current size
        if not frequent_itemsets:
            break

        # Add frequent itemsets to the collection
        all_frequent_itemsets.update(frequent_itemsets)

    return all_frequent_itemsets


def generate_association_rules(frequent_itemsets, min_support, min_confidence):
    """
    Generates association rules from the frequent itemsets.

    Args:
        frequent_itemsets (dict): Dictionary of frequent itemsets with their support counts.
        min_support (int): Minimum support threshold.
        min_confidence (float): Minimum confidence threshold.

    Returns:
        list: List of association rules in the form (antecedent, consequent, confidence).
    """
    rules = []

    # Generate rules from frequent itemsets
    for itemset in frequent_itemsets:
        # Skip itemsets of size 1 as they can't form rules
        if len(itemset) < 2:
            continue

        # Generate all possible antecedent-consequent splits
        for r in range(1, len(itemset)):
            for antecedent in itertools.combinations(itemset, r):
                antecedent = frozenset(antecedent)
                consequent = itemset - antecedent

                # Check if both antecedent and consequent are valid
                if (
                    consequent
                    and antecedent in frequent_itemsets
                    and itemset in frequent_itemsets
                ):
                    support_antecedent = frequent_itemsets[antecedent]
                    support_itemset = frequent_itemsets[itemset]

                    # Calculate confidence
                    confidence_value = support_itemset / support_antecedent

                    # Add the rule if thresholds are met
                    if (
                        support_itemset >= min_support
                        and confidence_value >= min_confidence
                    ):
                        rules.append((antecedent, consequent, confidence_value))

    return rules


def main():
    start = time()  # Start timing

    # Read the dataset
    transactions = read_dataset("data/T10I4D100K.dat")
    num_transactions = len(transactions)

    # Define thresholds
    support_threshold = 0.01  # 1% of total transactions (from lecture slides)
    support = int(num_transactions * support_threshold)
    confidence = 0.6  # Minimum confidence
    k_tuple = 3  # Maximum size of itemsets to consider

    # Run A-Priori algorithm
    frequent_itemsets = apriori(transactions, support, k_tuple)

    # Generate association rules
    rules = generate_association_rules(frequent_itemsets, support, confidence)

    for itemset, support_count in frequent_itemsets.items():
        print(f"{set(itemset)}: {support_count}\n")

    for antecedent, consequent, confidence in rules:
        print(
            f"{set(antecedent)} -> {set(consequent)} with confidence: {confidence:.2f}\n"
        )

    print("Total time:", time() - start)


# Execute the program
if __name__ == "__main__":
    main()

# Change standard output back to default
sys.stdout = default_stdout

# Close the file
f.close()
