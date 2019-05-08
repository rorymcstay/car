import traceback

from src.main.worker import Worker

worker = Worker()

if __name__ == '__main__':
    try:
        worker.main()
    except Exception:
        worker.driver.quit()
        traceback.print_exc()
