This repo contains the individual services of an automated data collection tool.

# Current functionality
1. car_feed is configurable with only 6 parameters and a mapping
2. car_feed can parse a car data item from a website in parrallel.
3. car_feed exposes an iterator over a rest api
4. car_feed can store cars in a cache on command.
5. car_feed can pick up where it last left off when hydrating cache
6. car_feed can be focused on a different car make/model
6. car_learning can supply dataframes of cars over rest api

# Roadmap
1. car_feed to supply raw car objects
2. car_mapper seperate microservice to handle translating raw source to car object
1. Decompose html source to a dataframe of nodes and meta info.
2. Consume html df into a neural network to predict which node contains the target field
