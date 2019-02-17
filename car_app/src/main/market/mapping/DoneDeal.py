import logging
import datetime

from src.main.car.Domain import CarDetails, Location, AdDetails, CarType, make_id
from src.main.market.mapping.mappingTools import index_of_list_where_key_equals, get_photos_in_a_list


def DoneDeal(car_old, url):
    """
    :param car_old:
    :return: This function persists the car object to the MongoDb database
    """
    now = datetime.datetime.now()

    carType = CarType(make=car_old['displayAttributes'][index_of_list_where_key_equals("make",
                                                                                       car_old,
                                                                                       "displayAttributes",
                                                                                       "name")]["value"],
                      model=car_old['displayAttributes'][index_of_list_where_key_equals("model",
                                                                                        car_old,
                                                                                        "displayAttributes",
                                                                                        "name")]["value"],
                      year=car_old['displayAttributes'][index_of_list_where_key_equals("year",
                                                                                       car_old,
                                                                                       "displayAttributes",
                                                                                       "name")]["value"])

    adDetails = AdDetails(
        url=url,
        dateCreated=now.isoformat(),
        special=car_old['spotlight'],
        location=Location(
            country="Ireland",
            county=car_old['county'],
            postcode="NA"
        ),
        sellerType=car_old['seller']['type'],
        price=car_old['price'],
        currency="GBP", carType=carType)

    carDetails = CarDetails(make=carType.make, model=carType.model, year=carType.year,
                            color=car_old['displayAttributes'][index_of_list_where_key_equals("colour",
                                                                                              car_old,
                                                                                              "displayAttributes",
                                                                                              "name")]["value"],
                            mileage=car_old['displayAttributes'][index_of_list_where_key_equals("mileage",
                                                                                                car_old,
                                                                                                "displayAttributes",
                                                                                                "name")]["value"],
                            owners=car_old['displayAttributes'][index_of_list_where_key_equals("previousOwners",
                                                                                               car_old,
                                                                                               "displayAttributes",
                                                                                               "name")]["value"],
                            engineCapacity=car_old['displayAttributes'][index_of_list_where_key_equals("engine",
                                                                                                       car_old,
                                                                                                       "displayAttributes",
                                                                                                       "name")][
                                "value"],
                            engineType=car_old['displayAttributes'][index_of_list_where_key_equals("cylinders",
                                                                                                   car_old,
                                                                                                   "displayAttributes",
                                                                                                   "name")]["value"],
                            fuelType=car_old['displayAttributes'][index_of_list_where_key_equals("fuelType",
                                                                                                 car_old,
                                                                                                 "displayAttributes",
                                                                                                 "name")]["value"],
                            bodyStyle=car_old['displayAttributes'][index_of_list_where_key_equals("bodyType",
                                                                                                  car_old,
                                                                                                  "displayAttributes",
                                                                                                  "name")]["value"],
                            numberDoors=car_old['displayAttributes'][index_of_list_where_key_equals("numDoors",
                                                                                                    car_old,
                                                                                                    "displayAttributes",
                                                                                                    "name")]["value"])

    adDescription = car_old['description']
    adPhotos = get_photos_in_a_list('photos', 'large', car_old)
    logging.debug("Mapped donedeal car succesfully")

    car = dict(_id=make_id(url), adDetails=adDetails, carDetails=carDetails, adDescription=adDescription,
               adPhotos=adPhotos)

    return car
