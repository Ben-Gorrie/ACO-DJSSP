import numpy as np


class Map:
    """
    Class to keep track of the map, keeping track of nodes, pheromones and ants
    """

    def __init__(self, operations: list, ants: list):
        """
        nodes: list of tuples holding coordinates for the location of nodes
        """
        self.operations = operations
        n_ops = len(self.operations)

        # Matrix to store pheromone levels between nodes
        # The indexing is the same as above, for example:
        # pheromone_matrix[1, 2] = 0.7 means the amount of pheromone deposited between node 1 and 2 is 0.7
        self.pheromone_matrix = np.full((n_ops, n_ops), 0.01)

        # Controls how quickly pheromone trails evaporate
        self.pheromone_evaporation_coefficient = 0.6

        # Matrix to store desirability of transition from node x to node y
        # desirability_matrix[1, 2] = 0.4 means the desirability to go from node 1 to node 2 is 0.4
        self.desirability_matrix = np.zeros((n_ops, n_ops))
        for i in range(n_ops):
            for j in range(n_ops):
                proc_time = self.operations[j].processing_time
                # Prevent division by zero
                self.desirability_matrix[i][j] = 1.0 / proc_time

        # List of ant objects
        self.ants = ants

    def pheromone_decay(self):
        """
        Decays existing pheromone trails
        To be performed before the ants update trails
        """
        self.pheromone_matrix *= self.pheromone_evaporation_coefficient

    def pheromone_update(self, decoder):
        """
        Decays and updates pheromones trails
        """
        self.pheromone_decay()
        # Create new pheromones
        for ant in self.ants:
            ant.deposit_pheromones(self, decoder)

    def construct_solutions(self):
        """
        Find a complete schedule for each ant.
        """
        for ant in self.ants:
            ant.construct_schedule(self)

    def find_best_path(self, decoder):
        """
        Finds the best path found by an ant.
        Returns the path and its associated makespan
        """
        best_path = None
        best_makespan = float("inf")
        for ant in self.ants:
            makespan = ant.calculate_makespan(decoder)
            if makespan < best_makespan:
                best_makespan = makespan
                best_path = ant.path.copy()

        return best_path, best_makespan

    def step(self, decoder):
        """
        Function to be called repeatedly.
        Completes one cycle of all ants finding a path,
        updating the pheromones and resetting them to the start.
        Keeps track of the best path this cycle.
        Returns:
            stagnated (bool): Whether all ants converged to the same tour
            best_path (list): Best path found this cycle
            best_length (float): Length of best path
        """
        # Find possible paths
        self.construct_solutions()

        # Keep the best path found
        best_path, best_makespan = self.find_best_path(decoder)

        # Update pheromones
        self.pheromone_update(decoder)

        # Reset position of ants
        for ant in self.ants:
            ant.reset()

        return best_path, best_makespan

    def main(self, decoder, max_cycles=1000, verbose=True):

        global_best_path = None
        global_best_makespan = float("inf")
        for i in range(max_cycles):
            cycle_best_path, cycle_best_makespan = self.step(decoder)

            if cycle_best_makespan < global_best_makespan:
                global_best_makespan = cycle_best_makespan
                global_best_path = cycle_best_path
                if verbose:
                    print(f"New best path of makespan {
                          global_best_makespan} found at cycle {i + 1}.")

        print(f"Best found path is {
              global_best_path} with a makespan of {global_best_makespan}.")

        return global_best_path, global_best_makespan
