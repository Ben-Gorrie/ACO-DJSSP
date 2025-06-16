import numpy as np
from random import choices


class Ant:
    def __init__(self, alpha=2, beta=3):
        # Parameter to control impact of pheromones on path decision making
        self.alpha = alpha

        # Parameter to control impact of desirability on path decision making
        self.beta = beta

        # Param to control how much pheromone ants leave when retracing path
        self.Q = 1

        # Path the ant has taken so far
        # Sequence of scheduled operations
        self.path = []

    def get_eligible_operations(self, all_operations):
        """
        Returns operations whose job-predecessors have already been scheduled.
        If an operation is the first in a job, it is automatically eligible
        (unless it has already been scheduled)
        """
        eligible = []
        scheduled_indices = {op.index for op in self.path}

        for op in all_operations:
            # Skip all already scheduled operations
            if op.index in scheduled_indices:
                continue

            # If the operation starts a new job, it is eligible
            if op.operation_id == 0:
                eligible.append(op)
            else:
                # Find the previous operation in the same job
                prev_op = next(
                    (o for o in all_operations
                     if o.job_id == op.job_id and o.operation_id == op.operation_id - 1),
                    None
                )

                if prev_op and prev_op.index in scheduled_indices:
                    eligible.append(op)

        return eligible

    def move_probabilities(self, map_instance, eligible_ops):
        """
        Returns the probabilities of an ant going from its current state
        to each other node it has not yet visited
        """
        from_op = self.path[-1] if self.path else None

        # Compute probabilities of ant moving to remaining nodes
        numerators = []
        for to_op in eligible_ops:
            i = from_op.index if from_op else None
            j = to_op.index

            # Default values if no previous operation (first move)
            pheromones = map_instance.pheromone_matrix[i][j] if from_op else 1
            desirability = map_instance.desirability_matrix[i][j] if from_op else 1

            numerators.append((pheromones ** self.alpha) *
                              (desirability ** self.beta))

        numerators = np.array(numerators)
        denominator = np.sum(numerators)

        if denominator == 0 or not np.isfinite(denominator):
            # Uniform distribution fallback
            # Necessary to prevent crashing when iterating for too long and some paths fade
            probabilities = np.ones(
                len(eligible_ops)) / len(eligible_ops)
        else:
            probabilities = numerators / denominator

        return probabilities

    def choose_operation(self, map_instance, eligible_ops):
        """
        Choose next operation to schedule given the possible remaining operations
        """
        # Choose an operation from the choices available
        probabilities = self.move_probabilities(map_instance, eligible_ops)
        return choices(eligible_ops, weights=probabilities)[0]

    def reset(self):
        """
        Reset the position of the ant
        """
        self.path = []

    def construct_schedule(self, map_instance):
        """
        Build a full schedule in valid order
        """
        self.reset()
        all_ops = map_instance.operations
        while len(self.path) < len(all_ops):
            eligible = self.get_eligible_operations(all_ops)
            op = self.choose_operation(map_instance, eligible)
            self.path.append(op)

    def calculate_makespan(self, decoder):
        """
        Use the decoder to get the makespan of the ant schedule.
        """
        result = decoder.decode(self.path)
        return result["makespan"]

    def deposit_pheromones(self, map_instance, decoder):
        """"
        Deposit pheromones on the path visited
        """
        makespan = self.calculate_makespan(decoder)

        pheromones_to_deposit = self.Q / makespan

        # Deposit pheromones based on makespan
        for i in range(len(self.path) - 1):
            current_op = self.path[i].index
            next_op = self.path[i + 1].index

            map_instance.pheromone_matrix[current_op,
                                          next_op] += pheromones_to_deposit
