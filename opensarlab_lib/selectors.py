import numpy as np
from osgeo import gdal
from pyproj import Transformer

from IPython.display import Markdown, display

import matplotlib.pyplot as plt
from matplotlib.widgets import RectangleSelector
import matplotlib.patches as patches

from opensarlab_lib.gdal_wrap import get_utm

plt.rcParams.update({'font.size': 12})


########################
#  Subset AOI Selector #
########################

class AOI_Selector:
    def __init__(self, image,
                 fig_xsize=None, fig_ysize=None,
                 cmap=plt.cm.gist_gray,
                 vmin=None, vmax=None,
                 drawtype='box'
                 ):
        display(Markdown(f"<text style=color:blue><b>Area of Interest Selector Tips:\n</b></text>"))
        display(Markdown(
            f'<text style=color:blue>- This plot uses "matplotlib notebook", whereas the other plots in this notebook use "matplotlib inline".</text>'))
        display(Markdown(
            f'<text style=color:blue>-  If you run this cell out of sequence and the plot is not interactive, rerun the "%matplotlib notebook" code cell.</text>'))
        display(Markdown(f'<text style=color:blue>- Use the pan tool to pan with the left mouse button.</text>'))
        display(Markdown(f'<text style=color:blue>- Use the pan tool to zoom with the right mouse button.</text>'))
        display(Markdown(
            f'<text style=color:blue>- You can also zoom with a selection box using the zoom to rectangle tool.</text>'))
        display(Markdown(
            f'<text style=color:blue>- To turn off the pan or zoom to rectangle tool so you can select an AOI, click the selected tool button again.</text>'))

        display(Markdown(f'<text style=color:darkred><b>IMPORTANT!</b></text>'))
        display(Markdown(
            f'<text style=color:darkred>- Upon loading the AOI selector, the selection tool is already active.</text>'))
        display(Markdown(
            f'<text style=color:darkred>- Click, drag, and release the left mouse button to select an area.</text>'))
        display(Markdown(
            f'<text style=color:darkred>- The square tool icon in the menu is <b>NOT</b> the selection tool. It is the zoom tool.</text>'))
        display(Markdown(
            f'<text style=color:darkred>- If you select any tool, you must toggle it off before you can select an AOI</text>'))
        self.image = image
        self.x1 = None
        self.y1 = None
        self.x2 = None
        self.y2 = None
        if not vmin:
            self.vmin = np.nanpercentile(self.image, 1)
        else:
            self.vmin = vmin
        if not vmax:
            self.vmax = np.nanpercentile(self.image, 99)
        else:
            self.vmax = vmax
        if fig_xsize and fig_ysize:
            self.fig, self.current_ax = plt.subplots(figsize=(fig_xsize, fig_ysize))
        else:
            self.fig, self.current_ax = plt.subplots()
        self.fig.suptitle('Area-Of-Interest Selector', fontsize=16)
        self.current_ax.imshow(self.image, cmap=cmap, vmin=self.vmin, vmax=self.vmax)

        def toggle_selector(self, event):
            print(' Key pressed.')
            if event.key in ['Q', 'q'] and toggle_selector.RS.active:
                print(' RectangleSelector deactivated.')
                toggle_selector.RS.set_active(False)
            if event.key in ['A', 'a'] and not toggle_selector.RS.active:
                print(' RectangleSelector activated.')
                toggle_selector.RS.set_active(True)

        toggle_selector.RS = RectangleSelector(self.current_ax, self.line_select_callback,
                                               drawtype=drawtype, useblit=True,
                                               button=[1, 3],  # don't use middle button
                                               minspanx=0, minspany=0,
                                               spancoords='pixels',
                                               rectprops=dict(facecolor='red', edgecolor='yellow',
                                                              alpha=0.3, fill=True),
                                               interactive=True)
        plt.connect('key_press_event', toggle_selector)

    def line_select_callback(self, eclick, erelease):
        'eclick and erelease are the press and release events'
        self.x1, self.y1 = eclick.xdata, eclick.ydata
        self.x2, self.y2 = erelease.xdata, erelease.ydata
        print("(%3.2f, %3.2f) --> (%3.2f, %3.2f)" % (self.x1, self.y1, self.x2, self.y2))
        print(" The button you used were: %s %s" % (eclick.button, erelease.button))


##################
#  Line Selector #
##################

class LineSelector:
    def __init__(self, image,
                 fig_xsize=None, fig_ysize=None,
                 cmap=plt.cm.gist_gray,
                 vmin=None, vmax=None
                 ):
        self.x1 = None
        self.x2 = None
        self.y1 = None
        self.y2 = None

        self.pnt1 = None
        self.pnt2 = None

        self.fig = plt.figure(figsize=(fig_xsize, fig_ysize))
        self.ax = self.fig.add_subplot(111, visible=False)
        self.rect = patches.Rectangle(
            (0.0, 0.0), fig_xsize, fig_ysize,
            fill=False, clip_on=False, visible=False)
        self.rect_patch = self.ax.add_patch(self.rect)
        self.cid = self.rect_patch.figure.canvas.mpl_connect('button_press_event',
                                                             self)
        self.cmap = cmap
        self.image = image
        self.plot = self.gray_plot(self.image, vmin=vmin, vmax=vmax, fig=self.fig, return_ax=True)
        self.plot.set_title('Select 2 Points of Interest')

    def gray_plot(self, image, vmin=None, vmax=None, fig=None, return_ax=False):
        if vmin is None:
            vmin = np.nanpercentile(self.image, 1)
        if vmax is None:
            vmax = np.nanpercentile(self.image, 99)
        ax = fig.add_axes([0.1, 0.1, 0.8, 0.8])
        ax.imshow(image, cmap=self.cmap, vmin=vmin, vmax=vmax)
        if return_ax:
            return (ax)

    def __call__(self, event):
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