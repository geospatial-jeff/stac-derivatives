import numpy as np

from derivatives.item import StacItem
from derivatives.utils import get_methods
from derivatives.outputs import Outputs


class BandError(Exception):
    pass

def requirements(bands):
    def wrapper(f):
        def wrapped_f(self):
            for band in bands:
                if not hasattr(self, band):
                    raise BandError("STAC Item {} is missing the '{}' band which is required for {} ({})".format(
                        self.item['id'],
                        band,
                        f.__name__,
                        bands
                    ))
            return f(self)
        wrapped_f.bands = bands
        return wrapped_f
    return wrapper

class StacIndices(StacItem):

    def __init__(self, item):
        super().__init__(item)

    def derivatives(self):
        valids = []
        methods = [x for x in get_methods(self) if x not in self.base_methods]
        for method in methods:
            band_reqs = getattr(getattr(self, method), 'bands')
            if set(band_reqs).issubset(set(self.bandlist)):
                valids.append(method)
        return valids

    @requirements(["red", "nir"])
    def ndvi(self):
        red, profile = self.read_band('red', profile=True)
        profile['dtype'] = 'float32'
        nir = self.read_band('nir')
        num = nir - red
        den = (nir + red) + 0.00000000001
        ndvi = np.divide(num, den)
        return Outputs(ndvi, profile)

    @requirements(["redge", "nir"])
    def ndre(self):
        redge, profile = self.read_band('rededge', profile=True)
        profile['dtype'] = 'float32'
        nir = self.read_band('nir')
        num = nir - redge
        den = (nir + redge) + 0.00000000001
        ndre = np.divide(num, den)
        return Outputs(ndre, profile)