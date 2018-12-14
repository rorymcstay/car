from car.market.src.mongo_service.MongoService import MongoService

class Market:
    """
    This is the market class. You must specify the CSS identifier/selector
    to ensure the browser waits for that item before moving onto the next set of
    results.This. You must also provide the stub of the expected url of a results page.
    The market class is called by get_results() to fetch a specified number of pages
    in order, determined by the partial url strings.
    """

    def __init__(self, name, result_body_class, wait_for_car, json_identifier, next_page_css, mapping, webcrawler):

        """
        :type result_body_class: str
        :type name: object
        :param wait_for_car: This is the CSS item which must be loaded for an individual car to be loaded
        :param json_identifier: What the JSON
        :param mapping: The string of the file defining the mapping from source json to generic car object
        :param browser: url of selenium container hosting browser
        """
        self.next_page_css = next_page_css
        self.result_body_class = result_body_class
        self.name = name
        self.wait_for_car = wait_for_car
        self.json_identifier = json_identifier
        self.mapping = mapping
        self.key = {}
        self.webcrawler = webcrawler
        self.service = MongoService()

    def collect_cars(self, n, order):
        """
        Loads up the market's cache preparing it for mapping
        :param order:
        :param n:
        :return fills market.:
        """
        webcrawler = self.webcrawler
        webcrawler.DoneDeal(order)
        base = webcrawler.base
        webcrawler.driver.get(base)
        x = 0
        while x < n:
            webcrawler.load_queue()
            for result in webcrawler.queue:
                self.service.insert(webcrawler.get_result(result))
            webcrawler.next_page()
            x = x + 1
        return





    def initialise(self, n, service):
        for i in range(n):
            self.collect_cars(i)
            default_car = []
            for car in self.cars:
                try:
                    default_car.append(self.mapping(car))
                except:
                    print 'Parsing error'
            for car in default_car:
                service.insert(car)

    # TODO Make the watch method. When started, it will monitor a market place and repeatedly check for new cars
