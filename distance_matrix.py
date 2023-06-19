import googlemaps

from googleapi import API_KEY

gmaps = googlemaps.Client(key=API_KEY)


def generate_distance_matrix(place_ids):
    distance_matrix = []

    for origin_id in place_ids:
        row = []
        for destination_id in place_ids:
            if origin_id == destination_id:
                row.append(0)
            else:
                result = gmaps.distance_matrix(origins='place_id:' + origin_id,
                                               destinations='place_id:' + destination_id,
                                               mode='driving')
                distance = result['rows'][0]['elements'][0]['distance']['value']  # Get distance in meters
                row.append(distance)
        distance_matrix.append(row)

    return distance_matrix


if __name__ == '__main__':
    _place_ids = ['ChIJd8BlQ2BZwokRAFUEcm_qrcA', 'ChIJE9on3F3HwoAR9AhGJW_fL-I']
    generate_distance_matrix(_place_ids)
