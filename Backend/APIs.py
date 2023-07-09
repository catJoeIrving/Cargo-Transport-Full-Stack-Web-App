
# ============================================
# Team Members
# ============================================
# Joseph Irving & Becky Tseng
#
# Joseph Irving Tasks:
#   - Created DB tables / Cargo APIs / Spaceship APIs
# Becky Tseng Tasks:
#   - Captain APIs / Login API

import flask
from flask import jsonify
from flask import request
from sql import create_connection
from sql import execute_read_query
from sql import execute_query
import creds
from mysql.connector import Error
import hashlib
from flask import request, make_response

app = flask.Flask(__name__)
app.config["DEBUG"] = True

# ============================================
# Cargo Table APIs
# ============================================
# Worked on by: Joseph Irving

# http://127.0.0.1:5000/api/cargo/all
@app.route('/api/cargo/all', methods=['GET']) #API to get all records from the cargo table
def api_all_cargo():
    # Set up a connection to the DB
    myCreds = creds.Creds()
    conn = create_connection(myCreds.conString, myCreds.userName, myCreds.password, myCreds.dbName)
    sql = "SELECT * FROM cargo"
    cargo = execute_read_query(conn, sql) # Collects all records from the DB table and makes a list of dictionaries
    results = [] # Empty list to put the records in

    for item in cargo: # Loop through the list of dictionaries
        # Swaps shipid with the secondary_id from the spaceship table:
        sql = "SELECT secondary_id FROM spaceship WHERE id = %s" % (item['shipid'])
        shipid = execute_read_query(conn, sql)
        item['shipid'] = shipid[0]['secondary_id']

        del item['id']

        results.append(item) # Add the result to list

    return jsonify(results)


# http://127.0.0.1:5000/api/cargo
@app.route('/api/cargo', methods=['GET']) #API to get a record from the cargo table
def api_cargo_record():
    if 'secondary_id' in request.args: # only if an secondary_id is provided as an argument, proceed
        # Gets the info from the arguments
        secondary_id = int(request.args['secondary_id'])
    else:
        no_id = 'ERROR: No ID provided!'
        return jsonify(no_id)

    # Set up a connection to the DB
    myCreds = creds.Creds()
    conn = create_connection(myCreds.conString, myCreds.userName, myCreds.password, myCreds.dbName)
    sql = "SELECT * FROM cargo"
    cargo = execute_read_query(conn, sql) # Collects all records from the DB table and makes a list of dictionaries
    results = [] # Empty string to put the record in

    for item in cargo: # Loop through the list of dictionaries
        if item['secondary_id'] == secondary_id: # Find the one with the matching ID
            # Swaps shipid with the secondary_id from the spaceship table:
            sql = "SELECT secondary_id FROM spaceship WHERE id = %s" % (item['shipid'])
            shipid = execute_read_query(conn, sql)
            item['shipid'] = shipid[0]['secondary_id']

            del item['id']

            results.append(item) # Add the result to list
    return jsonify(results)

# http://127.0.0.1:5000/api/cargo
@app.route('/api/cargo', methods=['POST']) #API to add new cargo to the cargo table so long as there is space
def add_cargo():
    # Set up a connection the DB
    myCreds = creds.Creds()
    conn = create_connection(myCreds.conString, myCreds.userName, myCreds.password, myCreds.dbName)

    # Get the json data and assign it to the proper variables
    request_data = request.get_json() # gets the info from the JSON package

    if 'secondary_id' not in request_data or 'weight' not in request_data or 'cargotype' not in request_data or 'secondary_ship_id' not in request_data:
        missing = 'ERROR: All fields (secondary_id, weight, cargotype, secondary_ship_id) are required!'
        return jsonify(missing)

    secondary_id = request_data['secondary_id']
    weight = request_data['weight']
    cargotype = request_data['cargotype']

    secondary_ship_id = request_data['secondary_ship_id'] # gets the actual ship ID using the secondary ID
    sql = "SELECT id FROM spaceship WHERE secondary_id = %s" % (secondary_ship_id)
    shipid = execute_read_query(conn, sql)
    shipid = shipid[0]['id']

    # Logic for getting a ships current weight and max weight:
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
        full = 'Not enough capacity on selected ship'
        return jsonify(full)
    else:
        sql = "INSERT INTO cargo (secondary_id, weight, cargotype, shipid) VALUES (%s, '%s', '%s', %s)" % (int(secondary_id), weight, cargotype, int(shipid))

        execute_read_query(conn, sql)
        conn.commit()

    return jsonify(True)

# http://127.0.0.1:5000/api/cargo
@app.route('/api/cargo', methods=['PUT'])
def update_cargo():
    # set up a connection to the db
    myCreds = creds.Creds()
    conn = create_connection(myCreds.conString, myCreds.userName, myCreds.password, myCreds.dbName)
    shipid = None

    # Get the json data
    request_data = request.get_json()
    if 'secondary_id' in request_data:  # only if an id is provided in the json data will it proceed
        secondary_id = int(request_data['secondary_id'])
    else:
        no_id = 'ERROR: No ID provided!'
        return jsonify(no_id)

    # So long as an ID is provided, this will go through each possible record and update only the fields that were
    # provided in the json data
    if 'secondary_ship_id' in request_data: # This will use the secondary_id given to find the actual id of the ship
        secondary_ship_id = request_data['secondary_ship_id']
        sql = "SELECT id FROM spaceship WHERE secondary_id = %s" % (secondary_ship_id)
        updated_shipid = execute_read_query(conn, sql)
        updated_shipid = updated_shipid[0]['id']

        sql = "SELECT * FROM spaceship"
        spaceship = execute_read_query(conn, sql)  # Collects all records from the cargo table and makes a list of dictionaries
        ship_exists = False
        has_space = False
        weight = None

        # The weight of the cargo will either be the updated weight if given, or it's current weight
        if 'weight' in request_data:
            weight = request_data['weight']
        else:
            sql = "SELECT * FROM cargo"
            cargo = execute_read_query(conn, sql)  # Collects all records from the DB table and makes a list of dictionaries
            for record in cargo:
                if record['secondary_id'] == secondary_id:
                    weight = record['weight']

        for ship in spaceship:  # Loop through ships to make sure the selected ship exists
            if ship['id'] == updated_shipid:  # Find the one with the matching ID
                ship_exists = True
                break
        else:
            no_ship = 'Selected ship does not exist'
            return jsonify(no_ship)
        # Logic for getting a ships current weight and max weight:
        current_ship_weight = []
        sql = "SELECT * FROM cargo"
        cargo = execute_read_query(conn, sql)
        for item in cargo:  # Loop through the list of dictionaries
            if item['shipid'] == updated_shipid:
                current_ship_weight.append(int(item['weight']))
        current_ship_weight = sum(current_ship_weight)
        sql = "SELECT maxweight FROM spaceship WHERE id = %s" % (updated_shipid)
        max_ship_weight = execute_read_query(conn, sql)
        max_ship_weight = int(max_ship_weight[0]['maxweight'])

        if int(current_ship_weight) + int(weight) > max_ship_weight:  # checks to see if there is space on the ship to
            # receive the weight of the new cargo
            full = 'Not enough capacity on selected ship'
            return jsonify(full)
        else:
            has_space = True

        if ship_exists and has_space: # If both are true, proceed with updating the record
            sql = "UPDATE cargo SET shipid = %s WHERE secondary_id = %s" % (int(updated_shipid), secondary_id)
            execute_read_query(conn, sql)

    # Go through to check for the rest of the attributes and update only the ones provided
    if 'weight' in request_data:
        updated_weight = request_data['weight']
        sql = "UPDATE cargo SET weight = %s WHERE secondary_id = %s" % (updated_weight, secondary_id)
        execute_read_query(conn, sql)
    if 'cargotype' in request_data:
        cargotype = request_data['cargotype']
        sql = "UPDATE cargo SET cargotype = '%s' WHERE secondary_id = %s" % (cargotype, secondary_id)
        execute_read_query(conn, sql)
    if 'departure' in request_data:
        updated_departure = request_data['departure']
        sql = "UPDATE cargo SET departure = '%s' WHERE secondary_id = %s" % (updated_departure, secondary_id)
        execute_read_query(conn, sql)
    if 'arrival' in request_data:
        updated_arrival = request_data['arrival']
        sql = "UPDATE cargo SET arrival = '%s' WHERE secondary_id = %s" % (updated_arrival, secondary_id)
        execute_read_query(conn, sql)

    conn.commit() # commits any changes from the above commands

    return jsonify(True)

# http://127.0.0.1:5000/api/cargo
@app.route('/api/cargo', methods=['DELETE']) # #API to delete a record from the cargo table
def delete_cargo():
    # Set up a connection
    myCreds = creds.Creds()
    conn = create_connection(myCreds.conString, myCreds.userName, myCreds.password, myCreds.dbName)

    # Get the json data, assign the id, execute the sql syntax to delete the record with the matching id
    request_data = request.get_json()
    delete_cargo = request_data['secondary_id']
    delete_sql = "DELETE FROM cargo WHERE secondary_id = %s" % (delete_cargo)
    execute_read_query(conn, delete_sql)
    conn.commit()

    return jsonify(True)

# ============================================
# Spaceship Table APIs
# ============================================
# Worked on by: Joseph Irving

@app.route('/api/spaceship/all', methods=['GET']) #API to get all records from the spaceship table
def api_all_spaceship():
    # Set up a connection to the DB
    myCreds = creds.Creds()
    conn = create_connection(myCreds.conString, myCreds.userName, myCreds.password, myCreds.dbName)
    sql = "SELECT * FROM spaceship"
    spaceships = execute_read_query(conn, sql) # Collects all records from the DB table and makes a list of dictionaries
    results = [] # Empty list to put the records in

    for item in spaceships:  # Loop through the list of dictionaries
        # Swaps captainid with the secondary_id from the captain table:
        sql = "SELECT secondary_id FROM captain WHERE id = %s" % (item['captainid'])
        captainid = execute_read_query(conn, sql)
        item['captainid'] = captainid[0]['secondary_id']

        del item['id']

        results.append(item)  # Add the result to list

    return jsonify(results)

# http://127.0.0.1:5000/api/spaceship
@app.route('/api/spaceship', methods=['GET']) #API to get a record from the spaceship table
def api_spaceship_record():
    if 'secondary_id' in request.args: # only if a secondary_id is provided as an argument, proceed
        # Gets the info from the arguments
        secondary_id = int(request.args['secondary_id'])
    else:
        no_id = 'ERROR: No ID provided!'
        return jsonify(no_id)

    # Set up a connection to the DB
    myCreds = creds.Creds()
    conn = create_connection(myCreds.conString, myCreds.userName, myCreds.password, myCreds.dbName)
    sql = "SELECT * FROM spaceship"
    spaceship = execute_read_query(conn, sql) # Collects all records from the DB table and makes a list of dictionaries
    results = [] # Empty list to put the record in

    for item in spaceship: # Loop through the list of dictionaries
        if item['secondary_id'] == secondary_id: # Find the one with the matching ID
            # Swaps captainid with the secondary_id from the captain table:
            sql = "SELECT secondary_id FROM captain WHERE id = %s" % (item['captainid'])
            captainid = execute_read_query(conn, sql)
            item['captainid'] = captainid[0]['secondary_id']

            del item['id']

            results.append(item) # Add the result to list

    return jsonify(results)


@app.route('/api/spaceship', methods=['POST'])  # API to add new spaceship to the spaceship table
def add_spaceship():
    # Set up a connection the DB
    myCreds = creds.Creds()
    conn = create_connection(myCreds.conString, myCreds.userName, myCreds.password, myCreds.dbName)

    request_data = request.get_json()  # gets the info from the JSON package

    # Check if all 3 fields were provided, otherwise return an error message
    if 'secondary_id' not in request_data or 'maxweight' not in request_data or 'captainid' not in request_data:
        missing = 'ERROR: All fields (secondary_id, maxweight, captainid) are required to add a new spaceship!'
        return jsonify(missing)

    # Assign JSON data to the proper variables
    secondary_id = request_data['secondary_id']
    maxweight = request_data['maxweight']
    captainid = request_data['captainid'] # this is actually the secondary_id for captain

    # Get the actual captain ID using the secondary_id
    sql = "SELECT id FROM captain WHERE secondary_id = '%s'" % captainid
    captain_result = execute_read_query(conn, sql)
    captain_id = captain_result[0]['id']

    # Insert the new spaceship into the table
    sql = "INSERT INTO spaceship (secondary_id, maxweight, captainid) VALUES ('%s', %s, %s)" % (secondary_id, maxweight, captain_id)
    execute_read_query(conn, sql)
    conn.commit()

    return jsonify(True)

@app.route('/api/spaceship', methods=['PUT']) #API to update spaceship record
def update_spaceship():
    # Set up a connection to the DB
    myCreds = creds.Creds()
    conn = create_connection(myCreds.conString, myCreds.userName, myCreds.password, myCreds.dbName)

    # Get the json data and assign it to the proper variables
    request_data = request.get_json()
    if 'secondary_id' in request_data: # only if a secondary_id is provided in the json data will it proceed
        secondary_id = int(request_data['secondary_id'])
    else:
        no_id = 'ERROR: No ID provided!'
        return jsonify(no_id)

    # Check if the captain_id is provided in the json data, and then get the actual captain_id from the captain table
    if 'captainid' in request_data:
        captain_secondary_id = request_data['captainid']
        sql = "SELECT id FROM captain WHERE secondary_id = %s" % (captain_secondary_id)
        captain_id = execute_read_query(conn, sql)
        captain_id = captain_id[0]['id']

    # Go through to check for the rest of the attributes and update only the ones provided
    if 'maxweight' in request_data:
        updated_maxweight = request_data['maxweight']
        sql = "UPDATE spaceship SET maxweight = %s WHERE secondary_id = %s" % (updated_maxweight, secondary_id)
        execute_read_query(conn, sql)
    if 'captainid' in request_data:
        sql = "UPDATE spaceship SET captainid = %s WHERE secondary_id = %s" % (captain_id, secondary_id)
        execute_read_query(conn, sql)

    conn.commit() # commits any changes from the above commands

    return jsonify(True)

@app.route('/api/spaceship', methods=['DELETE']) #API to delete a record from the spaceship table
def delete_spaceship():
    # Set up a connection
    myCreds = creds.Creds()
    conn = create_connection(myCreds.conString, myCreds.userName, myCreds.password, myCreds.dbName)

    # Get the json data, assign the id, execute the sql to delete the record with the matching id
    request_data = request.get_json()
    delete_spaceship = request_data['secondary_id']
    delete_sql = "DELETE FROM spaceship WHERE secondary_id = %s" % (delete_spaceship)
    execute_read_query(conn, delete_sql)
    conn.commit()

    return jsonify(True)


# ============================================
# Captain Table APIs
# ============================================
# Worked on by: Becky Tseng

@app.route('/api/captain/all', methods=['GET']) #API to get all records from the captain table
def api_all_captain():
    # Set up a connection to the DB
    myCreds = creds.Creds()
    conn = create_connection(myCreds.conString, myCreds.userName, myCreds.password, myCreds.dbName)
    sql = "SELECT * FROM captain"
    captains = execute_read_query(conn, sql) # Collects all records from the DB table and makes a list of dictionaries
    results = [] # Empty list to put the records in

    for item in captains:  # Loop through the list of dictionaries
        # Swaps captainid with the secondary_id from the captain table:

        del item['id']

        results.append(item)  # Add the result to list

    return jsonify(results)


@app.route('/api/captain', methods=['GET'])
def get_captain_record():
    myCreds = creds.Creds()
    conn = create_connection(myCreds.conString, myCreds.userName, myCreds.password, myCreds.dbName)
    if 'secondary_id' in request.args: # only if a secondary_id is provided as an argument, proceed
        # Gets the info from the arguments
        secondary_id = int(request.args['secondary_id'])
    else:
        no_id = 'ERROR: No ID provided!'
        return jsonify(no_id)

    sql = "SELECT * FROM captain"
    captain = execute_read_query(conn, sql) # Collects all records from the DB table and makes a list of dictionaries
    captain_record = [] # Empty string to put the record in

    for item in captain: # Loop through the list of dictionaries
        if item['secondary_id'] == secondary_id: # Find the one with the matching ID
            del item['id']
            captain_record.append(item) # Add the result to list
    return jsonify(captain_record)

@app.route('/api/captain', methods=['POST'])
def new_captain_record():
    # requesting new data to put in database
    request_data = request.get_json()

    if 'secondary_id' not in request_data or 'firstname' not in request_data or 'lastname' not in request_data or 'rank' not in request_data or 'homeplanet' not in request_data:
        missing = 'ERROR: All fields (secondary_id, firstname, lastname, rank, homeplanet) are required to add a new captain!'
        return jsonify(missing)

    secondary_id = request_data['secondary_id']
    firstname = request_data['firstname']
    lastname = request_data['lastname']
    rank = request_data['rank']
    homeplanet = request_data['homeplanet']
    print(request_data)
    print(secondary_id, firstname, lastname, rank, homeplanet)
    # Set up a connection the DB
    myCreds = creds.Creds()
    conn = create_connection(myCreds.conString, myCreds.userName, myCreds.password, myCreds.dbName)
    # SQL query to add a new captain information to the database
    sql = "INSERT INTO captain (secondary_id, firstname, lastname, `rank`, homeplanet) VALUES ('%s', '%s', '%s', '%s', '%s')" % (secondary_id, firstname, lastname, rank, homeplanet)
    execute_read_query(conn, sql)
    conn.commit()

    return("Captain added successfully") # Success

@app.route('/api/captain', methods=['PUT'])
def update_captain_record():
    myCreds = creds.Creds()
    conn = create_connection(myCreds.conString, myCreds.userName, myCreds.password, myCreds.dbName)   
    request_data = request.get_json() 
    newFirstName = request_data['firstname']
    newLastName = request_data['lastname']
    newRank = request_data['rank']
    newHomePlanet = request_data['homeplanet']
    inputID = request_data['secondary_id']

    if 'secondary_id' not in request_data or 'firstname' not in request_data or 'lastname' not in request_data or 'rank' not in request_data or 'homeplanet' not in request_data:
        missing = 'ERROR: All fields (secondary_id, firstname, lastname, rank, homeplanet) are required to add a new captain!'
        return jsonify(missing)

    # if the user wants to update one row in the 'captain' table, he/she will need to input values for all 4 variables (first name, last name, rank, home planet)
    # The row is identified by the id number
    sqlQuery = "UPDATE captain SET firstname='%s', lastname='%s', `rank` ='%s', homeplanet='%s' WHERE secondary_id ='%s' " % (newFirstName, newLastName, newRank, newHomePlanet, inputID)
    execute_query(conn, sqlQuery)
    conn.commit()
    
    return jsonify(True)

@app.route('/api/captain', methods=['DELETE'])
def delete_captain_record():

    # establishes connection to database
    request_data = request.get_json()
    idToDelete = request_data['secondary_id'] 
    myCreds = creds.Creds()
    conn = create_connection(myCreds.conString, myCreds.userName, myCreds.password, myCreds.dbName)
    sqlDeleteQuery = "DELETE FROM captain WHERE secondary_id = %s" % (idToDelete) # creates a SQL query to delete the row with ID identified
    execute_query(conn, sqlDeleteQuery) # executes the query
    conn.commit()
    
    return jsonify(True)

# ============================================
# Login API
# ============================================
# Worked on by: Becky Tseng

authorized_users = [
    {
        # default user
        'username': 'username',
        'password': 'password',
        'role': 'default',
    },
    {
        #admin user
        'username': 'admin',
        'password': 'password2.0',
        'role': 'admin',

    }
]


@app.route('/api/login', methods=['GET'])
def authenticate():
    username = request.headers.get('username') #get the header parameters. request headers are interpreted as dictionaries, so value access is easy and direct
    password = request.headers.get('password')
    print('username:', username)
    print('password:', password)
    for au in authorized_users: #loop over all users and find one that is authorized to access
        if au['username'] == username and au['password'] == password: #found an authorized user
            return 'True'
    return 'False' # Authentication failed

app.run()

# ============================================
#               References
# ============================================
# Code from class and ChatGPT for minor bug fixes
