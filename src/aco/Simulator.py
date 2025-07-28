from .misc import plot_schedule_gantt


class Simulator:
    def __init__(self, map_instance, arrival_manager, decoder, max_time=480, verbose=True):
        self.current_time = 0
        self.max_time = max_time
        self.verbose = verbose

        self.decoder = decoder
        self.arrival_manager = arrival_manager

        self.map = map_instance
        self.schedule = None

        # Track operations by index that have already started
        self.locked_operations = set()

        self.frozen_at_last_replan = set()

    @property
    def locked_ops(self):
        """
        Return actual Operation objects corresponding to locked operation indices.
        """
        return [op for op in self.map.operations if op.index in self.locked_operations]

    def tick(self, lambda_disruption=1):
        if self.verbose:
            print(f"\n===== Time {self.current_time} =====")

        # Simulate execution of jobs at this time
        self.execute_until(self.current_time)

        # Inject new jobs at this time
        new_ops = self.arrival_manager.get_jobs_arriving_at(self.current_time)
        if new_ops:
            if self.verbose:
                print(
                    f"[t={self.current_time}] Injecting new operations: {new_ops}")

            self.map.add_operations(new_ops)
            self.map.expand_matrices(self.map.operations)

            # Reset makespan, path and cost
            self.map.cycle_best_makespan = float("inf")
            self.map.cycle_best_path = None
            self.map.cycle_best_cost = float("inf")

            self.map.global_best_makespan = float("inf")
            self.map.global_best_path = None
            self.map.global_best_cost = float("inf")

            self.replan(lambda_disruption=lambda_disruption)

        self.current_time += 1

    def replan(self, lambda_disruption=1):
        if self.verbose:
            print(f"[t={self.current_time}] Replanning schedule")

        # Set the locked path for each ant
        for ant in self.map.ants:
            ant.set_locked_path(self.locked_ops)

        # Get the start times for the frozen operations
        frozen_start_times = {
            op.index: self.schedule["start_times"][op.index]
            for op in self.locked_ops
        }

        self.frozen_at_last_replan = set(self.locked_operations)

        if self.current_time == 0:
            previous_start_times = None
        else:
            previous_start_times = self.schedule["start_times"]

        self.map.main(self.decoder, self.locked_operations,
                      self.current_time, local_search=False, frozen_start_times=frozen_start_times, previous_start_times=previous_start_times, lambda_disruption=lambda_disruption)
        self.schedule = self.decoder.decode(
            self.map.global_best_path, self.locked_operations, self.current_time, frozen_start_times=frozen_start_times)

    def execute_until(self, time):
        if not self.schedule:
            return
        start_times = self.schedule["start_times"]
        end_times = self.schedule["end_times"]

        executing = [(op, start_times[op.index], end_times[op.index])
                     for op in self.map.operations
                     if start_times[op.index] <= time < end_times[op.index]]

        for op, _, _ in executing:
            self.locked_operations.add(op.index)

        if self.verbose:
            print(f"[t={time}] Currently executing operations:")
            for op, start, end in executing:
                print(f"  - {op} (from {start} to {end})")

    def run(self, plot_initial_schedule=False, lambda_disruption=1):
        # Initial schedule
        self.replan(lambda_disruption=lambda_disruption)

        # OPtionally plot initial schedule
        if plot_initial_schedule:
            plot_schedule_gantt(self.map.global_best_path, self.schedule,
                                title="Initial schedule", path="/tmp/gantt_initial.png")

        while self.current_time < self.max_time:
            self.tick(lambda_disruption=lambda_disruption)

        print("\nSimulation complete.")
        print(f"Best makespan: {self.map.global_best_makespan}")
        return self.map.global_best_path, self.schedule, self.map.global_best_makespan
