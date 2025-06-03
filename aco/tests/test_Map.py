from aco import Map, Ant
import math
import numpy as np

nodes = [
    (54, 67),
    (54, 62),
    (37, 84),
    (41, 94),
    (2, 99),
    (7, 64),
    (25, 62),
    (22, 60),
    (18, 54),
    (4, 50),
    (13, 40),
    (18, 40),
    (24, 42),
    (25, 38),
    (44, 35),
    (41, 26),
    (45, 21),
    (58, 35),
    (62, 32),
    (82,  7),
    (91, 38),
    (83, 46),
    (71, 44),
    (64, 60),
    (68, 58),
    (83, 69),
    (87, 76),
    (74, 78),
    (71, 71),
    (58, 69)
]

ants = [Ant() for i in range(len(nodes))]

map_instance = Map(nodes, ants)


def test_distance_matrix():
    # Ensure shape is correct
    assert map_instance.distance_matrix.shape == (len(nodes), len(nodes))

    # Ensure the distance is being correctly computed
    assert map_instance.distance_matrix[0, 1] == 5
    assert math.isclose(
        map_instance.distance_matrix[-2, -3], math.sqrt(3**2 + 7**2))


def test_desirability_matrix():
    # Test correct shape
    assert map_instance.desirability_matrix.shape == map_instance.distance_matrix.shape

    # Test values
    assert map_instance.desirability_matrix[1,
                                            2] == 1 / map_instance.distance_matrix[1, 2]
    assert map_instance.desirability_matrix[3,
                                            1] == 1 / map_instance.distance_matrix[3, 1]


def test_pheromone_decay():
    # Test corect shape
    assert map_instance.pheromone_matrix.shape == map_instance.distance_matrix.shape

    current_pheromone_matrix = map_instance.pheromone_matrix.copy()
    map_instance.pheromone_decay()
    new_pheromone_matrix = map_instance.pheromone_matrix

    # Test evaporations
    assert (current_pheromone_matrix *
            map_instance.pheromone_evaporation_coefficient == new_pheromone_matrix).all()


def test_distribute_ants():
    map_instance.distribute_ants()

    # Ensure that ants are evenly distributed among the nodes
    for idx, ant in enumerate(ants):
        assert ant.path[-1] == idx % len(map_instance.nodes)
        assert ant.path[-1] < len(map_instance.nodes)


def test_move_ants():
    old_map_instance_path_lengths = len(map_instance.ants[0].path)
    map_instance.move_ants()

    # Ensure that moving ants increases their path length
    for idx, ant in enumerate(map_instance.ants):
        assert len(ant.path) > old_map_instance_path_lengths


def test_find_paths():
    ants = [Ant() for i in range(len(nodes))]

    map_instance = Map(nodes, ants)

    map_instance.distribute_ants()

    map_instance.find_paths()

    for ant in map_instance.ants:
        # Ensure that the paths are of length len(Nodes) + 1
        assert len(ant.path) == len(map_instance.nodes) + 1
        # Ensure that paths are closed
        assert ant.path[-1] == ant.path[0]
        # Ensure that no duplicates are in the path (except for first and last)
        assert len(ant.path[:-1]) == len(set(ant.path[:-1]))


def test_step():
    ants = [Ant() for i in range(len(nodes))]

    map_instance = Map(nodes, ants)

    map_instance.distribute_ants()

    old_pheromones = map_instance.pheromone_matrix.copy()

    map_instance.step()
    new_pheromones = map_instance.pheromone_matrix.copy()

    # Only true if problem is symmetric
    assert new_pheromones[1, 2] == new_pheromones[2, 1]
    # Ensure paths have been reset
    assert len(map_instance.ants[0].path) == 1
    # Ensure pheromones change after a step
    assert np.sum(old_pheromones - new_pheromones) != 0


def test_square():

    nodes = [(0, 0), (0, 1), (1, 1), (1, 0)]
    ants = [Ant() for i in range(len(nodes))]

    map_instance = Map(nodes, ants)

    map_instance.main()

    assert map_instance.ants[0].calculate_tour_length(map_instance) == 4


def generate_ngon(n, radius=1.0):
    """
    Generate n points evenly spaced on a circle (regular polygon)
    """
    return [(radius * math.cos(2 * math.pi * i / n),
             radius * math.sin(2 * math.pi * i / n)) for i in range(n)]


def run_ngon_test(n, tolerance=1e-2, max_cycles=5000):
    """
    Test ACO on an N-gon inscrined in unit circle.
    Verifies that all ants converge to the minimal perimeter tour.
    """
    nodes = generate_ngon(n)
    ants = [Ant() for _ in range(n)]
    map_instance = Map(nodes, ants)

    map_instance.main(max_cycles=max_cycles)

    # N * side length
    expected_length = 2 * n * math.sin(math.pi / n)

    # Test that all ants have the same (optimal) tour length within tolerance
    for ant in map_instance.ants:
        length = ant.calculate_tour_length(map_instance)
        assert math.isclose(length, expected_length, rel_tol=tolerance), \
            f"Ant tour length {length:.4f} != expected {expected_length:.4f}"

    print(f"Test passed for {
          n}-gon: all ants found tour of length ~{expected_length:.4f}")


def test_ngons():
    n_sides = [4, 5, 6, 7, 8, 9, 10]
    for n in n_sides:
        run_ngon_test(n)
