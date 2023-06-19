import json
import os

import googlemaps
from dotenv import load_dotenv
from flask import Flask, request, make_response, jsonify
from pymongo import MongoClient

from autocomplete import autocomplete
from googleapi import API_KEY
from vrp_solver import vrp_solve_main

load_dotenv()
MDB_URI = os.environ.get('MDB_URI')
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


@app.route('/', methods=['GET'])
def home():
    return 'Hello, World!'


@app.route('/api/vrp_solve', methods=['GET'])
def get_vrp_solve():
    depot = int(request.args.get('depot', default=0))
    num_vehicles = int(request.args.get('num_vehicles', default=1))
    place_ids = request.args.getlist('place_id')
    json.dump(place_ids, open('example_place_ids.json', 'w'))

    vrp_solution = vrp_solve_main(place_ids, num_vehicles, depot)

    if vrp_solution:
        return make_response(json.dumps(vrp_solution), 200, {'Content-Type': 'application/json'})

    return make_response('No solution found', 404)


@app.route('/api/locations', methods=['GET'])
def get_locations():
    types = request.args.getlist('type')
    search = request.args.get('search')

    response = autocomplete(search, API_KEY, types) if len(search) > 2 else []
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
