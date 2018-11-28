from flask import Flask, request

operator = Flask(__name__)


@operator.route("/<market>")
def examine_market(market):
    return [market.json_identifier, market.url_stub_1, market.url_stub_2, market.wait_for_car]


@operator.route("/<market>/load/")
def initialise(marketplace):
    n = request.args.get('make', default=marketplace.n_page, type=int)
    pages = n/marketplace.n_page
    marketplace.initialise(pages)
