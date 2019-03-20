
class Routers(object):
    def __init__(self):

        donedeal_router = lambda make, model, sort: self.donedeal(make, model, sort)
        PistonHeads_router = lambda make, model, sort: self.PistonHeads(make, model, sort)
        self._donedeal_router = donedeal_router
        self._pistonheads_router = PistonHeads_router

        return

    def donedeal(self, make, model, sort='publishdate%20desc'):
        """return donedeal  url with specific make model and """
        if make and model is not None:
            base = "https://www.donedeal.co.uk/cars/" + make + "/" + model + "?sort=" + sort
        elif make is not None and model is None:
            base = "https://www.donedeal.co.uk/cars/" + make + "?sort="+sort
        else:
            base = "https://www.donedeal.co.uk/cars?sort="+sort
        return base

    def PistonHeads(self, make, model, sort):
        return "https://www.pistonheads.com/classifieds?Category=used-cars&SortOptions="+sort

    def __getitem__(self, item):
        return getattr(self, item)


routes = Routers()
