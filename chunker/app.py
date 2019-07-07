import logging
import os

from src.main.service import Pagechunker

logging.basicConfig(level=os.environ.get("LOGLEVEL", "INFO"))
logging.FileHandler('/var/tmp/myapp.log')



if __name__ == '__main__':
    pageChunker = Pagechunker()
    while True:
        pageChunker.main()
