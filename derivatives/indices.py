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
                        self.item.id,
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
                    else:
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

    @requirements(["red", "nir"])
    def msavi2(self, **kwargs):
        red = kwargs.get('red')
        nir = kwargs.get('nir')
        num = (2 * nir + 1 - np.sqrt((2 * nir + 1)**2 - 8 * (nir - red)))
        msavi2 = np.clip(np.divide(num, 2), -1, 1)
        return Outputs(msavi2, kwargs.get('profile'))

    @requirements(["red", "nir"])
    def avi(self, **kwargs):
        red = kwargs.get('red')
        nir = kwargs.get('nir')
        avi = np.cbrt((nir + 1) * (256 - red) * (nir - red))
        return Outputs(avi, kwargs.get('profile'))

    @requirements(["red", "nir"])
    def savi(self, **kwargs):
        red = kwargs.get('red')
        nir = kwargs.get('nir')
        L = kwargs.get('L') if kwargs.get('L') else 0.5
        num = (nir - red) * (1 + L)
        den = (nir + red + L)
        savi = np.clip(np.divide(num, den), -1, 1)
        return Outputs(savi, kwargs.get('profile'))

    @requirements(["red", "nir"])
    def osavi(self, **kwargs):
        red = kwargs.get('red')
        nir = kwargs.get('nir')
        num = nir - red
        den = nir + red + 0.16
        osavi = np.clip(np.divide(num, den), -1, 1)
        return Outputs(osavi, kwargs.get('profile'))

    @requirements(["nir", "swir16"])
    def ndmi(self, **kwargs):
        # moisture index
        nir = kwargs.get('nir')
        swir = kwargs.get('swir16')
        num = nir - swir
        den = nir + swir + 0.0000001
        ndwi = np.divide(num, den)
        return Outputs(ndwi, kwargs.get('profile'))

    @requirements(["green", "nir"])
    def ndwi(self, **kwargs):
        green = kwargs.get('green')
        nir = kwargs.get('nir')
        num = green - nir
        den = green + nir + 0.0000001
        ndwi = np.divide(num, den)
        return Outputs(ndwi, kwargs.get('profile'))

    @requirements(["nir", "swir16"])
    def ndbi(self, **kwargs):
        nir = kwargs.get('nir')
        swir = kwargs.get('swir16')
        num = swir - nir
        den = swir + nir + 0.0000001
        ndwi = np.divide(num, den)
        return Outputs(ndwi, kwargs.get('profile'))

    @requirements(["red", "nir", "swir16"])
    def bu(self, **kwargs):
        bu = self.ndbi().to_array() - self.ndvi().to_array()
        return Outputs(bu, kwargs.get('profile'))

    @requirements(["blue", "red", "nir", "swir16"])
    def bsi(self, **kwargs):
        blue = kwargs.get('blue')
        red = kwargs.get('red')
        nir = kwargs.get('nir')
        swir = kwargs.get('swir16')
        num = (swir + red) - (nir + blue)
        den = (swir + red) + (nir + blue) + 0.0000001
        bsi = np.divide(num, den)
        return Outputs(bsi, kwargs.get('profile'))

    @requirements(["blue", "green", "red"])
    def si(self, **kwargs):
        blue = kwargs.get('blue')
        green = kwargs.get('green')
        red = kwargs.get('red')
        si = np.cbrt((1 - blue) * (1 - green) * (1 - red))
        return Outputs(si, kwargs.get('profile'))

    @requirements(["green", "swir16"])
    def ndsi(self, **kwargs):
        green = kwargs.get('green')
        swir = kwargs.get('swir16')
        num = green - swir
        den = green + swir + 0.0000001
        ndsi = np.divide(num, den)
        return Outputs(ndsi, kwargs.get('profile'))

    @requirements(["green", "red"])
    def ndgi(self, **kwargs):
        green = kwargs.get('green')
        red = kwargs.get('red')
        num = green - red
        den = green + red + 0.0000001
        ndgi = np.divide(num, den)
        return Outputs(ndgi, kwargs.get('profile'))

    @requirements(["nir", "swir22"])
    def nbri(self, **kwargs):
        nir = kwargs.get('nir')
        swir = kwargs.get('swir22')
        num = nir - swir
        den = nir + swir + 0.0000001
        nbri = np.divide(num, den)
        return Outputs(nbri, kwargs.get('profile'))

    @requirements(["red", "blue"])
    def npcri(self, **kwargs):
        red = kwargs.get('red')
        blue = kwargs.get('blue')
        num = red - blue
        den = red + blue + 0.0000001
        npcri = np.divide(num, den)
        return Outputs(npcri, kwargs.get('profile'))

