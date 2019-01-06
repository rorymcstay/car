
class Routers(object):
    def __init__(self):

        DoneDeal_router = lambda make, model, sort: self.DoneDeal(make, model, sort)
        PistonHeads_router = lambda make, model, sort: self.PistonHeads(make, model, sort)
        self._DoneDeal_router = DoneDeal_router
        self._PistonHeads_router = PistonHeads_router

        return

    def DoneDeal(self, make, model, sort):
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


