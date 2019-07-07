import logging
import os
import traceback

from src.main.worker import Worker

worker = Worker()

logging.basicConfig(level=os.environ.get("LOGLEVEL", "INFO"))
logging.FileHandler('/var/tmp/myapp.log')


if __name__ == '__main__':
    try:
        worker.main()
    except Exception:
        worker.driver.quit()
        traceback.print_exc()
