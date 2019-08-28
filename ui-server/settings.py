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
feed_params = {
    "image": "car_feed",
    "success": "feed has started"
}

database_parameters = {
    "host": os.getenv("DATABSE_HOST", "localhost"),
    "port": os.getenv("DATABASE_PORT", 5432),
    "database": "postgres",
    "user": "postgres",
    "password": "postgres"
}
