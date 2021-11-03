import glob
import os
from pathlib import Path
import re
from typing import List, Union


def date_from_product_name(product_name: Union[str, Path]) -> Union[str, None]:
    """
    Takes: a string or posix path to a HyP3 product

    Returns: a string date and timestamp parsed from the name or None if none found
    """
    regex = "\w[0-9]{7}T[0-9]{6}"
    results = re.search(regex, str(product_name))
    if results:
        return results.group(0)
    else:
        return None


def get_polarity_from_path(product_name: Union[str, Path]) -> Union[str, None]:
    """
    Takes: a string or posix path to a HyP3 product containing its polarity in its filename

    Returns: the polarity string or None if none found
    """
    product_name = Path(product_name).name
    regex = "(v|V|h|H){2}"
    results = re.search(regex, product_name)
    if results:
        return results.group(0)
    else:
        return None


def get_RTC_polarizations(dir_path: Union[Path, str]) -> List[str]:
    """
    Takes a string or posix path to a directory containing RTC product directories

    Returns a list of present polarizations
    """
    assert Path(dir_path).is_dir(), f'Error: {str(dir_path)} does not exist'
    dir_path = Path(dir_path)
    paths = []
    pths = list(dir_path.glob('*/*.tif*'))
    for p in pths:
        polar_fname = re.search("^\w[\--~]{5,300}(_|-)(vv|VV|vh|VH|hh|HH|hv|HV).(tif|tiff)$", p.name)
        if polar_fname:
            paths.append(polar_fname.string.split('.')[0][-2:])
    if len(paths) == 0:
        print(f"Error: found no available polarizations.")
    return list(set(paths))
