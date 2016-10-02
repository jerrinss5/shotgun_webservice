from flask import request, Flask, jsonify
from pymongo import MongoClient
from bson.objectid import ObjectId
import urllib, json, time, math
from math import sin, cos, sqrt, atan2, radians
import datetime

app = Flask(__name__)

def mongo_db_connection():
    # connection parameter for the Mongo
    try:
        # Google Mongo DB
        client = MongoClient('mongodb://54.191.60.17:27017/')
        # Localhost Mongo DB
        # client = MongoClient('mongodb://localhost:27017')
        # Creating DB
        db = client.shotgun
        return db, client
    except:
        error_msg = {"database message" : "Unable to connect to MongoDB! Try Again"}
        # change it to json equivalent message
        return jsonify(error_msg)


# close the db connection
def close_mongo_db_connection(client):
    client.close()


# default index page
@app.route('/',methods=['GET'])
def test():
    print 'testing page'
    return 'Hello'


# registration page
@app.route('/register', methods=['POST'])
def register():
    # read the json file from request
    json_file = request.get_json()
    # reading json data
    firstname = json_file['firstname']
    lastname = json_file['lastname']
    username = json_file['username']
    # TODO: may look for encrypting this later
    password = json_file['password']
    phone_number = int(json_file['number'])
    car_owner = bool(json_file['carowner'])
    # debug line to check username being read from json
    # print username
    # calling the connection to database method
    db, client = mongo_db_connection()
    # creating the json entry to be inserted in mongo
    user_entry = {
        "firstname": firstname,
        "lastname": lastname,
        "username": username,
        "password": password,
        "phone_number": phone_number,
        "car_owner": car_owner
    }
    # calling the collection to insert the customer data
    customer_collection = db.customer
    # inserting the user data into mongo db
    user = customer_collection.insert(user_entry)
    # closing the database connection
    close_mongo_db_connection(client)
    # checking if the insertion was successful
    if user:
        message = {"message": "success"}
    else:
        message = {"message": "fail"}
    # returning json value
    return jsonify(message)


# login page
@app.route('/login', methods=['POST'])
def login():
    # reading the json file
    json_file = request.get_json()
    # reading the json data
    username = json_file['username']
    # TODO: again encrpytion
    password = json_file['password']
    # calling mongo db connection call
    db, client = mongo_db_connection()
    # creating the json entry to check the login of the inputted user
    user_credential_check = {
        "username": username,
        "password": password
    }
    # calling the collection to insert the customer data
    customer_collection = db.customer
    # firing the query in db
    user = customer_collection.find_one(user_credential_check)
    # closing the db connection
    close_mongo_db_connection(client)
    # checking if the login was successful
    if user:
        cust_id = str(user['_id'])
        car_owner = str(user['car_owner'])
        login_detail = {"login": True, "cust_id": cust_id, 'car_owner':car_owner}
    else:
        login_detail = {"login": False, "cust_id": ""}

    return jsonify(login_detail)


# storing questionnaire and answers for the users
@app.route('/questions', methods=['POST'])
def questions_answers():
    # reading the json file
    json_file = request.get_json()
    # reading the individual values
    customer_id = str(json_file['customer_id'])
    answer = bool(json_file['answer'])
    cust_source_lat = float(json_file['source_lat'])
    cust_source_lon = float(json_file['source_lon'])
    cust_quest = {"cust_id": customer_id}
    # get mongo connection
    db, client = mongo_db_connection()
    # calling the customer questions collection
    customer_question_collection = db.customer_questions
    # checking if the customer question answer is in the db
    user = customer_question_collection.find_one(cust_quest)
    # checking if the user had already answered questions
    if user:
        # if yes, just update the answer
        cust_quest_id = user['_id']
        cust_quest_id_query = {"_id": cust_quest_id}
        cust_query = {"answer": answer}
        cust_set_query = {"$set": cust_query}
        customer_question_collection.update_one(cust_quest_id_query, cust_set_query)
        message = {"message": "success"}
    else:
        # else insert the question with answer and customer details
        customer_question_query = {
            "cust_id": customer_id,
            "answer": answer
        }
        cust_quest = customer_question_collection.insert(customer_question_query)
        if cust_quest:
            message = {"message": "success"}
        else:
            message = {"message": "fail"}
    # inserting or updating customer location details and then getting the nearest garage location if any of the answer is true
    # getting customer location collection
    customer_location_details_collection = db.customer_location
    # creating query to check if the customer has already entry in the database
    customer_location_entry_detail = {
        'cust_id': customer_id
    }
    cust_location_results = customer_location_details_collection.find_one(customer_location_entry_detail)
    if cust_location_results:
        # the customer has previous location details which can be updated
        cust_location_results_id = cust_location_results['_id']
        # update query for the location
        cust_location_update_query = {
            "src_lat": cust_source_lat,
            "src_lon": cust_source_lon,
        }
        cust_location_update_query_set = {
            "$set": cust_location_update_query
        }
        cust_location_collection_id = {
            "_id": cust_location_results_id
        }
        # firing the update query to update the current src an dest lat lon
        customer_location_details_collection.update_one(cust_location_collection_id, cust_location_update_query_set)
        message = {"message": "location updated"}
    else:
        # customer doesn't have any location details so inserting location details
        cust_location_insert_query = {
            "cust_id": customer_id,
            "src_lat": cust_source_lat,
            "src_lon": cust_source_lon,
        }
        customer_location_details_collection.insert(cust_location_insert_query)
        close_mongo_db_connection(client)
        message = {"message": "location inserted"}

    # if the answer is true get garage location nearby
    if answer:
        url = "https://maps.googleapis.com/maps/api/place/nearbysearch/json?location="+str(cust_source_lat)+","+str(cust_source_lon)+"&radius=500&type=car_repair&key="
        response = urllib.urlopen(url)
        garage_data = json.loads(response.read())
        # pretty print statment
        # print json.dumps(garage_data, indent=4, sort_keys=True)
        garage_results = garage_data['results']
        garage_results_len = len(garage_results)
        garage_return_results = []
        for run in range(0, garage_results_len):
            garage_inner = {
                "garage_src_lat":garage_results[run]['geometry']['location']['lat'],
                "garage_src_lon":garage_results[run]['geometry']['location']['lng'],
                "garage_name":garage_results[run]['name']
            }
            garage_return_results.append(garage_inner)
        # debug purposes
        # print garage_return_results
        # print json.dumps(garage_return_results, indent=4, sort_keys=True)
    else:
        garage_return_results = ""
    return jsonify(results=garage_return_results)


@app.route('/weather',methods=['POST'])
def find_weather():
    # reading the json file
    json_file = request.get_json()
    # getting the customer id
    customer_id = str(json_file['customer_id'])
    # getting the lat lon for the customer
    customer_query = {"cust_id":customer_id}
    #make the connection to the database
    db, client = mongo_db_connection()
    # getting customer collection from db
    customer_location_collection = db.customer_location
    # finding the customer based on id
    customer = customer_location_collection.find_one(customer_query)
    #get the destination latitude and longitude for the customer from the database
    dest_lat = customer['dest_lat']
    dest_log = customer['dest_lon']
    #pass the destination latitude and longitude to the url to get the weather
    url="http://api.openweathermap.org/data/2.5/weather?lat="+str(dest_lat)+"&lon="+str(dest_log)+"&appid="
    response=urllib.urlopen(url)
    data=json.loads(response.read())
    # print data
    # print json.dumps(data, indent=4, sort_keys=True)
    # reading the json data
    main_w=data['weather'][0]['main']

    if(main_w=='Rain'):
        send_data=db.weather.find_one({'title':'Rain'})
    elif(main_w=='Thunderstrom'):
        send_data = db.weather.find_one({'title': 'Thunderstrom'})
    elif(main_w=='Snow'):
        send_data = db.weather.find_one({'title': 'Snow'})
    elif(main_w=='Drizzle'):
        send_data = db.weather.find_one({'title': 'Drizzle'})
    elif(main_w=='Atmosphere'):
        send_data = db.weather.find_one({'title': 'Atmosphere'})
    elif(main_w=='Clear'):
        send_data = db.weather.find_one({'title': 'Clear'})
    elif(main_w=='Clouds'):
        send_data = db.weather.find_one({'title': 'Clouds'})
    else:
        send_data = db.weather.find_one({'title': 'Extreme'})

    check_list = send_data['checks']
    check_list_ext = ""
    for run in range(len(check_list)):
        check_list_ext+=check_list[run]+","

    message = {"check": str(check_list_ext)}
    close_mongo_db_connection(client)
    return jsonify(message)


@app.route('/provide_pool',methods=['POST'])
def provide_pool():
    # reading the json file
    json_file = request.get_json()
    # getting the customer id
    customer_id = str(json_file['customer_id'])
    # getting the lat lon for the customer
    customer_query = {"cust_id": customer_id}
    # getting the mongo connection
    db, client = mongo_db_connection()
    # getting customer collection from db
    customer_location_collection = db.customer_location
    # getting customer collection from db
    customer_collection = db.customer
    # finding the customer based on id
    customer = customer_location_collection.find_one(customer_query)
    # get the destination latitude and longitude for the customer from the database
    dest_lat = customer['dest_lat']
    dest_lon = customer['dest_lon']
    src_lat = customer['src_lat']
    src_lon = customer['src_lon']

    # getting customer collection from db
    requester_location_collection = db.requester
    # calling the requester's location details
    # current_milli_time = int(round(time.time() * 1000))
    # for latest 30 min request
    # current_time_cond = current_milli_time - (1000 * 60 * 1)
    current_time_cond = datetime.datetime.now() - datetime.timedelta(minutes=60)
    valid_requester_query = {
        "timestamp":
            {
                "$gt": current_time_cond
        }
    }
    requester_details = requester_location_collection.find(valid_requester_query)
    valid_requesters = []
    for requester_detail in requester_details:
        print 'inside'
        requester_src_lat = requester_detail['src_lat']
        requester_src_lon = requester_detail['src_lon']
        requester_dest_lat = requester_detail['dest_lat']
        requester_dest_lon = requester_detail['dest_lon']
        customer_id = requester_detail['cust_id']
        print customer_id
        src_distance = distance(src_lat, src_lon, requester_src_lat, requester_src_lon)
        dest_distance = distance(dest_lat, dest_lon, requester_dest_lat, requester_dest_lon)
        # distance between request driver_origin and passenger_origin

        # give ride only if in 3 mile radius

        if src_distance <= 3.0 and dest_distance <= 3.0:
            cust_query = {"_id": ObjectId(customer_id)}
            requester = customer_collection.find_one(cust_query)
            valid_dict = {
                "name": requester['firstname'],
                "phonenumber": requester['phone_number']
            }
            valid_requesters.append(valid_dict)
        close_mongo_db_connection(client)
    # print valid_requesters
    return jsonify(valid_requesters)


@app.route('/request_pool',methods=['POST'])
def req_pool():
    db, client = mongo_db_connection()
    json_file = request.get_json()
    src_lon=json_file['src_lon']
    src_lat=json_file['src_lat']
    dest_lon=json_file['dest_lon']
    dest_lat=json_file['dest_lat']
    cust_id=json_file['customer_id']
    time=datetime.datetime.now()
    # print time
    db.requester.insert({'cust_id':cust_id,'src_lon':src_lon,'src_lat':src_lat,'dest_lon':dest_lon,'dest_lat':dest_lat,'timestamp':time})
    message = {"message":"done"}
    close_mongo_db_connection(client)
    return jsonify(message)


# storing destination
@app.route('/add_destination', methods=['POST'])
def add_destination():
    # reading the json file
    json_file = request.get_json()
    # getting the customer id
    customer_id = str(json_file['customer_id'])
    # getting the destination
    dest_lat = float(json_file['dest_lat'])
    dest_lon = float(json_file['dest_lon'])
    # getting the lat lon for the customer
    customer_query = {"cust_id": customer_id}
    # update query
    cust_update_query = {
        "dest_lat": dest_lat,
        "dest_lon": dest_lon
    }
    cust_update_query_set = {
        "$set" : cust_update_query
    }
    # getting the mongo connection
    db, client = mongo_db_connection()
    # getting customer collection from db
    customer_location_collection = db.customer_location
    # finding the customer based on id
    customer = customer_location_collection.update_one(customer_query, cust_update_query_set)
    message = {"message": "Destination updated successfully"}

    return jsonify(message)


def distance(lat1,lon1,lat2,lon2):
    #approx radius of earth
    R = 3959.0
    lat1, lat2, lon1, lon2 = map(radians, [lat1, lat2, lon1, lon2])

    dlat = lat2-lat1
    dlon = lon2-lon1

    a = sin(dlat / 2)**2 + cos(lat1) * cos(lat2) * sin(dlon / 2)**2
    c = 2 * atan2(sqrt(a), sqrt(1 - a))

    distance = R * c
    # print distance
    return distance


if __name__ == '__main__':
    #app.run(host='localhost', port=8080, debug=True)
    app.run(host='ec2-54-191-60-17.us-west-2.compute.amazonaws.com', port=8080, debug=True)