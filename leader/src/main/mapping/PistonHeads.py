from src.main.car.Domain import CarType, AdDetails, CarDetails, Car, Location
from src.main.mapping.mappingTools import find


def Mapper(car_old: dict, url: str) -> Car:
    """
    :param gen_key_extract('', car_old): the raw json object
    :return: returns a default car
    """

    carType = CarType(make=list(find('manufacturer', car_old)),
                      model=list(find('model', car_old)),

                      year=list(find('age', car_old)))
    adDetails = AdDetails(url=url,
                          dateCreated=list(find('xxx', car_old)),
                          special=False,
                          location=Location(
                              country=list(find("county", car_old)),
                              county=list(find('country', car_old)),
                              postcode=list(find("postcode", car_old))
                          ),
                          sellerType=list(find('category', car_old)),
                          price=list(find('price', car_old)),
                          currency=list(find('price_currency', car_old)),
                          carType=carType)

    carDetails=CarDetails(make=list(find('manufacturer', car_old)),
                          model=list(find('model', car_old)),
                          year=list(find('age', car_old)),
                          color=list(find('colour', car_old)),
                          mileage=list(find('fuel_type', car_old)),
                          owners=list(find('xxx', car_old)),
                          engineCapacity=list(find('size', car_old)),
                          engineType=list(find('size', car_old)),
                          fuelType=list(find('fuel_type', car_old)),
                          bodyStyle=list(find('style', car_old)),
                          numberDoors=list(find('xxx', car_old)))

    adPhotos = []
    adDescription = list(find('title', car_old))
    car = Car(adDetails, carDetails, adDescription[0], adPhotos)
    return car

if __name__ == '__main__':
    car_old = {
        "adzone": {},
        "content": {
            "title": "Used 2003 Porsche Boxster 986 [96-04] 24V TIPTRONIC S for sale in Down | Pistonheads",
            "type": "Ad Detail"
        },
        "motoring": {
            "co2_emissions": "259",
            "engine_size": "2700.0",
            "fuel_economy": "26.4",
            "fuel_type": "Petrol",
            "max_speed": "154",
            "transmission_type": "Automatic"
        },
        "navigation": {
            "hierarchy": [
                "Classifieds",
                "Used Cars",
                "Porsche",
                "Boxster 986 [96-04]"
            ],
            "locale": "en-US",
            "section": "Classifieds",
            "section_child1": "Used Cars",
            "section_child2": "Porsche",
            "section_child3": "Boxster 986 [96-04]",
            "site_domain": "www.pistonheads.com",
            "site_name": "PistonHeads",
            "sitecode": "PH"
        },
        "product": {
            "age": "2003",
            "category": "Used Cars",
            "city": "Newtownards",
            "colour": "Blue",
            "condition": "Used",
            "country": "GB",
            "county": "County Down",
            "id": "9466291",
            "location": "BT23",
            "manufacturer": "Porsche",
            "model": "Boxster 986 [96-04]",
            "postcode": "BT23",
            "price": "7950",
            "price_band": "7000",
            "price_currency": "GBP",
            "private_seller": "private",
            "product_edition": "24V TIPTRONIC S",
            "region": "Northern Ireland",
            "size": "2700.0",
            "style": "Convertible",
            "sub_category1": "Porsche",
            "sub_category2": "Boxster 986 [96-04]",
            "version": "2003"
        },
        "search": {}
    }

    t = Mapper(car_old, 'hello')
    print(t.__dict__())
