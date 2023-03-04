# DB Identifier: cis3368spring
# DB name: CIS3368SpringDB
# Username: admin
# PW: 32Graduating!!

import flask
from flask import jsonify
from flask import request
from sql import create_connection
from sql import execute_read_query
import creds

app = flask.Flask(__name__)
app.config["DEBUG"] = True

# http://127.0.0.1:5000/api/cargo
@app.route('/api/cargo', methods=['GET']) #API to get a cargo record from the DB table
def api_cargo_record():
    if 'secondary_id' in request.args: # only if an secondary_id is provided as an argument, proceed
        # Gets the info from the arguments
        secondary_id = int(request.args['secondary_id'])
    else:
        return 'ERROR: No ID provided!'

    # Set up a connection to the DB
    myCreds = creds.Creds()
    conn = create_connection(myCreds.conString, myCreds.userName, myCreds.password, myCreds.dbName)
    sql = "SELECT * FROM cargo"
    cargo = execute_read_query(conn, sql) # Collects all records from the DB table and makes a list of dictionaries
    results = [] # Empty string to put the record in

    for item in cargo: # Loop through the list of dictionaries
        if item['secondary_id'] == secondary_id: # Find the one with the matching ID
            results.append(item) # Add the result to list
    return jsonify(results)




app.run()

