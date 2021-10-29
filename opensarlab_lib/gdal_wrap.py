import json
import re
import subprocess

from osgeo import gdal


def vrt_to_gtiff(vrt: str, output: str):
    if '.vrt' not in vrt:
        print('Error: The path to your vrt does not contain a ".vrt" extension.')
        return
    if '.' not in output:
        output = f"{output}.tif"
    elif len(output) > 4 and (output[:-3] == 'tif' or output[:-4] == 'tiff'):
        print('Error: the output argument must either not contain a ' /
              'file extension, or have a "tif" or "tiff" file extension.')
        return

    cmd = f"gdal_translate -co \"COMPRESS=DEFLATE\" -a_nodata 0 {vrt} {output}"
    sub = subprocess.run(cmd, stderr=subprocess.PIPE, shell=True)
    print(str(sub.stderr)[2: -3])


def get_utm(img_path):
    info = (gdal.Info(img_path, options=['-json']))
    info = json.dumps(info)
    info = (json.loads(info))['coordinateSystem']['wkt']
    regex = 'ID\["EPSG",[0-9]{4,5}\]\]$'
    results = re.search(regex, info)
    if results:
        return results.group(0).split(',')[1][:-2]
    else:
        return None

def get_corner_coords(img_path):
    info = (gdal.Info(img_path, options=['-json']))
    return [info['cornerCoordinates']['upperLeft'], info['cornerCoordinates']['lowerRight']]
