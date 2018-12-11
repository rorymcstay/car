# Classified car ad API


This program consists of 3 parts. A Parsing library for parsing html strings
to export JSON to enable the construction of a car object. A car class which
has multiple types representing each market place. The difference for each 
is the way in which it manipulates the JSON to construct the car class. The
car class is as follows:

    ["market1": "Car1_url": {
                Make: "Ford",
                Model: "Mondeo",
                Year: 2006,
                Mileage: 115000,
                Color: "Red",
                Price: 2500,
                Location: "Dublin",
                Photos:[
                    "url_link1",
                    "url_link2"
                ],
                Description: "This is a long string of the cars description"
                },
               "Car2_url" = {
               Make: "Porsche",
               Model: "916",
               Year: 2005,
               Mileage: 1000,
               Color: "Red",
               Price: 30000,
               Location: "London",
               Photos:[
                     "url_link1",
                     "url_link2"
               ],
               Description: "This is a long string of the cars description"
               }
      "market1":
    ]

## API Endopoings

#### make=car_make/model=car_model/year=car_year/color=car_color

#### Deployment

Package needs to be turned into deployable python app. AWS instance is setup
and git needs to be installed. A docker script must be made which starts
the database and backs it up.

Then a starting script must start the database client for python and update
the database since last time it logged on.

#### Search Methods

The URL construction of all sites allows for dynamically altering urls stubs
depending on search criteria. A route handler class must then be created.
Market classes will then inheret the functionality of the route handler.

## API

The API is used for querying the database and controlling the python application.

### Application commands

#### current support

    GET: http://127.0.0.1:5000/query/cars/ :
    body: {
        "query": {"make": "Nissan"},
        "projection": {"carDetails.make":1}
    }
    PUT: http://localhost:5000/command/add_market/donedeal
    body: {
    	"url_stub_1": "https://www.donedeal.co.uk/cars?sort=publishdate%20desc",
    	"url_stub_2": "&sort=publishdate%20desc",
    	"result_stub": "https://www.donedeal.co.uk/cars-for-sale/",
    	"wait_for":"searchResultsPanel",
    	"wait_for_car":"js-featured-block",
    	"n_page": "28",
    	"json_identifier": "window.adDetails",
    	"mapping":"DoneDeal",
    	"browser": "http://172.20.0.4:4444/wd/hub"
    }
    response: ok

    PUT: localhost:5000/command/initialise/donedeal/10
    response: ok

The main methods:

* `load_database(pages)` - intialises the database
* `market()` - defines a market class

* querying methods explained in



#### Live methods

Allow users to directly query all markets for the most recent cars bypassing
the database. This triggers the get_cars command and returns json directly
to the user.

    http://localhost/api/functions/live/car_make/car_model


###
Get methods allow users to retrive information on cars. This can either be

    http://localhost/api/data/since=7days/car_make/car_model

