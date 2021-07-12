import os
import zipfile

import matplotlib.pyplot as plt
import numpy as np
from osgeo import gdal


def path_exists(path: str) -> bool:
    """
    Takes a string path, returns true if exists or
    prints error message and returns false if it doesn't.
    """
    assert type(path) == str, 'Error: path must be a string'

    if os.path.exists(path):
        return True
    else:
        print(f"Invalid Path: {path}")
        return False


def new_directory(path: str):
    """
    Takes a path for a new or existing directory. Creates directory
    and sub-directories if not already present.
    """
    assert type(path) == str

    if os.path.exists(path):
        print(f"{path} already exists.")
    else:
        os.makedirs(path)
        print(f"Created: {path}")
    if not os.path.exists(path):
        print(f"Failed to create path!")


def asf_unzip(output_dir: str, file_path: str):
    """
    Takes an output directory path and a file path to a zipped archive.
    If file is a valid zip, it extracts all to the output directory.
    """
    ext = os.path.splitext(file_path)[1]
    assert type(output_dir) == str, 'Error: output_dir must be a string'
    assert type(file_path) == str, 'Error: file_path must be a string'
    assert ext == '.zip', 'Error: file_path must be the path of a zip'

    if path_exists(output_dir):
        if path_exists(file_path):
            print(f"Extracting: {file_path}")
            try:
                zipfile.ZipFile(file_path).extractall(output_dir)
            except zipfile.BadZipFile:
                print(f"Zipfile Error.")
            return


def get_power_set(my_set, set_size=None):
    """
    my_set: list or set of strings
    set_size: deprecated, kept as optional for backwards compatibility
    returns: the power set of input strings
    """
    p_set = set()
    if len(my_set) > 1:
        pow_set_size = 1 << len(my_set) # 2^n
        for counter in range(0, pow_set_size):
            temp = ""
            for j in range(0, len(my_set)):
                if(counter & (1 << j) > 0):
                    if temp != "":
                        temp = f"{temp} and {my_set[j]}"
                    else:
                        temp = my_set[j]
                if temp != "":
                    p_set.add(temp)
    else:
        p_set = set(my_set)
    return p_set


def remove_nan_filled_tifs(tif_dir: str, file_names: list):
    """
    Takes a path to a directory containing tifs and
    and a list of the tif filenames.
    Deletes any tifs containing only NaN values.
    """
    assert type(tif_dir) == str, 'Error: tif_dir must be a string'
    assert len(file_names) > 0, 'Error: file_names must contain at least 1 file name'

    removed = 0
    for tiff in file_names:
        raster = gdal.Open(f"{tif_dir}{tiff}")
        if raster:
            band = raster.ReadAsArray()
            if np.count_nonzero(band) < 1:
                os.remove(f"{tif_dir}{tiff}")
                removed += 1
    print(f"GeoTiffs Examined: {len(file_names)}")
    print(f"GeoTiffs Removed:  {removed}")


def input_path(prompt):
    print(f"Current working directory: {os.getcwd()}")
    print(prompt)
    return input()


def handle_old_data(data_dir, contents):
    print(f"\n********************** WARNING! **********************")
    print(f"The directory {data_dir} already exists and contains:")
    for item in contents:
        print(f"• {item.split('/')[-1]}")
    print(f"\n\n[1] Delete old data and continue.")
    print(f"[2] Save old data and add the data from this analysis to it.")
    print(f"[3] Save old data and pick a different subdirectory name.")
    while True:
        try:
            selection = int(input("Select option 1, 2, or 3.\n"))
        except ValueError:
             continue
        if selection < 1 or selection > 3:
             continue
        return selection


#########################
#  OpenSARlab Functions #
#########################


def jupytertheme_matplotlib_format() -> bool:
    """
    If recognised jupytertheme dark mode is being used,
    reformat matplotlib settings for improved dark mode visibility.
    Return True if matplotlib settings adjusted or False if not
    """
    try:
        from jupyterthemes import jtplot
        print(f"jupytertheme style: {jtplot.infer_theme()}")
        if jtplot.infer_theme() in ('osl_dark', 'onedork'):
            plt.rcParams.update({'hatch.color': 'white'})
            plt.rcParams.update({'axes.facecolor': 'lightgrey'})
            plt.rcParams.update({'axes.labelcolor': 'white'})
            plt.rcParams.update({'xtick.color': 'lightgrey'})
            plt.rcParams.update({'ytick.color': 'lightgrey'})
            return True
    except ModuleNotFoundError:
        print("jupytertheme not installed")
        pass
    return False
