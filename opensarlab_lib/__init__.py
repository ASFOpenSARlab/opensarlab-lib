"""
A Python library to support ASF OpenSARlab's Jupyter Notebook repository
https://github.com/ASFOpenSARlab/opensarlab-notebooks
"""

from importlib.metadata import PackageNotFoundError, version

from .config import TESTING
from .aoi import AOI_Selector
from .edl import EarthdataLogin

try:
    __version__ = version(__name__)
except PackageNotFoundError:
    print('package is not installed!\n'
          'Install in editable/develop mode via (from the top of this repo):\n'
          '   python -m pip install -e .\n'
          'Or, to just get the version number use:\n'
          '   python setup.py --version')

__all__ = [
    'AOI_Selector',
    'EarthdataLogin',
    '__version__',
]
