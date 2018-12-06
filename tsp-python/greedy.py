import math
import time


class GreedySolver:

    def __init__(self, cities):
        self.cities = cities
        self.n = len(cities)

    def solve(self, time_allowance=60.0):
        """
        This algorithm fasts a tour in the graph by starting with a random node
        and iteratively choosing the next city by selecting the city with the
        lowest cost.

        :param time_allowance: the maximum amount of time the algorithm can run
        :return: a results dictionary
        """
        start_time = time.time()
        tour = list()
        best_tour = list()
        count = 0

        # Try different starting cities until one works
        for city in self.cities:
            tour.clear()
            start_city = city
            # Continue until tour is the correct length or time runs out
            while len(tour) < self.n and time.time() - start_time < time_allowance:
                min_cost = math.inf
                min_cities = dict()
                # Iterate through cities and find city with minimum cost
                for p_city in [c for c in self.cities if c not in tour]:
                    cost = start_city.cost_to(p_city)
                    if cost < math.inf:
                        min_cities[cost] = p_city
                        if cost < min_cost:
                            min_cost = cost
                if len(min_cities) == 0:
                    # No city for algorithm to travel to
                    count += 1
                    if len(tour) > len(best_tour):
                        best_tour = tour
                    break
                else:
                    # Add city to tour
                    tour.append(min_cities[min_cost])
                    start_city = min_cities[min_cost]
            if len(tour) == self.n:
                # Quit greedy algorithm when tour is found
                best_tour = tour
                break
        # Build results data
        results = dict()
        end_time = time.time()
        results['cost'] = self.tour_cost(best_tour) if len(best_tour) == self.n else math.inf
        results['time'] = end_time - start_time
        results['soln_count'] = 1 if len(best_tour) == self.n else 0
        results['soln'] = best_tour
        return results

    def tour_cost(self, tour):
        # TODO write function
        pass
