import numpy as np

from IPython.display import Markdown, display

import matplotlib.pyplot as plt
from matplotlib.widgets import RectangleSelector

plt.rcParams.update({'font.size': 12})


class AOI_Selector:
    def __init__(self,
                 image,
                 fig_xsize=None, fig_ysize=None,
                 cmap=plt.cm.gist_gray,
                 vmin=None, vmax=None
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
        self.current_ax.imshow(self.image, cmap=plt.cm.gist_gray, vmin=self.vmin, vmax=self.vmax)

        def toggle_selector(self, event):
            print(' Key pressed.')
            if event.key in ['Q', 'q'] and toggle_selector.RS.active:
                print(' RectangleSelector deactivated.')
                toggle_selector.RS.set_active(False)
            if event.key in ['A', 'a'] and not toggle_selector.RS.active:
                print(' RectangleSelector activated.')
                toggle_selector.RS.set_active(True)

        toggle_selector.RS = RectangleSelector(self.current_ax, self.line_select_callback,
                                               drawtype='box', useblit=True,
                                               button=[1, 3],  # don't use middle button
                                               minspanx=5, minspany=5,
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
