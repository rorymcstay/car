""" This module is a collection of useful mapping tools."""


def index_of_list_where_key_equals(attribute, json, list_name, parent):
    """
    This function is used when we have a list of dictionaries and wish to find the
    index of an dictionaries where attribute_key = attribute. For example, find the
    index of the list in the dictionary named json where the value equals mileage.
    This way we can extract the mileage of that json/car.

    eg.

    parent: {list_name: [{attribute: make, value: Citroen}...{not of interest}]}

    :param attribute:
    :param json: the JSON object from market.cars
    :param list_name: the list name as in the source file parent
    :param parent: the object name in source where the list occurs
    :return: index of where the attribute passes in list
    """
    pos = next((index for (index, d) in enumerate(json[list_name])
                if d[parent] == attribute), 0)
    return pos


def get_photos_in_a_list(name_photos, key, json):
    """
    Get photos from size organised links into an array
    :param name_photos:
    :param key:
    :param json:
    :return: a list of car photo links
    """
    photos=[]
    j=0
    for i in json[name_photos]:
        photos.append(json[name_photos][j][key])
        j=j+1
    return photos


def find(key: str, value: dict) -> list:
    """
    finds a list of keys in value
    :type value: dict
    """

    if hasattr(value,'items'):
        for k, v in value.items():
            if k == key:
                yield v
            if isinstance(v, dict):
                for result in find(key, v):
                    yield result
            elif isinstance(v, list):
                for d in v:
                    for result in find(key, d):
                        yield result
