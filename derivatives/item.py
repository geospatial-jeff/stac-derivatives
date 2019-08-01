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
# Current workaround is to add 0.0000001 to the denominators to prevent divide by 0 error.
# np.seterr(divide='ignore', invalid='ignore')

class StacItem(object):

    base_methods = ["__init__", "derivatives", "load_bands", "read_band"]

    def __init__(self, item):
        self.item = item
        self.load_bands()

    def load_bands(self):
        bandlist = []
        for asset in self.item['assets']:
            try:
                band_name = self.item['assets'][asset]['common_name']
                if band_name in BAND_NAMES:
                    setattr(self, band_name, self.item['assets'][asset])
                    bandlist.append(band_name)
            except KeyError:
                pass
        self.bandlist = bandlist

    def read_band(self, band, profile=False):
        with rasterio.open(getattr(self, band)['href']) as src:
            if profile:
                return [src.read().astype('float32'), src.profile]
            return src.read().astype('float32')
