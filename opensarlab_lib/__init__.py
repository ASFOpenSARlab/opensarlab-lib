"""
A Python library to support ASF OpenSARlab's Jupyter Notebook repository
https://github.com/ASFOpenSARlab/opensarlab-notebooks
"""

from importlib.metadata import PackageNotFoundError, version

from .config import TESTING
from .custom_exceptions import *
from .selectors import *
from .gdal_wrap import *
from .hyp3_wrap import *
from .util import *
from .widgets import *
from .product_name_parse import *

try:
    __version__ = version(__name__)
except PackageNotFoundError:
    print('package is not installed!\n'
          'Install in editable/develop mode via (from the top of this repo):\n'
          '   python -m pip install -e .\n'
          'Or, to just get the version number use:\n'
          '   python setup.py --version')

__all__ = [
    '__version__',
]
