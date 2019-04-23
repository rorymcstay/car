import datetime
import logging as log
import traceback
from time import time

from src.main.car.Domain import CarDetails, Location, AdDetails, CarType, Car
from src.main.market.mapping.mappingTools import index_of_list_where_key_equals, get_photos_in_a_list
from src.main.utils.LogGenerator import write_log, LogGenerator

LOG = LogGenerator(log, 'mapping')


def DoneDeal(car_old: dict, url: str) -> Car:
    """
    :param car_old: the raw json object
    :return: returns a default car
    """
    now = datetime.datetime.now()
    start = time()
    try:
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
        write_log(LOG.info, msg="mapped carType")
    except Exception:
        traceback.print_exc()
        write_log(LOG.warning, msg="CarType mapping error")
        carType = {}

    try:
        if car_old['price'] == None:
            price = None
        else:
            price = car_old['price']
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
            price=price,
            currency="GBP", carType=carType)
        write_log(LOG.info, msg="mapped adDetails")
    except Exception:
        traceback.print_exc()

        write_log(LOG.warning, msg="AdDetails mapping error")
        adDetails = {}
    try:
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
                                                                                                       "name")][
                                    "value"],
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
                                                                                                        "name")][
                                    "value"])
        write_log(LOG.info, msg="mapped carDetails")
    except Exception:
        traceback.print_exc()
        write_log(LOG.warning, msg="CarDetails mapping error")
        carDetails = {}

    try:
        adDescription = car_old['description']
        adPhotos = get_photos_in_a_list('photos', 'large', car_old)
    except Exception:
        traceback.print_exc()
        write_log(LOG.warning, msg="description/photots mapping error")
        adDescription = None
        adPhotos = {}

    write_log(LOG.info, msg="finished mapping", time=time()-start)

    car = Car(adDetails, carDetails, adDescription, adPhotos)
    return car
