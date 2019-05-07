from src.main.loader import ResultLoader

if __name__ == '__main__':
    rl = ResultLoader()
    while True:
        rl.consumeResults()