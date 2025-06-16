class ScheduleDecoder:
    def __init__(self, operations):
        self.operations = operations
        self.num_jobs = len(set(op.job_id for op in operations))
        self.num_machines = len(set(op.machine_id for op in operations))

    def decode(self, op_sequence):
        """
        Parameters:
            op_sequence (list of Operation): A full sequence of operations

        Returns:
            dict with keys:
                - "start_times": {op.index: start_time}
                - "end_times": {op.index: end_time}
                - "makespan": max end time across all operations
        """
        # Track when each machine and each job is next available
        machine_available_time = dict()
        job_latest_end_time = dict()

        start_times = {}
        end_times = {}

        for op in op_sequence:
            job_id = op.job_id
            machine_id = op.machine_id
            proc_time = op.processing_time

            # Find earliest start time respecting both constraints
            earliest_job_ready = job_latest_end_time.get(job_id, 0)
            earliest_machine_ready = machine_available_time.get(machine_id, 0)
            start_time = max(earliest_job_ready, earliest_machine_ready)

            end_time = start_time + proc_time

            # Record times
            start_times[op.index] = start_time
            end_times[op.index] = end_time

            # Update machine and job availability
            machine_available_time[machine_id] = end_time
            job_latest_end_time[job_id] = end_time

        makespan = max(end_times.values())

        return {
            "start_times": start_times,
            "end_times": end_times,
            "makespan": makespan
        }
