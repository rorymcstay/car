import os

kafka_params = {
    "bootstrap_servers": [os.getenv("KAFKA_ADDRESS")],
}
