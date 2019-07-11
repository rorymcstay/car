import os

hazelcast_params = {
    "host": os.getenv("HAZELCAST_HOST", "localhost"),
    "port": os.getenv("HAZELCAST_PORT", 5701)
}