from flask import Flask, request
from json import loads as read_json
from json import dumps as to_json

from car.src.marketplaces import donedeal

command = Flask(__name__)

@command.route("/command/<market>")
def examine_market(market):
    return to_json(list(market))



@command.route("/command/<market>/load/")
def initialise(marketplace):
    n = request.args.get('make', default=marketplace.n_page, type=int)
    pages = n/marketplace.n_page
    marketplace.initialise(pages)

