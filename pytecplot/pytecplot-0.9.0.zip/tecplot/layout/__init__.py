"""Pages, frames and other layout-related operations.

The "layout" consists of a stack of `Pages <Page>` identified by index or
`name <Page.name>`. Each `Page` consists of a single "workspace" which holds
a collection of `Frames <Frame>` that are laid out in relation to an area
called the `Paper`.

The |Tecplot Engine| is guaranteed to have at least one `Page` which is
holding onto at least one `Frame`. It also has the concept of an active
`Frame` and by extension, an active `Page`. Most, if not all operations
that require a handle to a `Frame` will use the active `Frame` by default.
This includes any function that operates on objects held by a `Frame`
such as a `Cartesian3DFieldPlot` or `Dataset`.
"""
from __future__ import division, print_function, absolute_import

from .frame import Frame
from .layout import (active_frame, active_page, add_page, aux_data, delete_page,
                     frames, next_page, page, pages, next_page, new_layout,
                     load_layout, save_layout)
from .page import Page, Paper
from .util import kwargs_pop_dataset
