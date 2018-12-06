import heapq
import math
import time

from data import SubTour


class BranchBoundSolver:

    def __init__(self, cities, bssf):
        self.cities = cities
        self.n = len(cities)
        self.bssf = bssf
        self.solutions = 0
        self.created = 0
        self.pruned = 0
        self.best_tour = None
        self.q = []
        self.q_max_size = 0

    def solve(self, time_allowance):
        """
        Finds the minimum tour, where each city is visited once.

        :param time_allowance: the maximum amount of time the algorithm can run
        :return: a dictionary of result statistics
        """
        start_time = time.time()
        start_node = self.cities[0]
        bound_matrix, lower_bound = self.init_bound_matrix(self.cities)
        # Set up queue
        item = SubTour([start_node], 0, bound_matrix, lower_bound)
        heapq.heappush(self.q, item)
        self.created += 1

        while len(self.q) > 0 and time.time() - start_time < time_allowance:
            sub_tour = heapq.heappop(self.q)
            # Don't add to queue if low bound is larger than BSSF
            if sub_tour.low_bound > self.bssf:
                self.pruned += 1
            else:
                # Make children
                for i in range(self.n):
                    self.created += 1
                    self.make_child(sub_tour, i)
        return self.build_results(time.time() - start_time)

    def make_child(self, sub_tour, city_index):
        """
        Creates a new child and decides whether to add it to the queue
        or not.

        :param sub_tour: the parent tour
        :param city_index: the index of the city to be added
        """
        tour = sub_tour.tour[:]
        from_city = tour[-1]
        to_city = self.cities[city_index]

        # Check if city is already in the tour
        if to_city in tour:
            self.pruned += 1
            return

        cost_to_travel = from_city.costTo(to_city)
        # Check if cost to travel is infinite
        if math.isinf(cost_to_travel):
            self.pruned += 1
            return

        # Lengthen tour and get cost information
        cost = sub_tour.cost + cost_to_travel
        if cost >= self.bssf:
            self.pruned += 1
            return
        tour += [to_city]

        # Check if tour is completed
        if len(tour) == self.n:
            return self.check_solution(tour, cost)

        # Create bounded matrix and find new lower bound
        bound_matrix = [l[:] for l in sub_tour.matrix]
        add_low = self.update_bound_matrix(bound_matrix, from_city.index(), to_city.index())
        low_bound = sub_tour.low_bound + add_low
        if low_bound > self.bssf:
            # Don't add child to queue
            self.pruned += 1
            return
        else:
            item = SubTour(tour, cost, bound_matrix, low_bound)
            heapq.heappush(self.q, item)
            if len(self.q) > self.q_max_size:
                self.q_max_size = len(self.q)

    def check_solution(self, tour, cost):
        """
        Given a full-length tour, check if it is a solution or not.

        :param cost: the cost of the tour without the cost from final to first
        :param tour: the potential tour
        """
        to_origin_cost = tour[-1].costTo(tour[0])
        if math.isinf(to_origin_cost):
            # Incomplete tour
            self.pruned += 1
        else:
            # Potential solution found
            cost += to_origin_cost
            if cost > self.bssf:
                self.pruned += 1
                return
            # Update best tour
            if cost < self.bssf:
                print("Solution: {} (cost {})"
                      .format("->".join([c.name() for c in tour]), cost))
                self.solutions += 1
                self.bssf = cost
                self.best_tour = tour
            elif self.best_tour is None:
                self.best_tour = tour

    def build_results(self, total_time):
        """
        Builds the results dictionary.

        :param total_time: the running time of the algorithm
        :return: a results dictionary
        """
        print("Building results...")
        results = {}
        if self.best_tour is not None:
            best = TSPSolution(self.best_tour)
            results['cost'] = best.cost
            results['soln'] = best
        results['time'] = total_time
        results['count'] = self.solutions
        results['max'] = self.q_max_size
        results['total'] = self.created
        results['pruned'] = self.pruned
        return results

    """ Bound Matrix Operations """

    def init_bound_matrix(self, cities):
        """
        Builds the initial bound matrix for a set of cities.

        :param cities: a list of City objects
        :return: the created bound matrix
        """
        matrix = []
        for _ in range(self.n):
            matrix += [[]]
        # Fill matrix with cost values
        for i in range(self.n):
            for j in range(self.n):
                if i == j:
                    matrix[i] += [math.inf]
                else:
                    matrix[i] += [cities[i].costTo(cities[j])]
        low_bound = self.reduce_bound_matrix(matrix)
        return matrix, low_bound

    def update_bound_matrix(self, matrix, row, col):
        """
        Updates a matrix with infinities given a row and column.

        :param matrix: the matrix to update
        :param row: the row index
        :param col: the column index
        :return: the new lower bound for the matrix
        """
        extra_cost = matrix[row][col]
        # Row
        matrix[row] = [math.inf] * self.n
        # Column
        for i in range(self.n):
            matrix[i][col] = math.inf
        # Extra index to prevent looping
        matrix[col][row] = math.inf
        return extra_cost + self.reduce_bound_matrix(matrix)

    def reduce_bound_matrix(self, matrix):
        """
        Reduces a matrix's columns and rows so that there is either
        a zero in each or all infinities.

        :param matrix: the matrix to reduce
        :return: value to add to the lower bound
        """
        lower_bound = 0
        # Row
        for i in range(self.n):
            min_val = min(matrix[i])
            if not math.isinf(min_val) and min_val != 0:
                for j in range(self.n):
                    matrix[i][j] -= min_val
                lower_bound += min_val
        # Column
        for j in range(self.n):
            min_val = min([matrix[i][j] for i in range(self.n)])
            if not math.isinf(min_val) and min_val != 0:
                for i in range(self.n):
                    matrix[i][j] -= min_val
                lower_bound += min_val
        return lower_bound

    """ Debug Functions """

    def print_matrix(self, matrix):
        string = list()
        max_val_size = len(str(max([max(v) for v in matrix])))
        # Print rows
        for row in matrix:
            for col in row:
                string.append("{val: >{fill}}  ".format(val=col if col != math.inf else "-",
                                                        fill=max_val_size + 1))
            print(''.join(string))
            string.clear()
