import numpy as np


class Map:
    """
    Class to keep track of the map, keeping track of nodes, pheromones and ants
    """

    def __init__(self, nodes: list, ants: list):
        """
        nodes: list of tuples holding coordinates for the location of nodes
        """
        self.nodes = nodes

        # Matrix to store the distance between nodes
        # Eg: if distance_matrx[1, 2] = 12, the distance between node 1 and node 2 is 12
        # This matrix is currently symmetric, but doesn't need to be
        self.distance_matrix = np.zeros((len(nodes), len(nodes)))
        self._compute_distance_matrix()

        # Matrix to store pheromone levels between nodes
        # The indexing is the same as above, for example:
        # pheromone_matrix[1, 2] = 0.7 means the amount of pheromone deposited between node 1 and 2 is 0.7
        self.pheromone_matrix = np.full((len(nodes), len(nodes)), 0.01)

        # Controls how quickly pheromone trails evaporate
        self.pheromone_evaporation_coefficient = 0.6

        # Matrix to store desirability of transition from node x to node y
        # desirability_matrix[1, 2] = 0.4 means the desirability to go from node 1 to node 2 is 0.4
        self.desirability_matrix = 1 / self.distance_matrix

        # List of ant objects
        self.ants = ants

    def calculate_distance(self, beginning, end):
        """
        Compute the euclidean distance between two nodes
        """
        beg_vec = np.array(beginning)
        end_vec = np.array(end)

        return np.linalg.norm(beg_vec - end_vec)

    def _compute_distance_matrix(self):
        """
        Generate the distance matrix using the euclidean norm
        """
        for node1_idx in range(len(self.nodes)):
            for node2_idx in range(len(self.nodes)):
                distance = self.calculate_distance(
                    self.nodes[node1_idx], self.nodes[node2_idx])
                if distance == 0:
                    distance = 0.01
                self.distance_matrix[node1_idx, node2_idx] = distance

    def pheromone_decay(self):
        """
        Decays existing pheromone trails
        To be performed before the ants update trails
        """
        self.pheromone_matrix *= self.pheromone_evaporation_coefficient

    def distribute_ants(self):
        """
        Uniformly distribute the ants across all the nodes
        """
        for idx, ant in enumerate(self.ants):
            ant.path.append(idx % len(self.nodes))

    def move_ants(self):
        """
        Move all ants one step forward
        """
        for ant in self.ants:
            ant.move(self)
