from selenium.webdriver.support.wait import WebDriverWait


def test_next_page(market):
    market.crawler.driver.get(market.home)
    WebDriverWait(market.crawler.driver, 5)
    visits = []
    market.crawler.next_page()
    visits.append(market.crawler.driver.current_url)
    market.crawler.next_page()
    visits.append(market.crawler.driver.current_url)
    market.crawler.next_page()
    visits.append(market.crawler.driver.current_url)
    return visits


def test_result_page(market, url_result, url_car):
    market.crawler.driver.get(url_car)
    WebDriverWait(market.crawler.driver, 5)
    first = market.crawler.result_page()
    market.crawler.driver.get(url_result)
    WebDriverWait(market.crawler.driver, 5)
    second = market.crawler.result_page()
    return first and second


def test_get_raw_car(market, url):
    market.crawler.driver.get(url)
    WebDriverWait(market.crawler.driver, 5)
    car = market.crawler.get_raw_car()
    return car

def test_order_history(market, urls):
    market.history = urls
    market.crawler.order_history()
    return is_monotonically_increasing(market.crawler.history)


def is_monotonically_increasing(urls):
    return all(x < y for x, y in zip(urls, urls[1:]))
