import logging
import datetime
from src.main.market.mapping.mappingTools import index_of_list_where_key_equals, get_photos_in_a_list


def DoneDeal(car_old, url):
    """
    :param car_old:
    :return: This function persists the car object to the MongoDb database
    """
    now = datetime.datetime.now()

    car = {"adDetails": {
        "url": url,
        "date_created": now.isoformat(),
        "special": car_old['spotlight'],
        "location": {
            "country": "Ireland",
            "county": car_old['county'],
            "postcode": "NA",
        },
        "seller_type": car_old['seller']['type'],
        "price": car_old['price'],
        "currency": "GBP"
    },
        "carDetails": {
            "make": car_old['displayAttributes'][index_of_list_where_key_equals("make",
                                                                                car_old,
                                                                                "displayAttributes",
                                                                                "name")]["value"],
            "model": car_old['displayAttributes'][index_of_list_where_key_equals("model",
                                                                                 car_old,
                                                                                 "displayAttributes",
                                                                                 "name")]["value"],
            "year": car_old['displayAttributes'][index_of_list_where_key_equals("year",
                                                                                car_old,
                                                                                "displayAttributes",
                                                                                "name")]["value"],
            "color": car_old['displayAttributes'][index_of_list_where_key_equals("colour",
                                                                                 car_old,
                                                                                 "displayAttributes",
                                                                                 "name")]["value"],
            "mileage(m)": car_old['displayAttributes'][index_of_list_where_key_equals("mileage",
                                                                                      car_old,
                                                                                      "displayAttributes",
                                                                                      "name")]["value"],
            "owners": car_old['displayAttributes'][index_of_list_where_key_equals("previousOwners",
                                                                                  car_old,
                                                                                  "displayAttributes",
                                                                                  "name")]["value"],
            "engine_capacity": car_old['displayAttributes'][index_of_list_where_key_equals("engine",
                                                                                           car_old,
                                                                                           "displayAttributes",
                                                                                           "name")]["value"],
            "engine_type": car_old['displayAttributes'][index_of_list_where_key_equals("cylinders",
                                                                                       car_old,
                                                                                       "displayAttributes",
                                                                                       "name")]["value"],
            "fuel_type": car_old['displayAttributes'][index_of_list_where_key_equals("fuelType",
                                                                                     car_old,
                                                                                     "displayAttributes",
                                                                                     "name")]["value"],
            "body_style": car_old['displayAttributes'][index_of_list_where_key_equals("bodyType",
                                                                                      car_old,
                                                                                      "displayAttributes",
                                                                                      "name")]["value"],
            "number_doors": car_old['displayAttributes'][index_of_list_where_key_equals("numDoors",
                                                                                        car_old,
                                                                                        "displayAttributes",
                                                                                        "name")]["value"]
        },
        "adDescription": car_old['description'],
        "adPhotos": get_photos_in_a_list('photos', 'large', car_old)}
    logging.debug("Mapped donedeal car succesfully")
    return car
