import rasterio
from satstac import Item, Collection
from urllib.parse import urljoin


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

    base_methods = ["__init__", "eobands", "load_bands", "read_band"]

    def __init__(self, item):
        self.item = item
        self.bands = self.load_bands()

    def eobands(self):
        try:
            return self.item['properties']['eo:bands']
        except KeyError:
            # eo:bands is often stored at collection level (commons)
            item = Item(self.item)
            col_link = item.links('collection')[0]
            if '..' in col_link:
                col = Collection.open(urljoin(item.links('self')[0], col_link))
            else:
                col = Collection.open(col_link)
            return col.properties['eo:bands']

    def read_band(self, band, profile=False):
        band = getattr(self.bands, band)
        with rasterio.open(band.href) as src:
            if band.bandcount == 1:
                arr = src.read()
            else:
                arr = src.read(band.bidx)
            if profile:
                return [arr, src.profile]
            else:
                return arr
            # if profile:
            #     return [src.read().astype('float32'), src.profile]
            # return src.read().astype('float32')

    def load_bands(self):
        bands = self.eobands()
        band_list = [x['common_name'] for x in bands if 'common_name' in x]
        band_stack = BandStack()
        # Using eo:bands to look up band information about each asset
        for asset in self.item['assets']:
            try:
                band_indices = self.item['assets'][asset]['eo:bands']
                for i, idx in enumerate(band_indices):
                    band = Band(bands[idx], self.item['assets'][asset], i+1, len(band_indices))
                    if band.common_name in BAND_NAMES:
                        setattr(band_stack, band.common_name, band)
            except:
                pass

        self.bandlist = band_list
        return band_stack

class BandStack(object):
    pass

class Band(object):

    def __init__(self, band, asset, bidx, bandcount):
        self.name = band['name']
        self.common_name = band['common_name']
        self.href = asset['href']
        self.bidx = bidx
        self.bandcount = bandcount
        self.__array = None

    @property
    def array(self):
        return self.__array

    @array.setter
    def array(self, arr):
        # Used for caching the array when calculating multiple indices within a single instance
        self.__array = arr

