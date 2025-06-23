from aco import Operation
from pathlib import Path
import json
from collections import defaultdict


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

def find_critical_path(op_sequence, decoder):
    """
    Find the critical path (longest path) through a scheduled list of operations.
    """
    schedule = decoder.decode(op_sequence)
    start_times = schedule["start_times"]
    end_times = schedule["end_times"]

    adjacency = _build_adjacency_list(op_sequence, start_times)
    reverse_adj = _build_reverse_adjacency(adjacency)

    # Find operation that finishes last
    end_op = max(end_times.items(), key=lambda x: x[1])[0]

    # Recursively find longest path ending at end_op
    memo = {}
    backtrack = {}
    _dfs_critical_path(end_op, reverse_adj, start_times, end_times, memo, backtrack)

    return _reconstruct_path(end_op, backtrack)

def _build_adjacency_list(op_sequence, start_times):
    """
    Create a dictionary where each operation points to the operations that must come after it.
    This includes job order (op1 before op2 in a job) and machine order (op1 scheduled before op2 on same machine).
    """
    adjacency = {op.index: [] for op in op_sequence}

    # Job precedence: Add edges between consecutive operations in the same job
    jobs = defaultdict(list)
    for op in op_sequence:
        jobs[op.job_id].append(op)

    for job_id, ops in jobs.items():
        ops.sort(key=lambda op: op.operation_id)
        for i in range(len(ops) - 1):
            before = ops[i]
            after = ops[i + 1]
            adjacency[before.index].append(after.index)

    # Machine precedence: Add edges based on scheduled order on machines
    machines = defaultdict(list)
    for op in op_sequence:
        machines[op.machine_id].append(op)

    for machine_id, ops in machines.items():
        ops.sort(key=lambda op: start_times[op.index])  # Respect the actual schedule
        for i in range(len(ops) - 1):
            before = ops[i]
            after = ops[i + 1]
            adjacency[before.index].append(after.index)

    return adjacency

def _build_reverse_adjacency(adjacency):
    """
    Create the reverse of the adjacency graph.
    If A -> B in the original, then B -> A in the reverse.
    This helps us backtrack from the end of the schedule.
    """
    reverse_adjacency = defaultdict(list)

    for from_node, to_nodes in adjacency.items():
        for to_node in to_nodes:
            reverse_adjacency[to_node].append(from_node)

    return reverse_adjacency

def _dfs_critical_path(current_op, reverse_adj, start_times, end_times, memo, backtrack):
    """
    Recursively find the longest path ending at 'current_op', and remember the best predecessor.

    Args:
        current_op: Operation index currently looking at
        reverse_adj: Who comes before this op
        start_times / end_times: From the decoder
        memo: Cache of longest paths already found
        backtrack: Stores the best previous node for each op in the path
    Returns:
        Length of the longest path ending at current_op
    """
    if current_op in memo:
        return memo[current_op]

    max_length = 0
    best_pred = None

    for prev_op in reverse_adj[current_op]:
        # Recurse to compute path length from predecessor
        path_length = _dfs_critical_path(prev_op, reverse_adj, start_times, end_times, memo, backtrack)

        # Add duration of the predecessor operation
        path_length += end_times[prev_op] - start_times[prev_op]

        if path_length > max_length:
            max_length = path_length
            best_pred = prev_op

    # Remember result
    memo[current_op] = max_length
    if best_pred is not None:
        backtrack[current_op] = best_pred

    return max_length

def _reconstruct_path(end_op, backtrack):
    """
    Reconstruct the critical path by following the backtrack map from end_op back to start.
    """
    path = [end_op]
    while path[-1] in backtrack:
        path.append(backtrack[path[-1]])
    path.reverse()
    return path



