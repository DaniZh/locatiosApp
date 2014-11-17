
# A Locations App with (Backbone.js, Require.js, Flask, and MongoDB)

This is a small app which allows the user to save his favorite locations.
Google maps is used for the address and location retrieval.
As a reference for the Locations App, the famous Todos app, included in the Backbone.js repository,
by [Jérôme Gravel-Niquet] was used.

Technologies used:

* Backbone.js - Client side framework.
* Require.js - Async resource loading.
* Flask - A simple python webapp to provide a REST interface.
* MongoDB - Persistance for the client app.

Setup:
    virtualenv env --no-site-packages
    source env/bin/activate
    pip install -r requirements.txt
    mkdir data
    mongod --dbpath=data/ --fork --logpath=data/mongod.log
    python app/server.py
    http://localhost:5000/

Testing:
    py.test app/test/locations_api_test.py