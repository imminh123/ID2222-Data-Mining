edges = [
    (1, 2), (1, 3), (2, 3),
    (3, 4), (4, 5), (5, 3),
    (2, 4), (2, 5), (4, 3)
]

edge_stream = open("web-Google.txt", "r")
edge_stream = [tuple(map(int, line.strip().split())) for line in edge_stream]


# Step 1: Convert edge list to adjacency set for faster look-up
adj = {}
for u, v in edge_stream:
    if u not in adj:
        adj[u] = set()
    if v not in adj:
        adj[v] = set()
    adj[u].add(v)
    adj[v].add(u)

# Step 2: Count triangles
triangle_count = 0
for u in adj:
    for v in adj[u]:
        if v > u:  # avoid double counting
            for w in adj[v]:
                if w > v and w in adj[u]:  # check if (u, w) is an edge
                    triangle_count += 1

print(f"Number of triangles: {triangle_count}")
