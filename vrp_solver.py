from distance_matrix import generate_distance_matrix
from googleapi import solve_vrp, print_solution


def get_routes(place_ids, num_vehicles, depot):
    distance_matrix = generate_distance_matrix(place_ids)

    data = {
        'distance_matrix': distance_matrix,
        'num_vehicles': num_vehicles,
        'depot': depot
    }

    result = solve_vrp(data)

    if result:
        data, manager, routing, solution = result

        print_solution(data, manager, routing, solution)

    else:
        print("No solution found.")
