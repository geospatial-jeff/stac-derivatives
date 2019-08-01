import boto3
import rasterio
from rasterio.io import MemoryFile

s3  = boto3.client('s3')


class Outputs(object):

    def __init__(self, arr, profile):
        self.arr = arr
        self.profile = profile

    def to_array(self):
        return self.arr

    def to_gtiff(self, outfile):
        print(self.profile)
        with rasterio.open(outfile, 'w', **self.profile) as dst:
            dst.write(self.arr)

    def to_s3(self, bucket, key):
        #https://github.com/mapbox/rasterio/issues/899#issuecomment-253133665
        memfile = MemoryFile()
        with memfile.open(**self.profile) as gtiff:
            gtiff.write(self.arr)
        s3.put_object(Bucket=bucket, Key=key, Body=memfile)