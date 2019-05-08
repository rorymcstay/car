import os


home_config = {
    "donedeal": {
        "skeleton": ["https://www.donedeal.co.uk/cars/", "{make}", "/", "{model}", "?sort=", "{sort}"],
        "sort_first": {
            "newest": "publishdate%20desc",
            "oldest": "publishdate%20asc",
            "high": "price%20desc",
            "low": "price%20asc"
        }
    }
}

hazelcast_params = {
    "host": os.getenv("HAZELCAST_HOST"), "port": os.getenv("HAZELCAST_PORT", 5701)
}
