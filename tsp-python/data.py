class SubTour:
    def __init__(self, tour, cost, matrix, low_bound):
        self.tour = tour
        self.cost = cost
        self.matrix = matrix
        self.low_bound = low_bound
        self.priority = self.get_priority()

    def __lt__(self, other):
        return self.priority < other.priority

    def __gt__(self, other):
        return self.priority > other.priority

    def get_priority(self):
        return self.low_bound / 16 - len(self.tour)
