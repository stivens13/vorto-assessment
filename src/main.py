import argparse
import math

import helper

DistanceMatrixSingleton = None

# Calculate Euclidean distance between two points
def euclidean_distance(p1, p2):
    if DistanceMatrixSingleton and DistanceMatrixSingleton.check_key(p1, p2):
        return DistanceMatrixSingleton.get(p1, p2)
    return math.sqrt((p1.x - p2.x) ** 2 + (p1.y - p2.y) ** 2)

def calculate_route_time(route):
    total_time = 0.0
    locations = [depot]
    for load in route:
        locations.extend([load.pickup, load.dropoff])
    locations.append(depot)
    for i in range(len(locations) - 1):
        dist = euclidean_distance(locations[i], locations[i + 1])
        total_time += dist
    return total_time  # , dists

class Route:
    def __init__(self, route, h):
        self.route = route
        self.route_time = calculate_route_time(route)

    def time(self):
        return self.route_time

    def get_route(self):
        return self.route

    def get_item(self, i):
        return self.route[i]

    def insert_load(self, i, load):
        delta = self.calculate_new_load_delta(i, load)
        self.route.insert(i, load)
        self.route_time += delta

    def get_time_with_new_load(self, i, load):
        delta = self.calculate_new_load_delta(i, load)
        return self.route_time + delta

    def update_time(self, h):
        self.route_time = calculate_route_time(self.route)

    def calculate_new_load_delta(self, i, load):
        delta = 0
        right = self.route[i]
        delta += euclidean_distance(load.dropoff, right.pickup)
        delta += euclidean_distance(load.pickup, load.dropoff)
        if self.len() == 1:
            delta -= euclidean_distance(depot, right.pickup)  # subtract previous recorded time
        elif self.len() >= 2:
            left = self.route[i - 1]
            delta -= euclidean_distance(left.dropoff, right.pickup)  # subtract previous recorded time
            delta += euclidean_distance(left.dropoff, load.pickup)
        return delta

    def len(self):
        return len(self.route)

    def __repr__(self):
        return f'Route: {self.len()}, {self.route_time:.1f}, {self.route}'

    def __str__(self):
        return f'len={self.len()}, time={self.route_time:.1f}, route={self.route}'

# Greedy Insertion
class GreedyInsertion:
    def __init__(self, h, loads, depot, max_travel_time=720):
        self.h = h
        self.loads = loads
        self.depot = depot
        self.max_travel_time = max_travel_time

    def solve(self):
        routes = []
        unassigned_loads = set(id for id in range(len(self.loads)))

        while unassigned_loads:
            best_load_id = None
            best_load = None
            best_route = None
            best_load_position = None
            best_increase = float('inf')

            # for load in unassigned_loads:
            for id in unassigned_loads:
                load = self.loads[id]
                for route in routes:
                    for i in range(route.len()):
                        new_route_time = route.get_time_with_new_load(i, load)
                        if new_route_time <= self.max_travel_time:
                            increase = new_route_time - route.time()
                            if increase < best_increase:
                                best_load_id = id
                                best_load = load
                                best_route = route
                                best_load_position = i
                                best_increase = increase

                new_route = Route([load], self.h)
                new_route.update_time(self.h)
                new_route_time = new_route.time()
                if new_route_time <= self.max_travel_time and new_route_time < best_increase:
                    best_load_id = id
                    best_load = load
                    best_route = None
                    best_load_position = 0
                    best_increase = new_route_time

            best_route_time_with_new_load = 0
            if best_route:
                best_route.update_time(self.h)
                best_route_time_with_new_load = best_route.get_time_with_new_load(best_load_position, best_load)
            if best_route is not None and best_route_time_with_new_load <= self.max_travel_time:
                best_route.insert_load(best_load_position, best_load)
            else:
                routes.append(Route([best_load], self.h))

            unassigned_loads.remove(best_load_id)
        return routes

# Calculate the total cost of the solution
def calculate_total_cost(routes, h):
    num_drivers = len(routes)
    total_driven_minutes = sum(calculate_route_time(route.get_route()) for route in routes)
    total_cost = 500 * num_drivers + total_driven_minutes
    return total_cost, total_driven_minutes

# Example usage
depot = helper.Point(0, 0)
MAX_TRAVEL_TIME = 720

def main(args):
    vrp2 = helper.loadProblemFromFile(args.filename)
    global DistanceMatrixSingleton
    DistanceMatrixSingleton = helper.DistanceMatrix(vrp2.loads, depot)
    greedy_insertion = GreedyInsertion(vrp2.h, vrp2.loads, depot, MAX_TRAVEL_TIME)
    best_routes = greedy_insertion.solve()
    count = 0
    for i, route in enumerate(best_routes):
        count += route.len()
        load_ids = [load.id for load in route.get_route()]
        print(load_ids)

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('filename', help='Name of the problem file')
    args = parser.parse_args()
    main(args)
