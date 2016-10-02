# shotgun_webservice
Contains the web service calls for all the services related to shotgun.
Means of communication is using JSON
Following URLs and JSON will guide you with going through web calls
--------------------- Registration Page --------------------
URL : http://ec2-54-191-60-17.us-west-2.compute.amazonaws.com:8080/register
Input Json:
{
	"firstname":"test",
	"lastname":"testing",
	"username":"test",
	"password":"test",
	"number":123,
	"carowner":true
}

Output Json:
{
  "message": "test registered successfully as test .  Now Login!"
}

--------------------- Login Page -----------------------------
URL: http://ec2-54-191-60-17.us-west-2.compute.amazonaws.com:8080/login
Input Json:
{
	"username":"test",
	"password":"test"
}

Output Json:

{
  "car_owner": "True",
  "cust_id": "57f0573205603b27f818fc13",
  "login": true
}tv

------------- Garage and questionarie ---------------------------------
URL: http://ec2-54-191-60-17.us-west-2.compute.amazonaws.com:8080/questions
Input Json:
{
	"customer_id":"57f0573205603b27f818fc13",
	"answer": true,
	"source_lat": 32.733355,
	"source_lon": -97.110611
}

Output Json:
{
  "results": [
    {
      "garage_name": "Oil States Industries Inc",
      "garage_src_lat": 32.7353818,
      "garage_src_lon": -97.1101989
    },
    {
      "garage_name": "Transmission Repair King | Transmission Experts Arlington | Transmission Company",
      "garage_src_lat": 32.737671,
      "garage_src_lon": -97.110897
    },
    {
      "garage_name": "Action Glass",
      "garage_src_lat": 32.7353818,
      "garage_src_lon": -97.1101989
    },
    {
      "garage_name": "City Glass & Mirror",
      "garage_src_lat": 32.7354613,
      "garage_src_lon": -97.1104422
    }
  ]
}

----------------------Request Pool-----------------------------------
URL: http://ec2-54-191-60-17.us-west-2.compute.amazonaws.com:8080/request_pool
Input JSON:
{
	"src_lat":32.751,
	"src_lon":-97.096,
	"dest_lon":-97.097,
	"dest_lat":32.7515,
	"customer_id":"57f05c405a6c24206075f721"
}
Output JSON:
{
  "message": "done"
}

-------------------------------------Provide Pool--------------------------------------
URL: http://ec2-54-191-60-17.us-west-2.compute.amazonaws.com:8080/provide_pool
Input JSON:
{
	"customer_id":"57f0573205603b27f818fc13"
}
Output JSON:
[
  {
    "name": "test",
    "phonenumber": 123
  },
  {
    "name": "test3",
    "phonenumber": 123
  }
]


--------------------------------------Add Destination ------------------------------------------------
URL: http://ec2-54-191-60-17.us-west-2.compute.amazonaws.com:8080/add_destination
Input JSON:
{
	"customer_id":"57f0573205603b27f818fc13",
	"dest_lat": 20.21,
	"dest_lon": -97.11
}
Output JSON:
{
  "message": "Destination updated successfully"
}


------------------------------- Get Weather -----------------------------------------------
URL: http://ec2-54-191-60-17.us-west-2.compute.amazonaws.com:8080/weather
Input JSON:
{
	"customer_id":"57f0573205603b27f818fc13"
}
Output JSON:
[
  {
    "check0": "Check the lights of the car"
  }
]
