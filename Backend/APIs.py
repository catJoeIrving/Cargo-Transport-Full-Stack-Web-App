# DB Identifier: cis3368spring
# DB name: CIS3368SpringDB
# Username: admin
# PW: 32Graduating!!

import flask
from flask import jsonify
from flask import request
from sql import create_connection
from sql import execute_read_query
from sql import execute_query
import creds
from mysql.connector import Error

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

# http://127.0.0.1:5000/api/cargo
@app.route('/api/cargo', methods=['POST']) #API to add new cargo to the DB table so long as there is space
def add_cargo():
    # Set up a connection the DB
    myCreds = creds.Creds()
    conn = create_connection(myCreds.conString, myCreds.userName, myCreds.password, myCreds.dbName)

    # Get the json data and assign it to the proper variables
    request_data = request.get_json() # gets the info from the JSON package
    secondary_id = request_data['secondary_id']
    weight = request_data['weight']
    cargotype = request_data['cargotype']
    departure = None
    arrival = None
    shipid = request_data['shipid']
    if 'departure' in request_data:
        departure = request_data['departure']
    if 'arrival' in request_data:
        arrival = request_data['arrival']

    # Logic for getting the a ships current weight and max weight:
    current_ship_weight = []
    sql = "SELECT * FROM cargo"
    cargo = execute_read_query(conn, sql)
    for item in cargo: # Loop through the list of dictionaries
        if item['shipid'] == shipid:
            current_ship_weight.append(int(item['weight']))
    current_ship_weight = sum(current_ship_weight)
    sql = "SELECT maxweight FROM spaceship WHERE id = %s" % (shipid)
    max_ship_weight = execute_read_query(conn, sql)
    max_ship_weight = int(max_ship_weight[0]['maxweight'])

    if int(current_ship_weight) + int(weight) > max_ship_weight: # checks to see if there is space on the ship to
        # receive the weight of the new cargo
        return 'Not enough capacity on selected ship'
    else:
        # Execute the SQL syntax to create a new record using the variables provided
        if departure and arrival: # SQL script for if departure and arrival were given
            sql = "INSERT INTO cargo (secondary_id, weight, cargotype, departure, arrival, shipid) VALUES (%s, '%s', '%s', '%s', '%s', %s)" % (
            int(secondary_id), weight, cargotype, departure, arrival, int(shipid))
        elif departure and not arrival: # SQL script for if departure was given but not arrival
            sql = "INSERT INTO cargo (secondary_id, weight, cargotype, departure, shipid) VALUES (%s, '%s', '%s', '%s', %s)" % (
            int(secondary_id), weight, cargotype, departure, int(shipid))
        elif arrival and not departure: # SQL script for if arrival was given but not departure
            sql = "INSERT INTO cargo (secondary_id, weight, cargotype, arrival, shipid) VALUES (%s, '%s', '%s', '%s', %s)" % (
            int(secondary_id), weight, cargotype, arrival, int(shipid))
        else: # neither were given
            sql = "INSERT INTO cargo (secondary_id, weight, cargotype, shipid) VALUES (%s, '%s', '%s', %s)" % (int(secondary_id), weight, cargotype, int(shipid))

        # FIXME: Duplicate secondary_id will return success string but encounter 'duplicate entry error' and not execute,
        #  may not be an issue but depends on what professor says
        execute_read_query(conn, sql)
        conn.commit()

    return 'Cargo added successfully'


app.run()


# Started working on this on accident, but this is basically a completed POST API for the captain table if you wanna
# use it, just change api/cargo path # http://127.0.0.1:5000/api/cargo @app.route('/api/cargo', methods=['POST'])
#
# #API to add new cargo to the DB table so long as there is space def add_cargo(): # Get the json data and assign it
# to the proper variables request_data = request.get_json() # gets the info from the JSON package secondary_id =
# request_data['secondary_id'] firstname = request_data['firstname'] lastname = request_data['lastname'] rank =
# request_data['rank'] homeplanet = request_data['homeplanet']
#
#     # Set up a connection the DB
#     myCreds = creds.Creds()
#     conn = create_connection(myCreds.conString, myCreds.userName, myCreds.password, myCreds.dbName)
#     # Execut the SQL syntax to create a new record using the variables provided
#     sql = "INSERT INTO snowboard (secondary_id, firstname, lastname, rank, homeplanet) VALUES (%s, '%s', '%s', '%s', '%s')" % (int(secondary_id), firstname, lastname, rank, homeplanet)
#     execute_read_query(conn, sql)
#     conn.commit()
#
#     return 'Snowboard added successfully'


# Becky's portion of captain table & log in API 
@app.route('api/captain', method = ["GET"])
def get_captain_record():
    myCreds = creds.Creds()
    conn = create_connection(myCreds.conString, myCreds.userName, myCreds.password, myCreds.dbName)
    if 'secondary_id' in request.args: # only if an secondary_id is provided as an argument, proceed
        # Gets the info from the arguments
        secondary_id = int(request.args['secondary_id'])
    else:
        return 'ERROR: No ID provided!'

    sql = "SELECT * FROM captain"
    captain = execute_read_query(conn, sql) # Collects all records from the DB table and makes a list of dictionaries
    captain_record = [] # Empty string to put the record in

    for item in captain: # Loop through the list of dictionaries
        if item['secondary_id'] == secondary_id: # Find the one with the matching ID
            captain_record.append(item) # Add the result to list
    return jsonify(captain_record)

@app.route('api/captain', method = ["POST"])
def new_captain_record():
    try:
        # requesting new data to put in database
        request_data = request.get_json()
        secondary_id = request_data['secondary_id']
        firstname = request_data['firstname']
        lastname = request_data['lastname']
        rank = request_data['rank']
        homeplanet = request_data['homeplanet']
        # Set up a connection the DB
        myCreds = creds.Creds()
        conn = create_connection(myCreds.conString, myCreds.userName, myCreds.password, myCreds.dbName)
        # SQL query to add a new captain information to the database
        sql = "INSERT INTO captain (secondary_id, firstname, lastname, rank, homeplanet) VALUES (%s, '%s', '%s', '%s', '%s')" % (int(secondary_id), firstname, lastname, rank, homeplanet)
        execute_read_query(conn, sql)
        conn.commit()
        return 'New captain added successfully' # Success message

    except Error as e:
        print(f"The error '{e}' occurred")

    

@app.route('api/captain', method = ["PUT"])
def update_captain_record():
    myCreds = creds.Creds()
    conn = create_connection(myCreds.conString, myCreds.userName, myCreds.password, myCreds.dbName)   
    request_data = request.get_json() 
    newFirstName = request_data['firstname']
    newLastName = request_data['lastname']
    newRank = request_data['rank']
    newHomePlanet = request_data['homeplanet']
    inputID = request_data['secondary_id']

    # if the user wants to update one row in the 'captain' table, he/she will need to input values for all 4 variables (first name, last name, rank, home planet)
    # The row is identified by the id number
    sqlQuery = "UPDATE captain SET firstname='%s', lastname='%s', rank='%s', homeplanet='%s' WHERE secondary_id ='%s' " % (newFirstName, newLastName, newRank, newHomePlanet, inputID)
    execute_query(conn, sqlQuery)
    return 'Update entire row is successful!'

@app.route('api/captain', method = ["DELETE"])
def delete_captain_record():
    # establishes connection to database
    myCreds = creds.Creds()
    conn = create_connection(myCreds.conString, myCreds.userName, myCreds.password, myCreds.dbName)
    sql = "SELECT * FROM captain"
    captain = execute_read_query(conn, sql) # reads the captain table 
    idToDelete = int(request.args['secondaryid'])
    for i in range(len(captain) -1, -1, -1):
        if captain[i]['secondaryid'] == idToDelete:
            sqlDeleteQuery = "DELETE FROM captain WHERE id= %s"%(idToDelete) # creates a SQL query to delete the row with ID identified
            execute_query(conn, sqlDeleteQuery) # executes the query
    
    return 'Delete request successful'

