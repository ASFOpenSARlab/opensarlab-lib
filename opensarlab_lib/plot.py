from pathlib import Path
from typing import List, Optional, Union, Tuple

import cartopy.crs
import cartopy.feature as cfeature
import pyproj
import shapefile  # Requires the pyshp package
from shapely.geometry import shape
from shapely.ops import transform

import matplotlib.pyplot as plt
import matplotlib.patches as patches
plt.rcParams.update({'font.size': 12})

def plot_shape_in_stack(
    shapefile_path: Union[Path, str], 
    src_crs: str, 
    max_extents: List[Union[float, int]], 
    common_extents: List[Union[float, int]], 
    figsize:Optional[Tuple[int]]=None):
    
    """
    Generates a basemap plot showing the maximum and common geographic extents covered by a data stack of geotiffs, and the location of a simple Polygon within
    those extents (loaded from a shapefile).
    
    Args:
        shapefile_path: the posix or string path to a shapefile conaining a single, simple Polygon in the same projection as your data stack
        src_crs:        The string EPSG of the data stack
        extents:        web mercator (EPSG: 3857) max raster extents of entire stack [xmin, ymin, xmax, ymax]
                            (guaranteed to contain data in at least one raster)
        common_extents: web mercator (EPSG: 3857) raster extents common to entire stack [xmin, ymin, xmax, ymax]
                            (guaranteed to contain data in all rasters)
        figsize: a tuple containing the figure size of the output plot in the format (x_size, y_size)     
    """
    
    fig = plt.figure(figsize=figsize)
    ax = fig.add_subplot(1,1,1, projection=cartopy.crs.Mercator())
    ax.stock_img()
    ax.add_feature(cfeature.BORDERS)
    ax.add_feature(cfeature.COASTLINE)

    x_padding = (max_extents[2] - max_extents[0]) / 10
    y_padding = (max_extents[3] - max_extents[1]) / 10

    ax.set_extent(
        [
            max_extents[0]-x_padding, # minimum latitude
            max_extents[2]+x_padding, # max latitude
            max_extents[1]-y_padding, # min longitude
            max_extents[3]+y_padding # max longitude
        ],
        crs=cartopy.crs.Mercator()
    )

    stack_extents = ax.add_patch(patches.Rectangle(
        (max_extents[0], max_extents[3]),
        max_extents[2] - max_extents[0],
        max_extents[1] - max_extents[3],
        fill=False, edgecolor='orange', 
        label='Max area covered by data stack'))

    extent_handles = [stack_extents]


    stack_common_extents = ax.add_patch(patches.Rectangle(
        (common_extents[0], common_extents[3]),
        common_extents[2] - common_extents[0], 
        common_extents[1] - common_extents[3], 
        fill=False, edgecolor='green', 
        label='Common area covered by data stack')) 

    extent_handles.append(stack_common_extents)

    sf = shapefile.Reader(shapefile_path)
    feature = sf.shapeRecords()[0]
    polygon = shape(feature.shape.__geo_interface__)

    utm_crs = pyproj.CRS(f'EPSG:{src_crs}')
    web_crs = pyproj.CRS('EPSG:3857')

    project = pyproj.Transformer.from_crs(utm_crs, web_crs, always_xy=True).transform
    web_sf = transform(project, polygon)

    x, y = web_sf.exterior.coords.xy

    shapefile_extents = ax.add_patch(patches.Polygon(list(zip(x,y)), 
                                                  fill=False, edgecolor='red',
                                                  label='Shapefile extents'))

    extent_handles.append(shapefile_extents)

    ax.legend(handles=extent_handles)

    gl = ax.gridlines(crs=cartopy.crs.PlateCarree(), draw_labels=True,
              linewidth=2, color='gray', alpha=0.5, linestyle='--')

    plt.show()