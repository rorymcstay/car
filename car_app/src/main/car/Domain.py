import hashlib

from bson import ObjectId


def make_id(string):
    id = hashlib.sha3_224(string.encode('utf-8')).hexdigest()
    id = id[:24]
    return ObjectId(id)


class CarDetails:
    def __init__(self, make, model, year, color, mileage, owners, engineCapacity, engineType, fuelType, bodyStyle, numberDoors):
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
        self._id = make_id('{}:{}'.format(make, model))


class CarType:
    def __init__(self, make, model, year=None):
        self.make = make
        self.model = model
        self.year = year
        self._id = make_id('{}:{}'.format(make, model))

    def __dict__(self):
        return {'_id': self._id, 'make': self.make, 'model': self.model, 'year': self.year}

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


class AdDetails:
    def __init__(self, url, dateCreated, special, location, sellerType, price, currency, carType):
        self.carType = carType
        self.dateCreated = dateCreated
        self.special = special
        self.location = location
        self.sellerType = sellerType
        self.price = price
        self.currency = currency
        self.url = url


class Location:
    def __init__(self, country, county, postcode):
        self.country = country
        self.county = county
        self.postcode = postcode


class MarketDeatils:
    def __init__(self, name,
                 result_css,
                 result_exclude,
                 wait_for_car,
                 json_identifier,
                 next_page_xpath,
                 result_stub):
        self.name = name
        self.result_css = result_css
        self.result_exclude = result_exclude
        self.wait_for_car = wait_for_car
        self.json_identifier = json_identifier
        self.next_page_xpath = next_page_xpath
        self.result_stub = result_stub
