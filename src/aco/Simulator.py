class Simulator:
    def __init__(self, map_instance, arrival_manager, decoder, max_time=480, verbose=True):
        self.current_time = 0
        self.max_time = max_time
        self.verbose = verbose

        self.decoder = decoder
        self.arrival_manager = arrival_manager

        self.map = map_instance
        self.schedule = None

        # Track operations that have already started
        self.locked_operations = set()

    def tick(self):
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

            # Reset makespan and path
            self.map.cycle_best_makespan = float("inf")
            self.map.cycle_best_path = None

            self.map.global_best_makespan = float("inf")
            self.map.global_best_path = None

            self.replan()

        self.current_time += 1

    def replan(self):
        if self.verbose:
            print(f"[t={self.current_time}] Replanning schedule")

        self.map.main(self.decoder, self.locked_operations)
        self.schedule = self.decoder.decode(self.map.global_best_path)

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

    def run(self):
        # Initial schedule
        self.replan()

        while self.current_time < self.max_time:
            self.tick()

        print("\nSimulation complete.")
        print(f"Best makespan: {self.map.global_best_makespan}")
        return self.map.global_best_path, self.schedule, self.map.global_best_makespan
