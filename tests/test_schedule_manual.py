from aco import Ant, Map, ScheduleDecoder, Operation


def generate_operations_from_jobs(jobs):
    """
    Converts job list to flat list of Operation objects.

    Parameters:
        jobs: list of jobs
              Each job is a list of (machine_id, processing_time) tuples.

    Returns:
        List of Operation objects with unique indices.
    """
    operations = []
    op_index = 0
    for job_id, job in enumerate(jobs):
        for operation_id, (machine_id, proc_time) in enumerate(job):
            op = Operation(
                index=op_index,
                job_id=job_id,
                operation_id=operation_id,
                machine_id=machine_id,
                processing_time=proc_time
            )
            operations.append(op)
            op_index += 1
    return operations


jobs = [
    [(0, 5), (1, 3)],  # Job 0
    [(1, 4), (0, 2)],  # Job 1
]

# Convert to list of Operation objects
operations = generate_operations_from_jobs(jobs)
ants = [Ant() for _ in range(10)]
map_instance = Map(operations, ants)

decoder = ScheduleDecoder(operations)

best_path, best_makespan = map_instance.main(decoder)
