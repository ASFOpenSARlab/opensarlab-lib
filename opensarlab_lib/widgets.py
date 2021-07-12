from datetime import datetime

import pandas as pd

import ipywidgets as widgets
from ipywidgets import Layout


def gui_date_picker(dates: list) -> widgets.SelectionRangeSlider:
    start_date = datetime.strptime(min(dates), '%Y%m%d')
    end_date = datetime.strptime(max(dates), '%Y%m%d')
    date_range = pd.date_range(start_date, end_date, freq='D')
    options = [(date.strftime(' %m/%d/%Y '), date) for date in date_range]
    index = (0, len(options)-1)

    selection_range_slider = widgets.SelectionRangeSlider(
    options = options,
    index = index,
    description = 'Dates',
    orientation = 'horizontal',
    layout = {'width': '500px'})
    return(selection_range_slider)


def get_slider_vals(selection_range_slider: widgets.SelectionRangeSlider) -> list:
    '''Returns the minimum and maximum dates retrieved from the
    interactive time slider.

    Parameters:
    - selection_range_slider: Handle of the interactive time slider
    '''
    [a,b] = list(selection_range_slider.value)
    slider_min = a.to_pydatetime()
    slider_max = b.to_pydatetime()
    return[slider_min, slider_max]


def select_parameter(things, description=""):
    return widgets.RadioButtons(
        options=things,
        description=description,
        disabled=False,
        layout=Layout(min_width='800px')
    )


def select_mult_parameters(things, description=""):
    height = len(things) * 19
    return widgets.SelectMultiple(
        options=things,
        description=description,
        disabled=False,
        layout=widgets.Layout(height=f"{height}px", width='175px')
    )
