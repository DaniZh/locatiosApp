import json
import requests
import unittest
from pymongo import Connection
from bson.objectid import ObjectId
from multiprocessing import Process
from app.server import app

port = 5001
url = 'http://localhost:%s' % port
db_name = 'locations_test'

def start_server():
    app.conn_args = {}
    app.db_name = db_name
    app.debug = False
    app.run(port=port)

def send_data(method, path, data):
    return requests.request(method, url + path, data=json.dumps(data), 
        headers={'Content-Type': 'application/json'})

class LocationApiIntegrationTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.server_process = Process(target=start_server)
        cls.server_process.start()
        cls.conn = Connection('localhost', 27017)

    @classmethod
    def tearDownClass(cls):
        cls.server_process.terminate()
        cls.conn.drop_database(db_name)
        cls.conn.disconnect()

    def tearDown(self):
        self.conn[db_name].drop_collection('locations')

    def test_create_location(self):
        """
        Validates that the specified location is created.
        :return:
        """
        expected_location = {'name': 'Work', 'lat': '123', 'lng': '432', 'address': 'Northern Territory 0872, Australia'}

        resp = send_data('post','/locations/', expected_location)
        
        self.assertEqual(200, resp.status_code)
        _name = expected_location['name']
        _lat = expected_location['lat']
        _lng = expected_location['lng']
        _address = expected_location['address']
        actual_location = json.loads(resp.content)

        self.assertIn('id', actual_location)
        _id = actual_location['id']
        self.assertIn('name', actual_location)
        self.assertEqual(_name, actual_location['name'])
        self.assertIn('lat', actual_location)
        self.assertEqual(_lat, actual_location['lat'])
        self.assertIn('lng', actual_location)
        self.assertEqual(_lng, actual_location['lng'])
        self.assertIn('address', actual_location)
        self.assertEqual(_address, actual_location['address'])

        del actual_location['id']
        
        self.assertEqual(expected_location, actual_location)
        
        location = self.conn[db_name].locations.find_one({'_id': ObjectId(_id)})
        
        self.assertIsNotNone(location)

    def test_get_all_locations(self):
        send_data('post','/locations/', {'name': 'Work', 'lat': '123', 'lng': '432', 'address': 'Northern Territory 0872, Australia'})
        send_data('post','/locations/', {'name': 'Home', 'lat': '1243', 'lng': '4321', 'address': 'Brixton, London SE24 0HJ, UK'})
        send_data('post','/locations/', {'name': 'Office', 'lat': '12463', 'lng': '43621', 'address': 'London SW18 1JN, UK'})

        resp = requests.get(url + '/locations/')

        self.assertEqual(200, resp.status_code)

        data = json.loads(resp.content)

        self.assertEqual(3, len(data))

        for location in data:
            self.assertIn('id', location)
            self.assertIsNotNone(location['id'])
            self.assertIn('name', location)
            self.assertIsNotNone(location['name'])
            self.assertIn('lat', location)
            self.assertIsNotNone(location['lat'])
            self.assertIn('lng', location)
            self.assertIsNotNone(location['lng'])
            self.assertIn('address', location)
            self.assertIsNotNone(location['address'])


    def test_get_location(self):
        location = {'name': 'Work', 'lat': '123', 'lng': '432', 'address': 'Northern Territory 0872, Australia'}
        create_resp = send_data('post', '/locations/', location)
        _id = json.loads(create_resp.content)['id']
        
        resp = requests.get(url + '/locations/' + _id)
        
        self.assertEqual(200, resp.status_code)
        
        data = json.loads(resp.content)
        
        self.assertEqual(_id, data['id'])
        self.assertEqual(data['name'], location['name'])
        self.assertEqual(data['lat'], location['lat'])
        self.assertEqual(data['lng'], location['lng'])
        self.assertEqual(data['address'], location['address'])

    def test_update_location(self):
        location = {'name': 'Work2', 'lat': '12321', 'lng': '43212', 'address': 'Northern Territory 0872, Australia'}
        create_resp = send_data('post','/locations/', location)
        
        _id = json.loads(create_resp.content)['id']
        
        location['name'] = 'Home'
        
        update_resp = send_data('put', '/locations/' + _id, location)
        
        self.assertEqual(200, update_resp.status_code)
        
        resp = requests.get(url + '/locations/' + _id)
        data = json.loads(resp.content)
        
        self.assertEqual(data['name'], location['name'])
        self.assertEqual(data['lat'], location['lat'])
        self.assertEqual(data['lng'], location['lng'])
        self.assertEqual(data['address'], location['address'])
    
    def test_delete_location(self):
        location = {'name': 'Work2', 'lat': '12321', 'lng': '43212', 'address': 'Northern Territory 0872, Australia'}
        create_resp = send_data('post','/locations/', location)
        
        _id = json.loads(create_resp.content)['id']
        
        delete_resp = requests.delete(url + '/locations/' + _id)
        
        self.assertEqual(200, delete_resp.status_code)
        
        resp = requests.get(url + '/locations/' + _id)
        
        self.assertEqual(404, resp.status_code)
    
    def test_that_non_existant_location_should_return_404(self):
        resp = requests.get(url + '/locations/4e971ed699b6bd4f08000001')
        
        self.assertEqual(404, resp.status_code)
    
    def test_that_invalid_location_id_should_return_400(self):
        resp = requests.get(url + '/locations/123')
        
        self.assertEqual(400, resp.status_code)
    
    def test_invalid_method_should_return_not_allowed(self):
        resp = requests.request('put', url + '/locations/')

        self.assertEqual(405, resp.status_code)
