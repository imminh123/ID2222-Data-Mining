import random
from collections import defaultdict

class TriestBase:
    def __init__(self, M):
        if M < 6:
            raise ValueError("M must be at least 6.")
        self.M = M
        self.S = set()  # Sampled edges
        self.t = 0  # Time step
        self.triangles = 0  # Global triangle count
        self.triangle_counters = {}  # Node-specific triangle counts (τu, τv, etc.)
        self.node_neighbors = defaultdict(set)  # Neighbors of each node

    def process_stream(self, stream):
        for edge in stream:  # Expecting stream as a list of tuples like [(+, (u, v)), ...]
            self.t += 1
            print(f"Processing edge {self.t}...")
         
            if self.sample_edge(edge):
                self.update_counters("+", edge)
                self.S.add(edge)

    def sample_edge(self, edge):
        u, v = edge
        if self.t <= self.M:
            return True
        elif self.flip_biased_coin(self.M / self.t):
            removed_edge = random.choice(list(self.S))
            self.S.remove(removed_edge)
            # self.update_counters("-", removed_edge)
            return True
        return False

    def flip_biased_coin(self, prob):
        return random.random() < prob

    def update_counters(self, operation, edge):
        u, v = edge

        if operation == "+":
            self.node_neighbors[u].add(v)
            self.node_neighbors[v].add(u)

        elif operation == "-":
            if v in self.node_neighbors[u]:
                self.node_neighbors[u].remove(v)
            if u in self.node_neighbors[v]:
                self.node_neighbors[v].remove(u)

        common_neighbors = self.node_neighbors[u].intersection(self.node_neighbors[v])

        # Calculate the weight η(t)
        weight = max(1, ((self.t - 1) * (self.t - 2)) / (self.M * (self.M - 1)))
        
       

        self.triangles += weight * len(common_neighbors) # this return unrealistic results
        
        # Update the global triangle counter
        # delta = len(common_neighbors)
        # if operation == "+":
        #     self.triangles += delta
        # elif operation == "-":
        #     self.triangles -= delta   

        # # Update triangle counts for common neighbors
        # for c in common_neighbors:
        #     self.update_counter(c, operation, 1)

        # # Update node-specific triangle counts
        # self.update_counter(u, operation, delta)
        # self.update_counter(v, operation, delta)

    def update_counter(self, key, operation, value):
        if operation == "+":
            self.triangle_counters[key] = self.triangle_counters.get(key, 0) + value
        elif operation == "-":
            self.triangle_counters[key] = self.triangle_counters.get(key, 0) - value

    def get_global_triangle_count(self):
        # Scale the triangle count if needed for unbiased estimation
        return self.triangles

edge_stream = open("web-Google.txt", "r")
edge_stream = [tuple(map(int, line.strip().split())) for line in edge_stream]

triest = TriestBase(M=2500)
triest.process_stream(edge_stream)


print(f"Number of triangles: {triest.get_global_triangle_count()}")