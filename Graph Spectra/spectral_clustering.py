import numpy as np
import matplotlib.pyplot as plt
import networkx as nx
from networkx import Graph
import scipy.linalg as linalg
from sklearn.cluster import KMeans

def load_graph(file_path):
    """
    Load a weighted or unweighted graph from a file.
    
    Args:
        path (str): Path to the file containing the graph data.
    
    Returns:
        Graph: A NetworkX graph object.
    """
    if file_path == "data/example1.dat":
        G = nx.read_edgelist(file_path, delimiter=",", create_using=Graph)  # Unweighted graph
    else:
        G = nx.read_weighted_edgelist(file_path, delimiter=",", create_using=Graph)  # Weighted graph

    return G

def plot_graph(graph, labels, pos, data):
    """
    Plot the graph with nodes colored by their cluster labels.
    
    Args:
        graph (Graph): The graph to be plotted.
        labels (list): Cluster labels for each node.
        pos (dict): Positions of nodes for the layout.
    """
    nx.draw_networkx(graph, pos=pos, node_size=6, node_color=labels,
                     cmap=plt.cm.Set1, with_labels=False)
    plt.savefig(f"./img/graph_plot_{data}.png", dpi=300, bbox_inches='tight')
    plt.show()

def plot_fiedler(f, data):
    """
    Plot the sorted Fiedler vector.
    
    Args:
        f (list): The Fiedler vector.
    """
    plt.plot(range(len(f)), f)
    plt.xlabel("Node")
    plt.ylabel("Fiedler Vector Value")
    plt.savefig(f"./img/fiedler_plot_{data}.png", dpi=300, bbox_inches='tight')
    plt.show()

def plot_affinity(A, data):
    """
    Visualize the affinity matrix.
    
    Args:
        A (ndarray): The affinity matrix.
    """
    plt.imshow(A, cmap='Blues', interpolation='nearest')
    plt.colorbar()
    plt.savefig(f"./img/affinity_plot_{data}.png", dpi=300, bbox_inches='tight')
    plt.show()

def num_clusters(eigen_values):
    """
    Determine the optimal number of clusters. 
    
    Args:
        eigen_values (list): Eigenvalues of the Laplacian matrix, sorted in ascending order.
    
    Returns:
        int: Optimal number of clusters (k).
    """
    # Calculate the difference between consecutive eigenvalues
    diff = np.diff(eigen_values)
    # Identify the largest gap
    index = np.argmax(diff) + 1
    # The number of clusters is equal to the number of eigenvalues greater than the largest gap
    k = len(eigen_values) - index
    return k

def eigenvector_matrix(L):
    """
    Perform eigenvector decomposition and compute the k smallest eigenvectors.
    
    Args:
        L (ndarray): Normalized Laplacian matrix.
    
    Returns:
        tuple: A tuple containing:
            - X (ndarray): Matrix of the k smallest eigenvectors (n x k).
            - k (int): Optimal number of clusters.
            - X_values (list): Eigenvalues of the Laplacian matrix.
            - fiedler_vec (list): The Fiedler vector (second smallest eigenvector).
    """
    # Compute eigenvalues and eigenvectors
    values, vectors = linalg.eigh(L)
    # Determine the optimal number of clusters
    k = num_clusters(values)
    # Extract and sort the Fiedler vector (second smallest eigenvector)
    fiedler = sorted(vectors[:, 1])
    # Select the k largest eigenvectors
    X = vectors[:, -k:]

    return X, k, fiedler

def normalized_X(X):
    """
    Normalize rows of the eigenvector matrix.
    
    Args:
        X (ndarray): Eigenvector matrix of size (n x k).
    
    Returns:
        ndarray: Normalized eigenvector matrix of size (n x k).
    """
    Y = X / np.sqrt(np.sum(X**2, axis=1)).reshape((-1, 1))
    return Y

def main():
    """
    Main function to load the graph, compute spectral clustering, and plot results.
    """
    path = "data/example2.dat"
    graph = load_graph(path)

    data = 0
    if path.__contains__("example1"):
        data = 1
    elif path.__contains__("example2"):
        data = 2
    
    # Generate node positions for the layout
    pos = nx.spring_layout(graph, seed=42)

    # Convert the graph to an adjacency matrix
    A = nx.to_numpy_array(graph)

    # Compute the diagonal degree matrix
    D = np.diagflat(np.sum(A, axis=1))

    # Compute the normalized Laplacian matrix
    D_inv = np.linalg.inv(np.sqrt(D))
    L = D_inv @ A @ D_inv

    # Perform eigenvector decomposition
    X, k, fiedler = eigenvector_matrix(L)
    # Normalize the eigenvector matrix
    Y = normalized_X(X)
    # Perform k-means clustering on the normalized eigenvectors
    clustering = KMeans(n_clusters=k).fit(Y)
    labels = clustering.labels_
    
    # Plot the results
    plot_graph(graph, labels, pos, data)
    plot_fiedler(fiedler, data)
    plot_affinity(A, data)

if __name__ == "__main__":
    main()
