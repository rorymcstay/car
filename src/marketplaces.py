from market import market

DoneDeal = market(url_stub_1="https://www.donedeal.co.uk/cars?sort=publishdate%20desc",
                  url_stub_2="&sort=publishdate%20desc",
                  result_stub="https://www.donedeal.co.uk/cars-for-sale/",
                  wait_for="searchResultsPanel",
                  wait_for_car="js-featured-block",
                  n_page=28,
                  json_identifier='window.adDetails',
                  mapping="DoneDeal")
