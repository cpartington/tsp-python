import sys


class TSPSolver:
    def __init__(self):
        # TODO write class
        pass


if __name__ == "__main__":
    if sys.argv[0] == "-f":
        cities = []
        with open(sys.argv[1]) as f:
            if sys.argv[1].endswith(".csv"):
                for line in f:
                    city, x, y = line.split(",")
            else:
                for line in f:
                    city, x, y = line.split()
