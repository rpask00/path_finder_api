import googlemaps

from googleapi import API_KEY


def get_place_details(place_name):
    gmaps = googlemaps.Client(key=API_KEY)

    # Request for place autocomplete
    autocomplete_result = gmaps.places_autocomplete(place_name)

    # if there are results, fetch latitude and longitude
    if autocomplete_result:
        place_id = autocomplete_result[0]['place_id']
        place_details = gmaps.place(place_id)
        lat = place_details['result']['geometry']['location']['lat']
        lng = place_details['result']['geometry']['location']['lng']

        # Include lat and lon in the autocomplete result
        autocomplete_result[0]['lat'] = lat
        autocomplete_result[0]['lon'] = lng

        return autocomplete_result[0]

    return None


place_name = 'New York'  # Replace with the place name you are searching for

place_details = get_place_details(place_name)

if place_details:
    print(place_details)
else:
    print('No results found.')
