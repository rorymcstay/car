import os


nanny_params = {
    "host": os.getenv("NANNY_HOST", "localhost"),
    "port": os.getenv("FLASK_PORT", 5003),
    "api_prefix": "containercontroller",
    "params_manager": "parametercontroller"
}

kafka_params = {
    "bootstrap_servers": [os.getenv("KAFKA_ADDRESS", "localhost:29092")],
}

hazelcast_params = {
    "host": os.getenv("HAZELCAST_HOST", "localhost"), "port": os.getenv("HAZELCAST_PORT", 5701)
}

database_parameters = {
    "host": os.getenv("DATABSE_HOST", "localhost"),
    "port": os.getenv("DATABASE_PORT", 5432),
    "database": "postgres",
    "user": "postgres",
    "password": "postgres"
}
