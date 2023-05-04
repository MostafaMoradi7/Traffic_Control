import json
from django.conf import settings
import os

from .models import Node, Car, Toll, Owner, Road


def get_all_info():
    with open(os.path.join(settings.BASE_DIR, 'cherry_app', 'data/all_nodes.json'), 'r') as data1:
        all_nodes_json = json.load(data1)

    with open(os.path.join(settings.BASE_DIR, 'cherry_app', 'data/owners.json'), 'r') as data2:
        owners_json = json.load(data2)

    with open(os.path.join(settings.BASE_DIR, 'cherry_app', 'data/tollStations.json'), 'r') as data3:
        toll_stations_json = json.load(data3)

    with open(os.path.join(settings.BASE_DIR, 'cherry_app', 'data/roads.json'), 'r') as data4:
        roads_json = json.load(data4)

    nodes = []
    owners = []
    toll_stations = []
    roads = []

    # TAKING OUT ALL THE NODES IN FILE 'all_nodes.json' and saving them in cache
    for n in all_nodes_json:
        node = Node(
            car=n['car'],
            location=n['location'],
            date=n['date']
        )
        nodes.append(node)

    # TRYING TO DO THE SAME THING FOR 'owners.json'
    for o in owners_json:
        cars = []
        for c in o['ownerCar']:
            car = Car(
                cId=c['id'],
                cType=c['type'],
                color=c['color'],
                length=c['length'],
                load_volume=c['load_valume']
            )
            cars.append(car)

        owner = Owner(
            name=o['name'],
            national_code=o['national_code'],
            age=o['age'],
            total_toll_paid=o['total_toll_paid'],
            cars=cars
        )
        owners.append(owner)

    # SAME FOR TOLL_STATIONS
    for t in toll_stations_json:
        toll = Toll(
            name=t['name'],
            toll_per_cross=t['toll_per_cross'],
            location=t['location']
        )
        toll_stations.append(toll)

    # SAME FOR THE ROADS TOO
    for r in roads_json:
        road = Road(
            name=r['name'],
            geom=r['geom'],
            width=r['width']
        )
        roads.append(road)

    # RETURNING THE RESULT
    all_info = {"all_nodes": nodes, "owners": owners,
                "tollStations": toll_stations, "roads": roads}
    return all_info


def find_all_red_and_blue_cars(owners):
    result = []
    for owner in owners:
        for car in owner.cars:
            if car.color == 'red' or car.color == 'blue':
                result.append(car)

    return result


def get_old_owners_cars(owners):
    cars = []
    for owner in owners:
        if owner.age > 70:
            for car in owner.cars:
                cars.append(car)

    return cars


def check_is_on_road(roads, node):
    for road in roads:
        road_x, road_y = road.get_coordinates()
        location_points = node.get_location_dict()['Point']
        if location_points['x'] < min(road_x) or location_points['x'] > max(road_x):
            continue
        for i in range(len(road_x) - 1):
            m = (road_y[i + 1] - road_y[i]) / (road_x[i + 1] - road_x[i])
            b = road_y[i] - road_x[i] * m

            if abs(location_points['y'] - (location_points['x'] * m + b)) < 1e-6:
                return True
    return False


def get_heavy_cars(information):
    # FIRST WE HAVE TO FIND THE CARS:
    heavy_cars_set = set()
    heavy_cars = []
    for owner in information['owners']:
        for car in owner.cars:
            if car.type == "big":
                heavy_cars_set.add(car.id)
                heavy_cars.append(car)

    # WE'LL FIND ALL ROADS WITH WIDTH LESS THAN 20 FIRST:
    tight_roads = []
    for road in information['roads']:
        if road.width < 20:
            tight_roads.append(road)

    # NOW WE NEED TO CHECK WHETHER THESE CARS WERE ON TIGHT ROADS OR NOT:
    result_set = set()      # FOR MAKING SURE WE'RE NOT DUPLICATING
    for node in information['all_nodes']:
        if (node.car in heavy_cars_set) and (node.car not in result_set):
            if check_is_on_road(tight_roads, node):
                result_set.add(node.car)

    result = []
    for car in heavy_cars:
        if car.id in result_set:
            result.append(car)
    return result
