### Setup Procedure

1. Install the required dependancies.

pip install fastapi uvicorn sqlalchemy databases

2. Run the application using the below command.

python app.py

### Open the following URL to play with the API "127.0.0.1:8000/docs"

### API details with test data

###################################

/create
{
  "street_no": "123",
  "city": "New York",
  "state": "NY",
  "country": "USA",
  "coordinates_l1": 40.7128,
  "coordinates_l2": -74.0060
}
{
  "street_no": "456",
  "city": "Los Angeles"
  "state": "NY",
  "country": "USA",
  "coordinates_l1": 40.7128,
  "coordinates_l2": -74.0060
}

###################################

/update/2
{
  "coordinates_l1": 34.0522,
  "coordinates_l2": -118.2437
}

###################################

/delete/2

###################################

/get_address

###################################

/addressess/filter

latitude=40.7128 longitude=-74.006 max_distance=50

###################################

