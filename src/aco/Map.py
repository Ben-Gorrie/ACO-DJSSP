import numpy as np


class Map:
    """
    Class to keep track of the map, keeping track of nodes, pheromones, ants and best values
    """

    def __init__(self, operations: list, ants: list):
        """
        nodes: list of tuples holding coordinates for the location of nodes
        """
        self.operations = operations
        self.n_ops = len(self.operations)

        # Min and max pheromone values
        self.tau_min = 0.01
        self.tau_max = 10.0

        # Matrix to store pheromone levels between nodes
        # pheromone_matrix[1, 2] = 0.7 means the amount of pheromone deposited between node 1 and 2 is 0.7
        # The initial value is larger than tau_max such that after 1 iteration, all of the values will be tau_max(1)
        self.pheromone_matrix = np.full(
            (self.n_ops, self.n_ops), self.tau_max + 1.5)

        # Controls how quickly pheromone trails evaporate
        self.pheromone_evaporation_coefficient = 0.8

        # Matrix to store desirability of transition from node x to node y
        # desirability_matrix[1, 2] = 0.4 means the desirability to go from node 1 to node 2 is 0.4
        self.desirability_matrix = np.zeros((self.n_ops, self.n_ops))
        for i in range(self.n_ops):
            for j in range(self.n_ops):
                proc_time = self.operations[j].processing_time
                # Prevent division by zero
                self.desirability_matrix[i][j] = 1.0 / proc_time

        # List of ant objects
        self.ants = ants

        # Best current iteration makespan and associated path
        self.cycle_best_makespan = float("inf")
        self.cycle_best_path = None

        # Global best makespan found and associated path
        self.global_best_makespan = float("inf")
        self.global_best_path = None

    def calculate_makespan(self, decoder, path):
        """
        Use the decoder to get the makespan of the schedule.
        """
        result = decoder.decode(path)
        return result["makespan"]

    def calculate_new_pheromone_bounds(self):
        # Find maximum allowed pheromone trail
        self.tau_max = 1 / \
            ((1 - self.pheromone_evaporation_coefficient) * self.global_best_makespan)

        p_best = 0.05

        # Average number of eligible operations available to the ant across all scheduling steps
        # Currently using crude estimate
        # CHANGE THIS BY COMPUTING AVERAGE BRANCHING FACTOR AFTER 10 RUNS
        avg = np.log(self.n_ops)

        n_th_root_p_best = p_best**(1./self.n_ops)

        # Find minimum allowed pheromone trail
        self.tau_min = (self.tau_max * (1 - n_th_root_p_best)
                        ) / ((avg - 1) * n_th_root_p_best)

    def bound_pheromone_trails(self):
        # Limit the existing pheromone trails
        np.clip(self.pheromone_matrix, self.tau_min,
                self.tau_max, out=self.pheromone_matrix)

    def pheromone_decay(self):
        """
        Decays existing pheromone trails
        To be performed before the ants update trails
        """
        self.pheromone_matrix *= self.pheromone_evaporation_coefficient

    def pheromone_update(self, use_global_best_path=False):
        """
        Decays and updates pheromones trails
        """
        # Decay pheromone trails
        self.pheromone_decay()

        # Create new pheromones from solution
        if use_global_best_path:
            pheromones_to_deposit = 1 / self.global_best_makespan
            sol_to_update = self.global_best_path
        else:
            pheromones_to_deposit = 1 / self.cycle_best_makespan
            sol_to_update = self.cycle_best_path

        # Deposit created pheromones
        for i in range(self.n_ops - 1):
            current_op = sol_to_update[i].index
            next_op = sol_to_update[i + 1].index

            self.pheromone_matrix[current_op,
                                  next_op] += pheromones_to_deposit

    def construct_solutions(self):
        """
        Find a complete schedule for each ant.
        """
        for ant in self.ants:
            ant.construct_schedule(self)

    def find_best_path(self, decoder):
        """
        Finds the best path found by an ant in a cycle.
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

    def step(self, decoder, use_global_best_path=False):
        """
        Function to be called repeatedly.
        Completes one cycle of all ants finding a path,
        updating the pheromones, bounding them and resetting ants to the start.
        Keeps track of the best path this cycle.
        """
        # Find possible paths
        self.construct_solutions()

        # Update the best path found this step
        best_path, best_makespan = self.find_best_path(decoder)
        self.cycle_best_path = best_path
        self.cycle_best_makespan = best_makespan

        # Update pheromones
        self.pheromone_update(use_global_best_path)

        # Bound min and max pheromone levels
        self.bound_pheromone_trails()

        # Reset position of ants
        for ant in self.ants:
            ant.reset()

    def main(self, decoder, max_cycles=1000, verbose=True):
        for i in range(max_cycles):
            self.step(decoder)

            # If new global best solution found
            if self.cycle_best_makespan < self.global_best_makespan:
                # Keep track of it
                self.global_best_makespan = self.cycle_best_makespan
                self.global_best_path = self.cycle_best_path

                # Update pheromone bounds
                self.calculate_new_pheromone_bounds()

                if verbose:
                    print(f"New best path of makespan {
                          self.global_best_makespan} found at cycle {i + 1}.")

        if verbose:
            print(f"Best found path is {
                  self.global_best_path} with a makespan of {self.global_best_makespan}.")

        return self.global_best_path, self.global_best_makespan
