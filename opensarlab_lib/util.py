import contextlib
import os
from pathlib import Path
import zipfile
from typing import List, Set, Union

import matplotlib.pyplot as plt


@contextlib.contextmanager
def work_dir(work_pth: Union[Path, str]):
    """
    Temporarily change directories, within the scope of a with statement.
    Useful when invoking scripts that only input files from the current working directory.

    Usage:
    with work_dir(work_pth):
        do_things()
    """
    cwd = Path.cwd()
    os.chdir(work_pth)
    try:
        yield
    finally:
        os.chdir(cwd)


def asf_unzip(output_dir: Union[Path, str], file_path: Union[Path, str]):
    """
    Takes: an output directory path and a file path to a zipped archive.
    If file is a valid zip, it extracts all to the output directory.
    """
    output_dir = Path(output_dir)
    file_path = Path(file_path)
    assert zipfile.is_zipfile(file_path)

    if output_dir.is_dir():
        if file_path.exists():
            print(f"Extracting: {str(file_path)}")
            try:
                zipfile.ZipFile(file_path).extractall(output_dir)
            except zipfile.BadZipFile:
                print(f"Zipfile Error.")
            return


def get_power_set(my_set: Union[List, Set]) -> Set[str]:
    """
    Takes: list or set of objects
    returns: the power set of of objects in my_set as strings
    """
    p_set = set()
    if len(my_set) > 1:
        pow_set_size = 1 << len(my_set)  # 2^n
        for i in range(0, pow_set_size):
            temp = ""
            for j in range(0, len(my_set)):
                if i & (1 << j) > 0:
                    if temp != "":
                        temp = f"{temp} and {my_set[j]}"
                    else:
                        temp = str(my_set[j])
                if temp != "":
                    p_set.add(temp)
    else:
        p_set = set(my_set)
    return p_set


def handle_old_data(data_dir: Union[Path, str]) -> Union[int, None]:
    """
    Takes: path to a directory
    Checks if directory exists and contains files
    Inputs user selection for handling any files found
    Returns: Integer selection for handling existing files
    """
    data_dir = Path(data_dir)
    if data_dir.is_dir():
        print(f"\n********************** WARNING! **********************")
        print(f"The directory {data_dir} already exists and contains:")
        contents = data_dir.glob('*')
        for item in contents:
            print(f"• {str(item).split('/')[-1]}")
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
        print("jupyterthemes not installed")
        pass
    return False
