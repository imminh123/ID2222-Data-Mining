from typing import Set, DefaultDict, FrozenSet
from collections import defaultdict
from scipy.stats import bernoulli
import random
import time
import sys

# Save the default standard output
default_stdout = sys.stdout

# Open the file you want to redirect output to
f = open(f"results.txt", "w")

# Change standard output to point to the file
sys.stdout = f

def get_edge(row: str) -> FrozenSet[int]:
    """
    Parses a line to extract an edge as a frozenset of two integers.

    :param row: A string representing an edge in the graph (e.g., "1 2").
    :return: A frozenset containing the two integer nodes of the edge.
    """
    return frozenset([int(node) for node in row.split()])


class TriestBase:
    """
    Implements the TRIÈST base algorithm for estimating the number of triangles in a graph
    from a stream of edges.
    """

    def __init__(self, path: str, M: int):
        """
        Initializes the algorithm with the path to file and memory constraints.

        :param path: Path to the file containing the edge stream.
        :param M: Maximum memory size (number of edges to store).
        """
        if M < 6:
            raise ValueError("Memory size M must be at least 6.")

        self.path: str = path
        self.M: int = M  # Maximum number of edges to store
        self.S: Set[FrozenSet[int]] = set()  # Set of sampled edges
        self.t: int = 0  # Total number of edges processed
        self.tau_local: DefaultDict[int, int] = defaultdict(
            int
        )  # Per-node triangle counts
        self.tau: int = 0  # Global triangle count

    @property
    def xi(self) -> float:
        return max(
            1.0,
            (self.t * (self.t - 1) * (self.t - 2))
            / (self.M * (self.M - 1) * (self.M - 2)),
        )

    def reservoir_sample_edge(self, t: int) -> bool:
        """
        Determines whether to include the current edge in the memory using reservoir sampling.
        If memory is full, a random edge is removed to make space.

        :param t: The total number of edges observed so far.
        :return: True if the edge is accepted, False otherwise.
        """
        if t <= self.M:
            return True  # Always accept if memory is not full
        elif bernoulli.rvs(p=self.M / t):  # Probabilistic acceptance
            # Remove a random edge to make space
            edge_to_remove = random.choice(list(self.S))
            self.S.remove(edge_to_remove)
            self.update_counters(
                edge_to_remove, decrement=True
            )  # Update triangle counts
            return True
        else:
            return False

    def update_counters(self, edge: FrozenSet[int], decrement: bool) -> None:
        """
        Updates the counters related to estimating the number of triangles. Updates happen by incrementing
        or decrementing the counters.

        :param edge: The edge involved in the update
        :param decrement: If True, decrement the counters; otherwise, increment them
        :return: None
        """
        common_neighbourhood = self.common_neighbours(edge)
        adjustment = -1 if decrement else 1

        # Update the triangle count for the common neighbors
        for node in common_neighbourhood:
            self.tau += adjustment
            self.tau_local[node] += adjustment

        # Update the triangle count for the nodes in the edge
            for node in edge:
                self.tau_local[node] += adjustment

    def common_neighbours(self, edge: FrozenSet[int]) -> Set[int]:
        """
        Identifies the common neighbors of the two vertices in an edge.

        :param edge: The edge whose common neighbors are being computed.
        :return: A set of common neighbors.
        """
        # Extract neighbors for both vertices in the edge
        neighbors = []
        for node in edge:
            node_neighbors = set()

            # Loop through the edges in memory and find the neighbors of the node
            for e in self.S:
                if node in e:
                    for neighbor in e:
                        if neighbor != node:
                            node_neighbors.add(neighbor)

            neighbors.append(node_neighbors)

        # Return the intersection of neighbors of both vertices
        return neighbors[0].intersection(neighbors[1])

    def run(self) -> float:
        """
        Executes the TRIÈST Base algorithm to estimate the global triangle count.

        :return: The estimated number of triangles in the graph.
        """
        print("Running the algorithm with M = {}.".format(self.M))

        with open(self.path, "r") as f:

            for line in f:
                edge = get_edge(line)  # Parse the edge
                self.t += 1  # Increment the processed edge count

                if self.reservoir_sample_edge(self.t):
                    self.S.add(edge)  # Add edge to memory
                    self.update_counters(edge, decrement=False)  # Update counters

                # if self.t % 1000 == 0:
                #     print(
                #         f"The current estimate for the number of triangles is {self.xi * self.tau}."
                #     )

            print(f"The estimated number of triangles is {self.xi * self.tau}.")
            return self.xi * self.tau


class TriestImproved:
    """
    Implements an optimized version of TRIÈST with a different triangle update strategy
    to improve accuracy and efficiency in edge sampling.
    """

    def __init__(self, path: str, M: int):
        """
        Initializes the algorithm with the path to file and memory constraints.

        :param path: Path to the file containing the edge stream.
        :param M: Maximum memory size (number of edges to store).
        """
        if M < 6:
            raise ValueError("Memory size M must be at least 6.")

        self.path: str = path
        self.M: int = M  # Maximum number of edges to store
        self.S: Set[FrozenSet[int]] = set()  # Set of sampled edges
        self.t: int = 0  # Total number of edges processed
        self.tau_local: DefaultDict[int, int] = defaultdict(
            int
        )  # Per-node triangle counts
        self.tau: int = 0  # Global triangle count

    @property
    def eta(self) -> float:
        """
        Computes the scaling factor for the improved algorithm.

        :return: Scaling factor based on the processed edge count and memory size.
        """
        return max(1.0, ((self.t - 1) * (self.t - 2)) / (self.M * (self.M - 1)))

    def reservoir_sample_edge(self, t: int) -> bool:
        """
        Determines whether to include the current edge in the memory using reservoir sampling.
        If memory is full, a random edge is removed to make space.

        :param t: The total number of edges observed so far.
        :return: True if the edge is accepted, False otherwise.
        """
        if t <= self.M:
            return True  # Always accept if memory is not full
        elif bernoulli.rvs(p=self.M / t):  # Probabilistic acceptance
            # Remove a random edge to make space
            edge_to_remove = random.choice(list(self.S))
            self.S.remove(edge_to_remove)
            self.update_counters(
                edge_to_remove
            )  # Update triangle counts
            return True
        else:
            return False

    def update_counters(self, edge: FrozenSet[int]) -> None:
        """
        Updates the counters related to estimating the number of triangles. Updates happen by incrementing
        or decrementing the counters based on the `decrement` flag.

        :param edge: The edge involved in the update
        :param decrement: If True, decrement the counters; otherwise, increment them
        :return: None
        """
        common_neighbourhood = self.common_neighbours(edge)

        for node in common_neighbourhood:
            self.tau += self.eta
            self.tau_local[node] += self.eta

            for node in edge:
                self.tau_local[node] += self.eta

    def common_neighbours(self, edge: FrozenSet[int]) -> Set[int]:
        """
        Identifies the common neighbors of the two vertices in an edge.

        :param edge: The edge whose common neighbors are being computed.
        :return: A set of common neighbors.
        """
        # Extract neighbors for both vertices in the edge
        neighbors = []
        for node in edge:
            node_neighbors = set()

            # Loop through the edges in memory and find the neighbors of the node
            for e in self.S:
                if node in e:
                    for neighbor in e:
                        if neighbor != node:
                            node_neighbors.add(neighbor)

            neighbors.append(node_neighbors)

        # Return the intersection of neighbors of both vertices
        return neighbors[0].intersection(neighbors[1])

    def run(self) -> float:
        """
        Executes the TRIÈST Improved algorithm to estimate the global triangle count.

        :return: The estimated number of triangles in the graph.
        """
        print("Running the algorithm with M = {}.".format(self.M))

        with open(self.path, "r") as f:

            for line in f:
                edge = get_edge(line)  # Parse the edge
                self.t += 1  # Increment the processed edge count

                self.update_counters(edge)  # Update counters

                if self.reservoir_sample_edge(self.t):
                    self.S.add(edge)  # Add edge to memory

                # if self.t % 1000 == 0:
                #     print(
                #         f"The current estimate for the number of triangles is {self.tau}."
                #     )
            print(f"The estimated number of triangles is {self.tau}.")

            return self.tau


if __name__ == "__main__":
    start_time = time.time()
    TriestBase(
        path="./data/facebook_combined.txt",
        M=5000,
    ).run()
    print(f"Time to run Triest Base: {time.time() - start_time:.2f} seconds")

    start_time = time.time()
    TriestImproved(
        path="./data/facebook_combined.txt",
        M=1000,
    ).run()
    print(f"Time to run Triest Improved: {time.time() - start_time:.2f} seconds")

# Change standard output back to default
sys.stdout = default_stdout

# Close the file
f.close()