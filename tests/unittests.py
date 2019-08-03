import os
import shutil
import tempfile
import unittest


import numpy as np
from satstac import Item
import rasterio

from derivatives import StacItem, StacIndices

class ItemTestCases(unittest.TestCase):

    def setUp(self):
        self.infile = "https://landsat-stac.s3.amazonaws.com/landsat-8-l1/026/038/2014-10-30/LC80260382014303LGN00.json"
        self.item = StacItem(self.infile)
        self.expected_bands = ['coastal', 'blue', 'green', 'red', 'nir', 'pan', 'lwir11', 'lwir12', 'swir16', 'swir22', 'cirrus']

    def test_load_item(self):
        input1 = self.infile
        input2 = Item.open(self.infile)
        input3 = input2.data
        self.assertTrue(type(StacItem.load_item(input1)) == type(StacItem.load_item(input2)) == type(StacItem.load_item(input3)) == Item)

    def test_load_bands(self):
        for b in self.expected_bands:
            self.assertTrue(hasattr(self.item.bands, b))
        self.assertEqual(sorted(self.item.bandlist), sorted(self.expected_bands))

    def test_read_band(self):
        green_band, profile = self.item.read_band('green', profile=True)
        self.assertTrue(type(green_band) == np.ndarray)
        self.assertTupleEqual(green_band.shape, (profile['count'], profile['height'], profile['width']))

class IndicesTestCases(unittest.TestCase):

    def setUp(self):
        self.infile = "https://landsat-stac.s3.amazonaws.com/landsat-8-l1/026/038/2014-10-30/LC80260382014303LGN00.json"
        self.item = StacIndices(self.infile)

    def test_derivatives(self):
        expected = ["ndvi"]
        self.assertListEqual(sorted(self.item.derivatives()), sorted(expected))

    def test_ndvi(self):
        ndvi = self.item.ndvi().to_array()
        self.assertGreaterEqual(np.min(ndvi), -1)
        self.assertLessEqual(np.max(ndvi), 1)

class OutputsTestCases(unittest.TestCase):

    def setUp(self):
        self.infile = "https://landsat-stac.s3.amazonaws.com/landsat-8-l1/026/038/2014-10-30/LC80260382014303LGN00.json"
        self.item = StacIndices(self.infile)
        self.ndvi = self.item.ndvi()

    def test_to_array(self):
        arr = self.ndvi.to_array()
        self.assertEqual(type(arr), np.ndarray)

    def test_to_gtiff(self):
        tempdir = tempfile.mkdtemp()
        fname = os.path.join(tempdir, 'test_to_gtiff.tif')
        self.ndvi.to_gtiff(fname)
        with rasterio.open(fname) as src:
            self.assertEqual(src.profile['driver'], 'GTiff')
            self.assertEqual(src.profile['crs'].to_epsg(), self.item.item.properties['eo:epsg'])
        shutil.rmtree(tempdir)
