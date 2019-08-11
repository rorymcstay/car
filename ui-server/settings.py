import os

kafka_params = {
    "bootstrap_servers": [os.getenv("KAFKA_ADDRESS", "localhost:29092")],
}

hazelcast_params = {
    "host": os.getenv("HAZELCAST_HOST", "localhost"), "port": os.getenv("HAZELCAST_PORT", 5701)
}

mongo_params = {
    "host": os.getenv("MONGO_HOST", "localhost:27017"),
    "username": os.getenv("MONGO_USER", "root"),
    "password": os.getenv("MONGO_PASS", "root"),
    "serverSelectionTimeoutMS": 5
}