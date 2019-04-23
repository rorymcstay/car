import datetime
from time import time

from src.main.car.Domain import CarType, AdDetails, CarDetails, Car, Location


def Mapper(car_old: dict, url: str) -> Car:
    """
    :param car_old['']: the raw json object
    :return: returns a default car
    """
    now = datetime.datetime.now()
    start = time()
    car_old = car_old['result']
    try:
        carType = CarType(make=car_old[''],
                          model=car_old[''],
                          year=car_old[''])
    except:

        carType = {}
    try:
        adDetails = AdDetails(url=url,
                              dateCreated=car_old[''],
                              special=False,
                              location=Location(
                                  country="Ireland",
                                  county=car_old['']['county'],
                                  postcode="NA"
                              ),
                              sellerType=car_old[''],
                              price=car_old[''],
                              currency=car_old[''],
                              carType=carType)
    except:
        adDetails={}
    try:
        carDetails=CarDetails(make=car_old['factSheetDetails'][0],
                              model=car_old['factSheetDetails'][0],
                              year=car_old['factSheetDetails'][0],
                              color=car_old['factSheetDetails'][0],
                              mileage=car_old['factSheetDetails'][0],
                              owners=car_old['factSheetDetails'][0],
                              engineCapacity=car_old['factSheetDetails'][0],
                              engineType=car_old['factSheetDetails'][0],
                              fuelType=car_old['factSheetDetails'][0],
                              bodyStyle=car_old['factSheetDetails'][0],
                              numberDoors=car_old['factSheetDetails'][0])
    except:
        carDetails = {}
    adPhotos = []
    adDescription = car_old['']
    car = Car(adDetails, carDetails, adDescription, adPhotos)
    return car