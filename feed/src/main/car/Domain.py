import hashlib
from json import JSONEncoder
from typing import Dict

from bson import ObjectId

"""
Houses the standard car classes to map to
"""


class Encoder(JSONEncoder):
    """
    Extends JSONEncoder so that ~bson.ObjectId can be serialised to a string
    """
    def default(self, o):
        if isinstance(o, ObjectId):
            return str(0)
        else:
            return JSONEncoder.default(self, o)


def make_id(string) -> ObjectId:
    """
    default function for constructing an id for mongo persistence
    :param string: The attribute to
    :return:
    """
    id = hashlib.sha3_224(string.encode('utf-8')).hexdigest()
    id = id[:24]
    return ObjectId(id)


class CarDetails:
    _id: ObjectId

    def __init__(self, make, model, year, color, mileage, owners, engineCapacity, engineType, fuelType, bodyStyle,
                 numberDoors):
        self.numberDoors = numberDoors
        self.bodyStyle = bodyStyle
        self.fuelType = fuelType
        self.engineType = engineType
        self.engineCapacity = engineCapacity
        self.owners = owners
        self.mileage = mileage
        self.color = color
        self.year = year
        self.model = model
        self.make = make
        id = make_id('{}:{}'.format(make, model))
        self._id = id

class CarType:
    def __init__(self, make, model, year=None):
        self.make = make
        self.model = model
        self.year = year
        self._id = make_id('{}:{}'.format(make, model))

    def __dict__(self):
        return {'_id': self._id, 'make': self.make, 'model': self.model, 'year': self.year}

    def getId(self) -> ObjectId:
        return self._id

    def update_car_type(self, collection, year):
        """

        :type collection: Collection
        """
        x = collection.find_one({'_id': self._id})
        if x is None:
            collection.insert_one(self.__dict__())
            return
        if x['years'] is not None:
            x['years'].append(int(year))
            collection.update_one({'_id': self._id}, x)
            return

class Location:
    def __init__(self, country, county, postcode):
        self.country = country
        self.county = county
        self.postcode = postcode

    def __dict__(self):
        return dict(country=self.country, county=self.county, postcode=self.postcode)


class AdDetails:
    def __init__(self, url: str, dateCreated: str, special: bool, location: Location, sellerType, price, currency,
                 carType: CarType):
        self.carType = carType.__dict__()
        self.dateCreated = dateCreated
        self.special = special
        self.location = location.__dict__()
        self.sellerType = sellerType
        self.price = price
        self.currency = currency
        self.url = url
        self.previousPrices = []

    def __dict__(self):
        return dict(carType=self.carType, dateCreated=self.dateCreated, special=self.special, location=self.location,
                    price=self.price, currency=self.currency, url=self.url, previousPrices=self.previousPrices)


class MarketDetails:
    def __init__(self, name,
                 result_css,
                 result_exclude,
                 wait_for_car,
                 json_identifier,
                 next_page_xpath,
                 result_stub, next_button_text,
                 sort):
        self._id = make_id(name)
        self.sort = sort
        self.next_button_text = next_button_text
        self.name = name
        self.result_css = result_css
        self.result_exclude = result_exclude
        self.wait_for_car = wait_for_car
        self.json_identifier = json_identifier
        self.next_page_xpath = next_page_xpath
        self.result_stub = result_stub


class Car(object):
    _id: ObjectId

    def __init__(self, adDetails: AdDetails, carDetails: CarDetails, adDescription: str, adPhotos: list):
        """

        :type adDescription: str
        :type adPhotos: list
        :param adDetails:
        :param carDetails:
        :param adDescription:
        :param adPhotos:
        """
        self._id = make_id(adDetails.url)
        self.adDetails = adDetails
        self.carDetails = carDetails
        self.adDescription = adDescription
        self.adPhotos = adPhotos

    def __dict__(self):
        return dict(_id=self._id, adDetails=self.adDetails.__dict__(), carDetails=self.carDetails.__dict__,
                    adDescription=self.adDescription, adPhotos=self.adPhotos)

    def getId(self) -> ObjectId:
        return self._id

    def getAdDetails(self) -> AdDetails:
        return self.adDetails

    def getCarDetails(self) -> CarDetails:
        return self.carDetails
    
class Result:

    def __init__(self, items: Dict[str, str], url):

        self.items = items
        self.url = url

    def __dict__(self):
        return dict(id=self.url, **self.items)


