import googlemaps

from autocomplete import API_KEY


def get_route(api_key, start_place_id, end_place_id):
    gmaps = googlemaps.Client(key=api_key)

    # Request directions
    directions = gmaps.directions(
        "place_id:" + start_place_id,
        "place_id:" + end_place_id,
        mode="driving",
    )

    # Extract the points along the route from the directions
    points = []
    for step in directions[0]["legs"][0]["steps"]:
        # Each step's start location is a point along the route
        points.append((step["start_location"]["lat"], step["start_location"]["lng"]))

    # Don't forget to include the end location of the final step
    last_step = directions[0]["legs"][0]["steps"][-1]
    points.append((last_step["end_location"]["lat"], last_step["end_location"]["lng"]))

    return points


api_key = API_KEY  # replace this with your actual API key
start_place_id = 'ChIJX_OXBPtPBEcRS24cQch39SA'  # replace this with your actual start place ID
end_place_id = 'ChIJvRmjsCygFkcRvFDfvAr1xzo'  # replace this with your actual end place ID
print(get_route(api_key, start_place_id, end_place_id))
