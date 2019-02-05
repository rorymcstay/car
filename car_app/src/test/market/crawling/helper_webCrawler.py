from selenium.webdriver.support.wait import WebDriverWait


def test_next_page(market):
    market.webCrawler.driver.get(market.home)
    WebDriverWait(market.webCrawler.driver, 5)
    visits = []
    market.webCrawler.next_page()
    visits.append(market.webCrawler.driver.current_url)
    market.webCrawler.next_page()
    visits.append(market.webCrawler.driver.current_url)
    market.webCrawler.next_page()
    visits.append(market.webCrawler.driver.current_url)
    return visits


def test_result_page(market, url_result, url_car):
    market.webCrawler.driver.get(url_car)
    WebDriverWait(market.webCrawler.driver, 5)
    first = market.webCrawler.result_page()
    market.webCrawler.driver.get(url_result)
    WebDriverWait(market.webCrawler.driver, 5)
    second = market.webCrawler.result_page()
    return first and second


def test_get_raw_car(market, url):
    market.webCrawler.driver.get(url)
    WebDriverWait(market.webCrawler.driver, 5)
    car = market.webCrawler.get_raw_car()
    return car

def test_order_history(market, urls):
    market.history = urls
    market.webCrawler.order_history()
    return is_monotonically_increasing(market.webCrawler.history)


def is_monotonically_increasing(urls):
    return all(x < y for x, y in zip(urls, urls[1:]))
