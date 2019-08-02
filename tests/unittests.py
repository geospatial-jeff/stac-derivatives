import unittest

import numpy as np
from satstac import Item

from derivatives import StacItem

class ItemTestCases(unittest.TestCase):

    def setUp(self):
        self.infile = "https://landsat-stac.s3.amazonaws.com/landsat-8-l1/026/038/2014-10-30/LC80260382014303LGN00.json"
        self.item = StacItem(self.infile)
        self.expected_bands = ['coastal', 'blue', 'green', 'red', 'nir', 'pan', 'lwir11', 'lwir12', 'swir16', 'swir22']

    def test_load_item(self):
        input1 = self.infile
        input2 = Item.open(self.infile)
        input3 = input2.data
        self.assertTrue(type(StacItem.load_item(input1)) == type(StacItem.load_item(input2)) == type(StacItem.load_item(input3)) == Item)

    def test_load_bands(self):
        for b in self.expected_bands:
            self.assertTrue(hasattr(self.item.bands, b))
        self.assertEqual(self.item.bandlist.sort(), self.expected_bands.sort())

    def test_read_band(self):
        green_band, profile = self.item.read_band('green')
        self.assertTrue(type(green_band) == np.ndarray)
        self.assertTupleEqual(green_band.shape, (profile['count'], profile['height'], profile['width']))