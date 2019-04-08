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
        carDetails=CarDetails(make=car_old[''],
                              model=car_old[''],
                              year=car_old[''],
                              color=car_old[''],
                              mileage=car_old[''],
                              owners=car_old[''],
                              engineCapacity=car_old[''],
                              engineType=car_old[''],
                              fuelType=car_old[''],
                              bodyStyle=car_old[''],
                              numberDoors=car_old[''])
    except:
        carDetails = {}
    adPhotos = []
    adDescription = car_old['']
    car = Car(adDetails, carDetails, adDescription, adPhotos)
    return car