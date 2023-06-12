from typing import List, Optional, Union, Tuple

import matplotlib
import matplotlib.pyplot as plt
from matplotlib.widgets import RectangleSelector
import matplotlib.patches as patches

import cartopy.crs
import cartopy.feature as cfeature
import numpy as np

plt.rcParams.update({'font.size': 12})


########################
#  Subset AOI Selector #
########################

class AOI_Selector:
    """
    Creates an interactive matplotlib plot allowing users
    to select an area-of-interest with a bounding box
    """

    def __init__(self, extents: List[Union[float, int]],
                 common_extents: Optional[List[Union[float, int]]] = None,
                 figsize: Optional[Tuple[int]]=(10,8)):
        """
        Args:
            extents:        web mercator (EPSG: 3857) max raster extents of entire stack [xmin, ymin, xmax, ymax]
                            (guaranteed to contain data in at least one raster)
            common_extents: web mercator (EPSG: 3857) raster extents common to entire stack [xmin, ymin, xmax, ymax]
                            (guaranteed to contain data in all rasters)
            figsize: a tuple containing the figure size of the output plot in the format (x_size, y_size)
            
        """
        
        self.x1 = None
        self.y1 = None
        self.x2 = None
        self.y2 = None
        self.extents = extents
        self.common_extents = common_extents
        self.fig = plt.figure(figsize=figsize)     
        self.ax = self.fig.add_subplot(1,1,1, projection=cartopy.crs.Mercator())
        self.ax.stock_img()
        self.ax.add_feature(cfeature.BORDERS)
        self.ax.add_feature(cfeature.COASTLINE)
        
        x_padding = (self.extents[2] - self.extents[0]) / 10
        y_padding = (self.extents[3] - self.extents[1]) / 10
        
        self.ax.set_extent(
            [
                self.extents[0]-x_padding, # minimum latitude
                self.extents[2]+x_padding, # max latitude
                self.extents[1]-y_padding, # min longitude
                self.extents[3]+y_padding # max longitude
            ],
            crs=cartopy.crs.Mercator()
        )
        
        gl = self.ax.gridlines(crs=cartopy.crs.PlateCarree(), draw_labels=True,
                  linewidth=2, color='gray', alpha=0.5, linestyle='--')
        
        stack_extents = self.ax.add_patch(patches.Rectangle((self.extents[0], self.extents[3]),
                                                         self.extents[2] - self.extents[0], self.extents[1] - self.extents[3],
                                                         fill=False, edgecolor='orange', 
                                                         label='Max area covered by data stack'))
        extent_handles = [stack_extents]
        
        if self.common_extents:
            stack_common_extents = self.ax.add_patch(patches.Rectangle((self.common_extents[0], self.common_extents[3]),
                                                             self.common_extents[2] - self.common_extents[0], 
                                                             self.common_extents[1] - self.common_extents[3], 
                                                             fill=False, edgecolor='green', 
                                                             label='Common area covered by data stack')) 
            extent_handles.append(stack_common_extents)
        
        self.ax.legend(handles=extent_handles)
            
        self.fig.suptitle('Area-Of-Interest Selector', fontsize=16)
        plt.show()

        def toggle_selector(event: matplotlib.backend_bases.Event):
            """
            Takes: a key press event

            Toggles the selector off if the Pan or Zoom tools are selected.
            Toggles the selector on if the Pan and Zoom tools are deselected.
            """
            if event.key in ['Q', 'q'] and toggle_selector.RS.active:
                toggle_selector.RS.set_active(False)
            if event.key in ['A', 'a'] and not toggle_selector.RS.active:
                toggle_selector.RS.set_active(True)

        toggle_selector.RS = RectangleSelector(self.ax, self.line_select_callback,
                                               useblit=True,
                                               button=[1, 3],  # don't use middle button
                                               minspanx=0, minspany=0,
                                               spancoords='pixels',
                                               props=dict(facecolor='red', edgecolor='yellow',
                                                              alpha=0.3, fill=True),
                                               interactive=True)
        plt.connect('key_press_event', toggle_selector)

    def line_select_callback(self,
                             eclick: matplotlib.backend_bases.Event,
                             erelease: matplotlib.backend_bases.Event):
        """
        Takes: An eclick and erelease event

        Sets self.x1, self.x2, self.y1, and self.y2 from selection corner coordinates
        """

        self.x1, self.y1 = eclick.xdata, eclick.ydata
        self.x2, self.y2 = erelease.xdata, erelease.ydata

##################
#  Line Selector #
##################

class LineSelector:
    """
    Creates an interactive matplotlib plot allowing users
    to define a line by selecting 2 points
    """

    def __init__(self, image: np.ndarray,
                 figsize: Optional[Tuple[int]]=(10,8),
                 cmap: Optional[matplotlib.colors.LinearSegmentedColormap] = plt.cm.gist_gray,
                 vmin: Optional[Union[float, int]] = None,
                 vmax: Optional[Union[float, int]] = None
                 ):
        self.x1 = None
        self.x2 = None
        self.y1 = None
        self.y2 = None

        self.pnt1 = None
        self.pnt2 = None

        self.fig = plt.figure(figsize=figsize)
        self.ax = self.fig.add_subplot(111, visible=False)
        self.rect = patches.Rectangle(
            (0.0, 0.0), figsize[0], figsize[1],
            fill=False, clip_on=False, visible=False)
        
        self.rect_patch = self.ax.add_patch(self.rect)
        self.cid = self.rect_patch.figure.canvas.mpl_connect('button_press_event',
                                                             self)
        self.cmap = cmap
        self.image = image
        self.plot = self.gray_plot(self.fig, vmin=vmin, vmax=vmax, return_ax=True)
        self.plot.set_title('Select 2 Points of Interest')

    def gray_plot(self,
                  fig: matplotlib.figure.Figure,
                  vmin: Optional[Union[float, int]] = None,
                  vmax: Optional[Union[float, int]] = None,
                  return_ax: Optional[bool] = False):
        """
        Takes: a matplotlib.figure.Figure object and optional vmin and vmax

        Calculates reasonable vmin, vmax if not passed

        Returns: axes if return_ax == True
        """
        if vmin is None:
            vmin = np.nanpercentile(self.image, 1)
        if vmax is None:
            vmax = np.nanpercentile(self.image, 99)
        ax = fig.add_axes([0.1, 0.1, 0.8, 0.8])
        ax.imshow(self.image, cmap=self.cmap, vmin=vmin, vmax=vmax)
        if return_ax:
            return (ax)

    def __call__(self, event: matplotlib.backend_bases.Event):
        """
        Takes: a click event

        Maintains a stack of 2 points and one line:
        Adding a new point deletes the line and oldest point, and
        creates a new line between the new point and the remaining old point.
        """

        self.x1 = event.xdata
        self.y1 = event.ydata

        if len(self.plot.get_lines()) == 3:
            self.plot.get_lines()[2].remove()

        plt.plot(self.x1, self.y1, 'ro')

        for i, pnt in enumerate(self.plot.get_lines()):
            if len(self.plot.get_lines()) == 3 and i == 0:
                pnt.remove()

        self.line_x = [pnt.get_xdata() for pnt in self.plot.get_lines()]
        self.line_y = [pnt.get_ydata() for pnt in self.plot.get_lines()]
        if len(self.plot.get_lines()) > 1:
            plt.plot(self.line_x, self.line_y)

        for i, pnt in enumerate(self.plot.get_lines()):
            if i == 0:
                self.pnt1 = pnt.get_xydata()
            elif i == 1:
                self.pnt2 = pnt.get_xydata()
