from datetime import datetime
from typing import List, Set, Dict, Union, Optional

import pandas as pd

import ipywidgets as widgets
from ipywidgets import Layout


def gui_date_picker(dates: list) -> widgets.SelectionRangeSlider:
    """
    Takes: a list of dates
    Returns: a SelectionRangeSlider over the range of provided dates in daily steps
    """
    start_date = datetime.strptime(min(dates), '%Y%m%d')
    end_date = datetime.strptime(max(dates), '%Y%m%d')
    date_range = pd.date_range(start_date, end_date, freq='D')
    options = [(date.strftime(' %m/%d/%Y '), date) for date in date_range]
    index = (0, len(options) - 1)

    selection_range_slider = widgets.SelectionRangeSlider(
        options=options,
        index=index,
        description='Dates',
        orientation='horizontal',
        layout={'width': '500px'})
    return (selection_range_slider)


def get_slider_vals(selection_range_slider: widgets.SelectionRangeSlider) -> List[datetime.date]:
    """
    Takes: widgets.SelectionRangeSlider of dates
    Returns: a list containing the min and max selected dates from the SelectionRangeSlider
    """
    [a, b] = list(selection_range_slider.value)
    slider_min = a.to_pydatetime()
    slider_max = b.to_pydatetime()
    return [slider_min, slider_max]


def select_parameter(container: Union[List, Set, Dict],
                     description: Optional[str] = "",
                     min_width: Optional[str] = "800px") -> widgets.RadioButtons:
    """
    Takes: a container, an optional widget description, and an optional minimum widget width
    Returns: a widgets.RadioButtons object containing the objects in the container
    """
    return widgets.RadioButtons(
        options=container,
        description=description,
        disabled=False,
        layout=Layout(min_width=min_width)
    )


def select_mult_parameters(container: Union[List, Set, Dict],
                           description: Optional[str] = "",
                           width: Optional[str] = '175px'):
    """
    Takes: a container, an optional widget description, and an optional widget width
    Returns: a widgets.SelectMultiple containing the objects in the container
    """
    height = len(container) * 19
    return widgets.SelectMultiple(
        options=container,
        description=description,
        disabled=False,
        layout=widgets.Layout(height=f"{height}px", width=width)
    )
