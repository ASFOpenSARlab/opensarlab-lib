from pathlib import Path
import re
import subprocess
from typing import List, Union

import numpy as np
from osgeo import gdal

from .custom_exceptions import VRTError, UnexpectedFileExtension


def vrt_to_gtiff(vrt: Union[Path, str], output: Union[Path, str]):
    """
    Takes: a string or posix path to an input VRT and a string or posix path to an output tif

    If a file extension is not included in `output`, 'tif' will be used

    Creates a geotiff (output) from the vrt
    """
    vrt = str(vrt)
    output = str(output)

    try:
        driver = gdal.Info(vrt, format='json')['driverShortName']
    except TypeError:
        raise FileNotFoundError
    except KeyError:
        raise KeyError("'driverShortName' not found in image metadata")
    if driver != 'VRT':
        raise VRTError(f"gdal recognized {vrt} as a {driver} file, not a VRT.")
    if '.' not in output:
        output = f"{output}.tif"
    elif len(output) > 4 and (output[:-3] == 'tif' or output[:-4] == 'tiff'):
        raise UnexpectedFileExtension(f"'tif' or 'tiff' not recognized as the file extension for {output}")

    cmd = f"gdal_translate -co \"COMPRESS=DEFLATE\" -a_nodata 0 {vrt} {output}"
    sub = subprocess.run(cmd, stderr=subprocess.PIPE, shell=True)
    print(str(sub.stderr)[2: -3])


def get_projection(img_path: Union[Path, str]) -> Union[str, None]:
    """
    Takes: a string or posix path to a product in a UTM projection

    Returns: the projection (as a string) or None if none found
    """
    img_path = str(img_path)
    try:
        info = gdal.Info(img_path, format='json')['coordinateSystem']['wkt']
    except KeyError:
        return None
    except TypeError:
        raise FileNotFoundError

    regex = 'ID\["EPSG",[0-9]{4,5}\]\]$'
    results = re.search(regex, info)
    if results:
        return results.group(0).split(',')[1][:-2]
    else:
        return None


def get_corner_coords(img_path: Union[Path, str]) -> Union[List[str], None]:
    """
    Takes: a string or posix path to geographic dataset

    Returns: a list whose 1st element are the upperLeft coords and
             whose 2nd element are the lowerRight coords or None
             if none found
    """
    img_path = str(img_path)
    try:
        info = gdal.Info(img_path, options=['-json'])
    except TypeError:
        raise FileNotFoundError
    try:
        return [info['cornerCoordinates']['upperLeft'], info['cornerCoordinates']['lowerRight']]
    except KeyError:
        return None


def remove_nan_filled_tifs(tifs: List[Union[Path, str]]):
    """
    Takes: a list of string or posix paths to the tifs

    Deletes any tifs containing only NaN values.
    """
    tifs = [Path(t) for t in tifs]
    removed = 0
    for tif in tifs:
        try:
            raster = gdal.Open(str(tif))
        except TypeError:
            raise FileNotFoundError

        band = raster.ReadAsArray()
        if np.count_nonzero(band) < 1:
            tif.unlink()
            removed += 1
    print(f"GeoTiffs Examined: {len(tifs)}")
    print(f"GeoTiffs Removed:  {removed}")
