import re
import os
import glob

def date_from_product_name(product_name: str) -> str:
    regex = "\w[0-9]{7}T[0-9]{6}"
    results = re.search(regex, product_name)
    if results:
        return results.group(0)
    else:
        return None

def get_products_dates(products_info: list) -> list:
    dates = list()
    for info in products_info:
        date_regex = "\w[0-9]{7}T[0-9]{6}"
        date_strs = re.findall(date_regex, info['granule'])
        if date_strs:
            for d in date_strs:
                dates.append(d[0:8])
    dates.sort()
    dates = list(set(dates))
    return dates

def get_polarity_from_path(path: str) -> str:
    """
    Takes a path to a HyP3 product containing its polarity in its filename
    Returns the polarity string or none if not found
    """
    path = os.path.basename(path)
    regex = "(v|V|h|H){2}"
    return re.search(regex, path).group(0)


def get_RTC_polarizations(base_path: str) -> list:
    """
    Takes a string path to a directory containing RTC product directories
    Returns a list of present polarizations
    """
    assert type(base_path) == str, 'Error: base_path must be a string.'
    assert os.path.exists(base_path), f"Error: select_RTC_polarization was passed an invalid base_path, {base_path}"
    paths = []
    pths = glob.glob(f"{base_path}/*/*.tif")
    if len(pths) > 0:
        for p in pths:
            filename = os.path.basename(p)
            polar_fname = re.search("^\w[\--~]{5,300}(_|-)(vv|VV|vh|VH|hh|HH|hv|HV).(tif|tiff)$", filename)
            if polar_fname:
                paths.append(polar_fname.string.split('.')[0][-2:])
    if len(paths) > 0:
        return list(set(paths))
    else:
        print(f"Error: found no available polarizations.")