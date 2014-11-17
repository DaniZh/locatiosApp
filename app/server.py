import pymongo
from bson.objectid import ObjectId
from flask import Flask, render_template, request
from util import make_json_response, bad_id_response

app = Flask(__name__)

app.debug = True

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/locations/', methods=['GET'])
def get_locations():
    """
    Used to retrieve all locations from the DB.
    :return:list -- of locations
    """
    locations = get_collection()
    cur = locations.find().sort('order', pymongo.ASCENDING)
    data = []
    
    for location in cur:
        location['id'] = str(location['_id'])
        del location['_id']
        data.append(location)
    
    return make_json_response(data)

@app.route('/locations/<location_id>',  methods=['GET'])
def get_location(location_id):
    """
    Retrieves a specific location.
    :param location_id: str -- The id of location object which will be updated.
    :return: -- Json response The specified location object.
    """
    oid = None
    try:
        oid = ObjectId(location_id)
    except:
        return bad_id_response()

    locations = get_collection()
    location = locations.find_one({'_id': oid})

    if location is None:
        return make_json_response({'message': 'no location with id: ' + location_id}, 404)

    location['id'] = str(location['_id'])
    del location['_id']

    return make_json_response(location)

@app.route('/locations/', methods=['POST'])
def create_location():
    """
    Saves a location to the DB,
    :return: dict -- location
    """
    data = request.json
    locations = get_collection()
    oid = locations.insert(data)
    location = locations.find_one({'_id': ObjectId(oid)})
    location['id'] = str(location['_id'])
    del location['_id']
    return make_json_response(location)

@app.route('/locations/<location_id>',  methods=['PUT'])
def update_location(location_id):
    """
    Updates specific location.
    :param location_id: str -- The id of location object which will be updated.
    :return: -- Json response status 200.
    """
    data = request.json
    locations = get_collection()
    locations.update({'_id': ObjectId(location_id)}, {'$set': data})
    return make_json_response({'message': 'OK'})

@app.route('/locations/<location_id>',  methods=['DELETE'])
def delete_location(location_id):
    """
    Removes a specific Location.
    :param location_id: str -- The id of location object which will be deleted..
    :return: -- Json response status 200.
    """
    locations = get_collection()
    locations.remove(ObjectId(location_id))
    return make_json_response({'message': 'OK'})

def get_collection():
    conn = pymongo.Connection('localhost:27017', **app.conn_args)
    return conn[app.db_name].locations

if __name__ == '__main__':
    import optparse
    parser = optparse.OptionParser()
    parser.add_option('-r', '--replicaset', dest='replicaset', help='Define replicaset name to connect to.')
    
    options, args = parser.parse_args()
    
    if options.replicaset is not None:
        app.conn_args = {'replicaset': options.replicaset, 'slave_okay': True}
    else:
        app.conn_args = {}
    
    app.db_name = 'locations_prod'
    app.run(host='0.0.0.0')
