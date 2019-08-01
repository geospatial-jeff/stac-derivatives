import numpy as np
import rasterio

# https://github.com/radiantearth/stac-spec/tree/master/extensions/eo#common-band-names
BAND_NAMES = [
    "coastal",
    "blue",
    "green",
    "red",
    "redge",
    "pan",
    "nir",
    "cirrus",
    "swir16",
    "swir22",
    "lwir12",
    "lwir22"
]

# TODO: Fix np.seterr, it isn't working propertly for some reason
# np.seterr(divide='ignore', invalid='ignore')


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
        return wrapped_f
    return wrapper

class StacItem(object):

    def __init__(self, item):
        self.item = item
        self.load_bands()

    def load_bands(self):
        for asset in self.item['assets']:
            try:
                band_name = self.item['assets'][asset]['common_name']
                if band_name in BAND_NAMES:
                    setattr(self, band_name, self.item['assets'][asset])
            except KeyError:
                pass

    def read_band(self, band, profile=False):
        with rasterio.open(getattr(self, band)['href']) as src:
            if profile:
                return [src.read(1).astype(float), profile]
            return src.read(1).astype(float)

    @requirements(["red", "nir"])
    def ndvi(self):
        red, profile = self.read_band('red', profile=True)
        nir = self.read_band('nir')
        num = nir - red
        den = (nir + red) + 0.00000000001
        ndvi = np.divide(num, den)
        return ndvi

    @requirements(["redge", "nir"])
    def ndre(self):
        redge, profile = self.read_band('rededge', profile=True)
        nir = self.read_band('nir')
        num = nir - redge
        den = (nir + redge) + 0.00000000001
        ndre = np.divide(num, den)
        return ndre
