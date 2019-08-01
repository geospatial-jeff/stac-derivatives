
# https://github.com/radiantearth/stac-spec/tree/master/extensions/eo#common-band-names
BAND_NAMES = [
    "coastal",
    "blue",
    "green",
    "red",
    "pan",
    "nir",
    "cirrus",
    "swir16",
    "swir22",
    "lwir12",
    "lwir22"
]

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
        # Load assets
        for asset in self.item['assets']:
            try:
                band_name = self.item['assets'][asset]['common_name']
                if band_name in BAND_NAMES:
                    setattr(self, band_name, self.item['assets'][asset])
            except KeyError:
                pass

    @requirements(["red", "nir"])
    def ndvi(self):
        print("inside ndvi")