import json
import json
import re

import googlemaps
from bson import ObjectId
from bson.json_util import dumps
from dotenv import load_dotenv
from flask import Flask, request, Response, make_response, jsonify
from pymongo import MongoClient

from autocomplete import autocomplete, API_KEY
from vrp_solver import vrp_solve_main

load_dotenv()

MDB_URI = 'mongodb://admin:secret@localhost:27017'
DB_NAME = 'path_finder'

app = Flask(__name__)

client = MongoClient(MDB_URI)
db = client[DB_NAME]


@app.before_request
def before_request():
    if request.method == 'OPTIONS':
        return make_response(jsonify({'message': 'ok'}), 200)


@app.after_request
def apply_headers(response):
    response.headers["Access-Control-Allow-Origin"] = "*"
    response.headers["Access-Control-Allow-Methods"] = "*"
    response.headers["Access-Control-Allow-Headers"] = "*"

    return response


@app.route('/')
def index():
    return app.redirect('/api/ip_addresses')


@app.route('/api/points')
def get_ip_addresses():
    sort_query = get_sort_query(request.args)
    page = int(request.args.get('page', 0))
    items_per_page = int(request.args.get('size', 20))
    offset = page * items_per_page
    filter_query = get_filer_query(request.args)
    total_items = db['points'].count_documents(filter_query)
    points = db['points'].find(filter_query)

    if sort_query:
        points = points.sort(list(sort_query.items()))

    points = points.skip(offset).limit(items_per_page)

    points = list(points)

    for ip_address in points:
        ip_address['_id'] = str(ip_address['_id'])

    return Response(dumps({
        'data': points,
        'totalItems': total_items
    }), status=200, content_type='application/json')


@app.route('/api/points/<string:_id>', methods=['PUT'])
def update_ip_addresses(_id):
    _id = ObjectId(_id)

    check_ip_address = db['ip_addresses'].find_one({'ip': request.json['ip']})

    if check_ip_address and check_ip_address['_id'] != _id:
        return make_response('IP address must be unique', 409)

    db['ip_addresses'].update_one({'_id': _id}, {'$set': request.json})
    update_ip_address = db['ip_addresses'].find_one({'ip': _id})

    return Response(dumps(update_ip_address), status=200, content_type='application/json')


@app.route('/api/points', methods=['POST'])
def create_point():
    _id = db['points'].insert_one(request.json).inserted_id
    inserted_point = db['points'].find_one({'ip': _id})

    return Response(dumps(inserted_point), status=200, content_type='application/json')


@app.route('/api/points/<string:_id>', methods=['DELETE'])
def delete_ip_address(_id):
    _id = ObjectId(_id)
    db['ip_addresses'].delete_one({'_id': _id})

    return make_response('', 204)


@app.route('/api/vrp_solve', methods=['GET'])
def get_vrp_solve():
    depot = request.args.get('depot', default=1)
    num_vehicles = int(request.args.get('num_vehicles', default=1))
    place_ids = request.args.getlist('place_id')
    json.dump(place_ids, open('example_place_ids.json', 'w'))

    vrp_solution = vrp_solve_main(place_ids, num_vehicles, depot)

    if vrp_solution:
        return make_response(json.dumps(vrp_solution), 200, {'Content-Type': 'application/json'})

    return make_response('No solution found', 404)


@app.route('/api/locations', methods=['GET'])
def get_locations():
    search = request.args.get('search')
    API_KEY = 'AIzaSyDQjweYwLm4pqNCXBX4oXm09HZUXvHdkA8'
    params = {
        'input': search,
        'types': 'geocode',
        'language': 'pl',
        'key': API_KEY,
        'region': 'pl',
    }

    param_string = '&'.join([f'{key}={value}' for key, value in params.items()])
    url = f"https://maps.googleapis.com/maps/api/place/autocomplete/json?{param_string}"

    payload = {}
    headers = {}

    response = autocomplete(search, API_KEY) if len(search) > 2 else []
    return make_response(json.dumps(response), 200, {'Content-Type': 'application/json'})


cached_places = []


@app.route('/api/places_details/<string:place_id>', methods=['GET'])
def places_details(place_id):
    for cached in cached_places:
        if cached['place_id'] == place_id:
            print('cached', place_id)
            return cached

    gmaps = googlemaps.Client(key=API_KEY)
    result = gmaps.place(place_id)['result']
    cached_places.append(result)
    return result


def get_sort_query(args):
    sort_query = {}
    sort_args = [arg for arg in args if 'sort' in arg]

    for arg in sort_args:
        field = re.search(r'\[(.*?)\]', arg).group(1)
        direction = args.get(arg)
        sort_query[field] = 1 if direction == 'asc' else -1

    print(sort_query)

    return sort_query


def get_filer_query(args):
    filter_query = {}
    filter_args = [arg for arg in args if 'filter' in arg]

    for arg in filter_args:
        field = re.search(r'\[(.*?)\]', arg).group(1)
        value = args.get(arg)
        filter_query[field] = {'$regex': value, '$options': 'i'}

    print(filter_query)
    return filter_query
