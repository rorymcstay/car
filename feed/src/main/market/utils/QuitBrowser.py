class BrowserQuit(Exception):
    def __init__(self, e=None):
        super(e)


def quit_browser(browser, e=None):
    """

    :type e: class:Exception
    """
    browser.driver.quit()
    raise BrowserQuit(e)
