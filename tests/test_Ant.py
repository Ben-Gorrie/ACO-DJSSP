from aco import Map, Ant
import numpy as np
import math

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

ant = Ant()
path = [1, 5, 4]
ant.path = path


def test_move_probabilities():
    # Make sure that the remaining nodes are correct
    probabilities, nodes_remaining = ant.move_probabilities(map_instance)
    assert (nodes_remaining == np.delete(np.array([i for i in range(
        len(nodes))]), path)).all()
    assert len(nodes_remaining) == len(nodes) - len(path)

    # Ensure probabilites add to 1
    assert math.isclose(np.sum(probabilities), 1)


def test_choose_node():
    # Increase probability the ant goes to node 10
    map_instance.pheromone_matrix[4, 10] *= 10

    counter = 0

    for i in range(100):
        choice = ant.choose_node(map_instance)

        # Ensure the chosen node is not where the ant has already been
        assert choice not in path
        assert choice < len(nodes)

        if choice == 10:
            counter += 1

    # Ensure the ant is weighted towards going to the 10th node
    assert counter > 5


def test_calculate_tour_length():
    map_instance.distance_matrix[1, 5] = 3.4
    map_instance.distance_matrix[5, 4] = 2.7

    # Ensure tour length is calculated correctly
    assert ant.calculate_tour_length(map_instance) == 3.4 + 2.7


def test_deposit_pheromones():
    old_pheromones = map_instance.pheromone_matrix.copy()
    ant.deposit_pheromones(map_instance)
    new_pheromones = map_instance.pheromone_matrix.copy()

    # Ensure that adding new pheromones increases the pheromone trail
    assert old_pheromones[1, 5] < new_pheromones[1, 5]
    assert old_pheromones[5, 4] < new_pheromones[5, 4]


def test_move():
    old_path = ant.path.copy()
    ant.move(map_instance)
    new_path = ant.path.copy()

    # Make sure we are not closing out the path
    if len(old_path) < len(nodes):
        # Ensure that the new path is longer than the old path
        assert len(old_path) < len(new_path)

        # Ensure that the newly added node was not already in the path
        assert new_path[-1] not in old_path


def test_reset_position():
    old_path = ant.path.copy()
    ant.reset_position()

    # Ensure that resetting the position of the ant is done correctly
    assert old_path[0] == ant.path[0]
