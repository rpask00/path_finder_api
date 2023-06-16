import json

from distance_matrix import generate_distance_matrix
from get_route import get_route
from googleapi import solve_vrp, parse_solution


def vrp_solve_main(place_ids, num_vehicles, depot=0):
    distance_matrix = generate_distance_matrix(place_ids)

    data = {
        'distance_matrix': distance_matrix,
        'num_vehicles': num_vehicles,
        'depot': depot
    }

    result = solve_vrp(data)

    if result:
        data, manager, routing, solution = result

        routes_order, max_route_distance = parse_solution(data, manager, routing, solution)
        routes = []

        for vehicle_id in routes_order:
            for i, start_i in enumerate(routes_order[vehicle_id]['route'][:-1]):
                end_i = routes_order[vehicle_id]['route'][i + 1]
                start = place_ids[start_i]
                end = place_ids[end_i]
                route_segment = get_route(start, end)
                routes.append({
                    'from': start,
                    'to': end,
                    'waypoints': route_segment,
                    'vehicle_id': vehicle_id,
                    'distance': routes_order[vehicle_id]['distance']
                })

        return routes

    return None


if __name__ == '__main__':
    place_ids = json.load(open('example_place_ids.json', 'r'))
    vrp_solve_main(place_ids, 2, 0)
