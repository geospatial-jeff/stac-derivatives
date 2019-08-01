import numpy as np

from derivatives.item import StacItem
from derivatives.utils import get_methods
from derivatives.outputs import Outputs


class BandError(Exception):
    pass

def requirements(bands):
    def wrapper(f):
        def wrapped_f(self):
            args = {}
            for idx, band in enumerate(bands):
                # Make sure STAC Item has all required bands to create the indice
                if not hasattr(self.bands, band):
                    raise BandError("STAC Item {} is missing the '{}' band which is required for {} ({})".format(
                        self.item['id'],
                        band,
                        f.__name__,
                        bands
                    ))
                else:
                    # Read the band and update profile
                    if idx == 0:
                        arr, profile = self.read_band(band, profile=True)
                        profile['dtype'] = 'float32'
                        args.update({band: arr, 'profile': profile})
                    args.update({band: self.read_band(band).astype('float32')})
            return f(self, **args)
        wrapped_f.bands = bands
        return wrapped_f
    return wrapper

class StacIndices(StacItem):

    StacItem.base_methods += ["derivatives"]

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
    def ndvi(self, **kwargs):
        nir = kwargs.get('nir')
        red = kwargs.get('red')
        num = nir - red
        den = (nir + red) + 0.0000001
        ndvi = np.divide(num, den)
        return Outputs(ndvi, kwargs.get('profile'))

    @requirements(["redge", "nir"])
    def ndre(self, **kwargs):
        nir = kwargs.get('nir')
        redge = kwargs.get('redge')
        num = nir - redge
        den = (nir + redge) + 0.0000001
        ndre = np.divide(num, den)
        return Outputs(ndre, kwargs.get('profile'))