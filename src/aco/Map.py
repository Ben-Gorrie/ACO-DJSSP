import numpy as np
from collections import defaultdict
from .misc import apply_local_search


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
        self.pheromone_evaporation_coefficient = 0.6

        # Count how many operations each job contains
        job_op_counts = defaultdict(int)
        for op in self.operations:
            job_op_counts[op.job_id] += 1

        # Matrix to store desirability of transition from node x to node y
        # desirability_matrix[1, 2] = 0.4 means the desirability to go from node 1 to node 2 is 0.4
        # Fill in desirability matrix using a weighted combination of:
        # - processing time (shorter is better)
        # - number of remaining operations in the job (fewer is better)
        self.desirability_matrix = np.zeros((self.n_ops, self.n_ops))
        for i in range(self.n_ops):
            for j in range(self.n_ops):
                to_op = self.operations[j]
                proc_time = self.operations[j].processing_time

                total_ops_in_job = job_op_counts[to_op.job_id]
                remaining_ops = total_ops_in_job - to_op.operation_id

                # Prevent division by zero
                self.desirability_matrix[i][j] = 1.0 / \
                    (1e-6 + 0.8 * proc_time + 0.2 * remaining_ops)

        # List of ant objects
        self.ants = ants

        # Best current iteration makespan and associated path
        self.cycle_best_makespan = float("inf")
        self.cycle_best_path = None

        # Global best makespan found and associated path
        self.global_best_makespan = float("inf")
        self.global_best_path = None

    def expand_pheromone_matrix(self, new_operations):
        old_n = self.n_ops
        new_n = len(new_operations)

        # Create new pheromone matrix
        new_pheromones = np.full(
            (new_n, new_n), self.tau_max + 1.5)
        # Copy old pheromone values over
        new_pheromones[:old_n, :old_n] = self.pheromone_matrix
        self.pheromone_matrix = new_pheromones

    def expand_desirability_matrix(self, new_operations):
        old_n = self.n_ops
        new_n = len(new_operations)

        # Count how many operations each job contains
        job_op_counts = defaultdict(int)
        for op in new_operations:
            job_op_counts[op.job_id] += 1

        # Create new desirability matrix
        new_desirability_matrix = np.zeros((new_n, new_n))
        # Copy over old values
        new_desirability_matrix[:old_n, :old_n] = self.desirability_matrix
        for i in range(new_n):
            for j in range(old_n, new_n):
                to_op = self.operations[j]
                proc_time = self.operations[j].processing_time

                total_ops_in_job = job_op_counts[to_op.job_id]
                remaining_ops = total_ops_in_job - to_op.operation_id

                # Prevent division by zero
                new_desirability_matrix[i][j] = 1.0 / \
                    (1e-6 + 0.8 * proc_time + 0.2 * remaining_ops)

        self.desirability_matrix = new_desirability_matrix

    def expand_matrices(self, new_operations):
        self.expand_pheromone_matrix(new_operations)
        self.expand_desirability_matrix(new_operations)
        self.n_ops = len(new_operations)

    def add_operations(self, new_ops):
        """
        Append new operations to the operation list
        """
        self.operations.extend(new_ops)

    def calculate_makespan(self, decoder, path, frozen_indices, current_time, frozen_start_times):
        """
        Use the decoder to get the makespan of the schedule.
        """
        result = decoder.decode(path, frozen_indices,
                                current_time, frozen_start_times)
        return result["makespan"]

    def calculate_new_pheromone_bounds(self):
        """
        Calculate the new max and min pheromone bounds.
        This should only be run when a new best path is found.
        """
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

    def pheromone_trail_smoothing(self, pts_delta=0.5):
        """
        Smooth the pheromone trails by pulling them slightly toward tau_max
        to promote exploration.
        """
        self.pheromone_matrix += pts_delta * \
            (self.tau_max - self.pheromone_matrix)

    def construct_solutions(self, frozen_indices):
        """
        Find a complete schedule for each ant.
        """
        # Get frozen ops in correct order from previous global best path
        frozen_index_set = set(frozen_indices)
        if self.global_best_path is not None:
            locked_path = [
                op for op in self.global_best_path if op.index in frozen_index_set]
        else:
            # Fallback arbitrary order for first run
            locked_path = [
                op for op in self.operations if op.index in frozen_index_set]
        for ant in self.ants:
            ant.set_locked_path(locked_path)
            ant.construct_schedule(self)

    def find_best_path(self, decoder, frozen_indices, current_time, frozen_start_times):
        """
        Finds the best path found by an ant in a cycle.
        Returns the path and its associated makespan
        """
        best_path = None
        best_makespan = float("inf")
        for ant in self.ants:
            ant_path = ant.path
            makespan = self.calculate_makespan(
                decoder, ant_path, frozen_indices, current_time, frozen_start_times)
            if makespan < best_makespan:
                best_makespan = makespan
                best_path = ant_path.copy()

        return best_path, best_makespan

    def penalize_path(self, path, penalty=0.1):
        """
        Penalize the chosen path.
        Hopefully can be used to discourage ants going down the same path?
        """
        for i in range(len(path) - 1):
            a = path[i].index
            b = path[i + 1].index
            self.pheromone_matrix[a][b] *= penalty

    def step(self, decoder, frozen_indices, current_time, use_global_best_path=False, local_search=True, frozen_start_times=None):
        """
        Function to be called repeatedly.
        Completes one cycle of all ants finding a path,
        updating the pheromones, bounding them and resetting ants to the start.
        Keeps track of the best path this cycle.
        """
        if not use_global_best_path:
            # Find possible paths
            self.construct_solutions(frozen_indices)

            # Update the best path found this step
            best_path, best_makespan = self.find_best_path(
                decoder, frozen_indices, current_time, frozen_start_times)

            # Use local search if enabled
            if local_search:
                best_path, best_makespan = apply_local_search(
                    best_path, decoder, frozen_indices, current_time)

            self.cycle_best_path = best_path
            self.cycle_best_makespan = best_makespan

        # Update pheromones
        self.pheromone_update(use_global_best_path)

        # Bound min and max pheromone levels
        self.bound_pheromone_trails()

        # Reset position of ants
        for ant in self.ants:
            ant.reset()

    def main(self, decoder, frozen_indices, current_time, job_arrival_manager=None, max_cycles=1000, verbose=True, local_search=True, frozen_start_times=None, reset_pheromones_if_sol_not_changed=0.1):
        # Define the maximum number of iterations where the global best solution does not change
        max_static_iterations = reset_pheromones_if_sol_not_changed * max_cycles

        # soft_static_iterations = max_static_iterations * 0.5

        # Keep track of number of iterations where the global best solution does not change
        n_static_iterations = 0

        for i in range(max_cycles):

            # Perform a cycle
            self.step(decoder, frozen_indices, current_time,
                      local_search=local_search, frozen_start_times=frozen_start_times)

            # If new global best solution found
            if self.cycle_best_makespan < self.global_best_makespan:
                # Keep track of it
                self.global_best_makespan = self.cycle_best_makespan
                self.global_best_path = self.cycle_best_path

                # Update pheromone bounds
                self.calculate_new_pheromone_bounds()

                # Reset nothing changed counter
                n_static_iterations = 0

                if verbose:
                    print(f"New best path of makespan {
                          self.global_best_makespan} found at cycle {i + 1}.")

            # PTS
            if (i % 20 == 0 and i != 0):
                self.pheromone_trail_smoothing()

            # Reset pheromone trails
            if n_static_iterations == max_static_iterations:
                if verbose:
                    print(f"Fully resetting pheromones at cycle {i}")
                self.pheromone_trail_smoothing(1)
                n_static_iterations = 0

            n_static_iterations += 1

        if verbose:
            print(f"Best found path is {
                  self.global_best_path} with a makespan of {self.global_best_makespan}.")

        return self.global_best_path, self.global_best_makespan
