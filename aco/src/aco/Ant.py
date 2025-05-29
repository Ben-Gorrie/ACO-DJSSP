class Ant:
    def __init__(self):
        # Parameter to control impact of pheromones on path decision making
        self.alpha = 1

        # Parameter to control impact of desirability on path decision making
        # In the case of the TSP, desirability is distance (shorter is better)
        self.beta = 6

        # Param to control how much pheromone ants leave when retracing path
        self.Q = 1

        # Path the ant has taken so far
        # If this were [0, 3], it started at node 0 and went to node 3
        self.path = []

    def move_probabilities(self, map_instance):
        """
        Returns the probabilities of an ant going from its current state
        to each other node it has not yet visited
        """
        pass

    def choose_node(self, map_instance):
        """
        Choose next node given the possible remaining nodes and probabilities
        """
        pass

    def calculate_tour_length(self, map_instance):
        """
        Compute length of total tour. Should only be called at end of tour.
        """
        pass

    def deposit_pheremones(self, map_instance):
        """"
        Deposit pheremones on the path visited
        """
        pass

    def move(self, map_instance):
        """
        Move the ant from its current node to the next
        """
        pass
