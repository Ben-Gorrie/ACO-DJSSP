import numpy as np
from random import choices


class Ant:
    def __init__(self):
        # Parameter to control impact of pheromones on path decision making
        self.alpha = 1

        # Parameter to control impact of desirability on path decision making
        # In the case of the TSP, desirability is distance (shorter is better)
        self.beta = 6

        # Param to control how much pheromone ants leave when retracing path
        self.Q = 1

        # Path the ant has taken so far
        # If this were [0, 3], it started at node 0 and went to node 3
        # Nodes are ordered in the same way as they are ordered in Map
        # Note that this path must end up closed
        self.path = []

    def move_probabilities(self, map_instance):
        """
        Returns the probabilities of an ant going from its current state
        to each other node it has not yet visited
        """
        # Get all remaining nodes
        all_nodes = [i for i in range(len(map_instance.nodes))]
        nodes_remaining = list(set(all_nodes) - set(self.path))

        current_position = self.path[-1]

        # Compute probabilities of ant moving to remaining nodes
        numerators = np.array([(map_instance.pheromone_matrix[current_position, y]**self.alpha)
                               * (map_instance.desirability_matrix[current_position, y]**self.beta) for y in nodes_remaining])
        denominator = np.sum(numerators)

        if denominator == 0 or not np.isfinite(denominator):
            # Uniform distribution fallback
            # Necessary to prevent crashing when iterating for too long and some paths fade
            probabilities = np.ones(
                len(nodes_remaining)) / len(nodes_remaining)
        else:
            probabilities = numerators / denominator

        return probabilities, nodes_remaining

    def choose_node(self, map_instance):
        """
        Choose next node given the possible remaining nodes and probabilities
        """
        # Choose a node from the choices available
        probabilities, nodes_remaining = self.move_probabilities(map_instance)
        assert len(probabilities) == len(nodes_remaining)
        return choices(nodes_remaining, weights=probabilities)[0]

    def calculate_tour_length(self, map_instance):
        """
        Compute length of total tour. Should only be called at end of tour.
        """
        total_length = 0

        for i in range(len(self.path) - 1):
            leg1 = self.path[i]
            leg2 = self.path[i + 1]
            total_length += map_instance.distance_matrix[leg1, leg2]

        return total_length

    def deposit_pheromones(self, map_instance):
        """"
        Deposit pheromones on the path visited
        """
        # Reverse the path. Not needed for symmetric problems
        path_back = self.path[::-1]

        tour_length = self.calculate_tour_length(map_instance)

        pheromones_to_deposit = self.Q / tour_length

        # As the path loops, -1 here to avoid out of bounds
        for i in range(len(path_back) - 1):
            current_node = path_back[i]
            next_node = path_back[i + 1]
            map_instance.pheromone_matrix[next_node,
                                          current_node] += pheromones_to_deposit
            # Make symmetric here, but does not have to be the case
            map_instance.pheromone_matrix[current_node,
                                          next_node] += pheromones_to_deposit

    def reset_position(self):
        """
        Reset the ant to its starting position.
        As ants are uniformly distributed, each ant has a different "start"
        """
        self.path = self.path[0:1]

    def move(self, map_instance):
        """
        Move the ant from its current node to the next
        """
        next_node = self.choose_node(map_instance)
        self.path.append(next_node)
