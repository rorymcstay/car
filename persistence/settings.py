import os

nanny_params = {
    "host": os.getenv("NANNY_HOST", "localhost"),
    "port": os.getenv("FLASK_PORT", 5003),
    "api_prefix": "containercontroller",
    "params_manager": "parametercontroller"
}

database_parameters = {
    "host": os.getenv("DATABSE_HOST", "database"),
    "port": os.getenv("DATABASE_PORT", 5432),
    "database": "postgres",
    "user": "postgres",
    "password": "postgres"
}
