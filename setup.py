import os

from setuptools import find_packages, setup

_HERE = os.path.abspath(os.path.dirname(__file__))
with open(os.path.join(_HERE, 'README.md'), 'r') as f:
    long_desc = f.read()

setup(
    name='opensarlab_lib',
    use_scm_version=True,
    setup_requires=['setuptools_scm'],
    description="A Python library to support ASF OpenSARlab's Jupyter Notebook repository https://github.com/ASFOpenSARlab/opensarlab-notebooks",
    long_description=long_desc,
    long_description_content_type='text/markdown',

    url='https://github.com/ASFOpenSARlab/opensarlab-lib',

    author='ASF OpenSARlab Team',
    author_email='uaf-jupyterhub-asf@alaska.edu',

    license='BSD',
    include_package_data=True,

    classifiers=[
        'Intended Audience :: Science/Research',
        'License :: OSI Approved :: BSD License',
        'Natural Language :: English',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.8',
        'Programming Language :: Python :: 3.9',
    ],

    packages=find_packages(),
    python_requires='>=3.8',

    install_requires=[
        'numpy',
        'pyproj',
        'asf_search',
        'hyp3_sdk',
        'IPython',
        'ipywidgets',
        'matplotlib',
        'osgeo',
        'pandas',
        'pytest',
        'pytest-cov',
        'requests',
    ],

    extras_require={
    },
)
