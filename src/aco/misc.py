from aco import Operation
from pathlib import Path
import json


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


def parse_taillard_to_operations(path):
    """
    Parses a Taillard-format JSSP instance file and returns a flat list of Operation objects.

    Parameters:
        path (str or Path): Path to the Taillard-format instance file.

    Returns:
        List[Operation]: Flat list of Operation objects.
    """
    path = Path(path)
    with open(path, "r") as f:
        lines = f.readlines()

    # Remove comments and blank lines
    content_lines = [line.strip() for line in lines if line.strip()
                     and not line.startswith("#")]

    jobs = []

    # Each subsequent line defines a job except the first line
    for line in content_lines[1:]:
        # Split and convert into integers
        line_split_ints = [int(a) for a in line.split()]

        # Get machine ids and processing times
        machines = line_split_ints[::2]
        proc_times = line_split_ints[1::2]

        # Zip them together to get a list of (id, proc_times) pairs
        machine_proc_time_pair = list(zip(machines, proc_times))

        # Add to jobs list
        jobs.append(machine_proc_time_pair)

    # Convert into lsit of Operations and return
    return generate_operations_from_jobs(jobs)


def load_instance_with_optimum(jsplib_path, instance_name):
    metadata_path = Path(jsplib_path) / "instances.json"

    with open(metadata_path, "r") as f:
        instance_metadata = json.load(f)

    matched_entry = next(
        (item for item in instance_metadata if item["name"] == instance_name), None)

    if not matched_entry:
        raise ValueError(f"No metadata found for instance '{
                         instance_name}' in {metadata_path}")

    optimum = matched_entry["optimum"]

    instance_path = Path(jsplib_path) / matched_entry["path"]

    return optimum, parse_taillard_to_operations(instance_path)
