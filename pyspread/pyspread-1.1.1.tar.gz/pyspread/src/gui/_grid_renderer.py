#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Copyright Martin Manns
# Distributed under the terms of the GNU General Public License

# --------------------------------------------------------------------
# pyspread is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# pyspread is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with pyspread.  If not, see <http://www.gnu.org/licenses/>.
# --------------------------------------------------------------------

"""
_grid_renderer
==============

Provides
--------

1) GridRenderer: Draws the grid
2) Background: Background drawing

"""

import wx.grid
import wx.lib.mixins.gridlabelrenderer as glr

from src.sysvars import get_color
from src.config import config
import src.lib.i18n as i18n
from src.lib._grid_cairo_renderer import GridCellCairoRenderer
from src.gui._events import post_command_event, EventMixin

try:
    import src.lib.vlc as vlc
    from grid_panels import VLCPanel
except (ImportError, WindowsError):
    vlc = None

# Use ugettext instead of getttext to avoid unicode errors
_ = i18n.language.ugettext


class GridRenderer(wx.grid.PyGridCellRenderer, EventMixin):
    """This renderer draws borders and text at specified font, size, color"""

    selection_color_tuple = \
        tuple([c / 255.0 for c in get_color(config["selection_color"]).Get()] +
              [0.5])

    def __init__(self, data_array):

        wx.grid.PyGridCellRenderer.__init__(self)

        self.data_array = data_array

        # Cache for cell content
        self.cell_cache = {}

        # Video cell register, contains keys
        self.video_cells = {}

        # Zoom of grid
        self.zoom = 1.0

        # Old cursor position
        self.old_cursor_row_col = 0, 0

    def get_zoomed_size(self, size):
        """Returns zoomed size as Integer

        Parameters
        ----------

        font_size: Integer
        \tOriginal font size

        """

        return max(1.0, round(size * self.zoom))

    def _draw_cursor(self, dc, grid, row, col,
                     pen=None, brush=None):
        """Draws cursor as Rectangle in lower right corner"""

        # If in full screen mode draw no cursor
        if grid.main_window.IsFullScreen():
            return

        key = row, col, grid.current_table
        rect = grid.CellToRect(row, col)
        rect = self.get_merged_rect(grid, key, rect)

        # Check if cell is invisible
        if rect is None:
            return

        size = self.get_zoomed_size(1.0)

        caret_length = int(min([rect.width, rect.height]) / 5.0)

        color = get_color(config["text_color"])
        if pen is None:
          pen = wx.Pen(color)
        if brush is None:
          brush = wx.Brush(color)

        pen.SetWidth(size)

        # Inner right and lower borders
        border_left = rect.x + size - 1
        border_right = rect.x + rect.width - size - 1
        border_upper = rect.y + size - 1
        border_lower = rect.y + rect.height - size - 1

        points_lr = [
            (border_right, border_lower - caret_length),
            (border_right, border_lower),
            (border_right - caret_length, border_lower),
            (border_right, border_lower),
        ]

        points_ur = [
            (border_right, border_upper + caret_length),
            (border_right, border_upper),
            (border_right - caret_length, border_upper),
            (border_right, border_upper),
        ]

        points_ul = [
            (border_left, border_upper + caret_length),
            (border_left, border_upper),
            (border_left + caret_length, border_upper),
            (border_left, border_upper),
        ]

        points_ll = [
            (border_left, border_lower - caret_length),
            (border_left, border_lower),
            (border_left + caret_length, border_lower),
            (border_left, border_lower),
        ]

        point_list = [points_lr, points_ur, points_ul, points_ll]

        dc.DrawPolygonList(point_list, pens=pen, brushes=brush)

        self.old_cursor_row_col = row, col

    def update_cursor(self, dc, grid, row, col):
        """Whites out the old cursor and draws the new one"""

        old_row, old_col = self.old_cursor_row_col

        bgcolor = get_color(config["background_color"])

        self._draw_cursor(dc, grid, old_row, old_col,
                          pen=wx.Pen(bgcolor), brush=wx.Brush(bgcolor))
        self._draw_cursor(dc, grid, row, col)

    def get_merging_cell(self, grid, key):
        """Returns row, col, tab of merging cell if the cell key is merged"""

        return grid.code_array.cell_attributes.get_merging_cell(key)

    def get_merged_rect(self, grid, key, rect):
        """Returns cell rect for normal or merged cells and None for merged"""

        row, col, tab = key

        # Check if cell is merged:
        cell_attributes = grid.code_array.cell_attributes
        merge_area = cell_attributes[(row, col, tab)]["merge_area"]

        if merge_area is None:
            return rect

        else:
            # We have a merged cell
            top, left, bottom, right = merge_area

            # Are we drawing the top left cell?
            if top == row and left == col:
                # Set rect to merge area
                ul_rect = grid.CellToRect(row, col)
                br_rect = grid.CellToRect(bottom, right)

                width = br_rect.x - ul_rect.x + br_rect.width
                height = br_rect.y - ul_rect.y + br_rect.height

                rect = wx.Rect(ul_rect.x, ul_rect.y, width, height)

                return rect

    def _get_drawn_rect(self, grid, key, rect):
        """Replaces drawn rect if the one provided by wx is incorrect

        This handles merged rects including those that are partly off screen.

        """

        rect = self.get_merged_rect(grid, key, rect)
        if rect is None:
            # Merged cell is drawn
            if grid.is_merged_cell_drawn(key):
                # Merging cell is outside view
                row, col, __ = key = self.get_merging_cell(grid, key)
                rect = grid.CellToRect(row, col)
                rect = self.get_merged_rect(grid, key, rect)
            else:
                return

        return rect

    def _get_draw_cache_key(self, grid, key, drawn_rect, is_selected):
        """Returns key for the screen draw cache"""

        row, col, tab = key
        cell_attributes = grid.code_array.cell_attributes

        zoomed_width = drawn_rect.width / self.zoom
        zoomed_height = drawn_rect.height / self.zoom

        # Button cells shall not be executed for preview
        if grid.code_array.cell_attributes[key]["button_cell"]:
            cell_preview = repr(grid.code_array(key))[:100]
        else:
            cell_preview = repr(grid.code_array[key])[:100]

        sorted_keys = sorted(grid.code_array.cell_attributes[key].iteritems())

        key_above_left = row - 1, col - 1, tab
        key_above = row - 1, col, tab
        key_above_right = row - 1, col + 1, tab
        key_left = row, col - 1, tab
        key_right = row, col + 1, tab
        key_below_left = row + 1, col - 1, tab
        key_below = row + 1, col, tab

        borders = []

        for k in [key, key_above_left, key_above, key_above_right,
                  key_left, key_right, key_below_left, key_below]:
            borders.append(cell_attributes[k]["borderwidth_bottom"])
            borders.append(cell_attributes[k]["borderwidth_right"])
            borders.append(cell_attributes[k]["bordercolor_bottom"])
            borders.append(cell_attributes[k]["bordercolor_right"])

        return (zoomed_width, zoomed_height, is_selected, cell_preview,
                tuple(sorted_keys), tuple(borders))

    def _get_cairo_bmp(self, mdc, key, rect, is_selected, view_frozen):
        """Returns a wx.Bitmap of cell key in size rect"""

        bmp = wx.EmptyBitmap(rect.width, rect.height)
        mdc.SelectObject(bmp)
        mdc.SetBackgroundMode(wx.SOLID)
        mdc.SetBackground(wx.WHITE_BRUSH)
        mdc.Clear()
        mdc.SetDeviceOrigin(0, 0)

        context = wx.lib.wxcairo.ContextFromDC(mdc)

        context.save()

        # Zoom context
        zoom = self.zoom
        context.scale(zoom, zoom)

        # Set off cell renderer by 1/2 a pixel to avoid blurry lines
        rect_tuple = \
            -0.5, -0.5, rect.width / zoom + 0.5, rect.height / zoom + 0.5
        spell_check = config["check_spelling"]
        cell_renderer = GridCellCairoRenderer(context, self.data_array,
                                              key, rect_tuple, view_frozen,
                                              spell_check=spell_check)
        # Draw cell
        cell_renderer.draw()

        # Draw selection if present
        if is_selected:
            context.set_source_rgba(*self.selection_color_tuple)
            context.rectangle(*rect_tuple)
            context.fill()

        context.restore()

        return bmp

    def Draw(self, grid, attr, dc, rect, row, col, isSelected):
        """Draws the cell border and content using pycairo"""

        key = row, col, grid.current_table

        # If cell is merge draw the merging cell if invisibile
        if grid.code_array.cell_attributes[key]["merge_area"]:
            key = self.get_merging_cell(grid, key)

        drawn_rect = self._get_drawn_rect(grid, key, rect)
        if drawn_rect is None:
            return

        cell_cache_key = self._get_draw_cache_key(grid, key, drawn_rect,
                                                  isSelected)

        mdc = wx.MemoryDC()

        if vlc is not None and key in self.video_cells and \
           grid.code_array.cell_attributes[key]["panel_cell"]:
            # Update video position of previously created video panel
            self.video_cells[key].SetClientRect(drawn_rect)

        elif cell_cache_key in self.cell_cache:
            mdc.SelectObject(self.cell_cache[cell_cache_key])

        else:
            code = grid.code_array(key)
            if vlc is not None and code is not None and \
               grid.code_array.cell_attributes[key]["panel_cell"]:
                try:
                    # A panel is to be displayed
                    panel_cls = grid.code_array[key]

                    # Assert that we have a subclass of a wxPanel that we
                    # can instantiate
                    assert issubclass(panel_cls, wx.Panel)

                    video_panel = panel_cls(grid)
                    video_panel.SetClientRect(drawn_rect)
                    # Register video cell
                    self.video_cells[key] = video_panel

                    return

                except Exception, err:
                    # Someting is wrong with the panel to be displayed
                    post_command_event(grid.main_window, self.StatusBarMsg,
                                       text=unicode(err))
                    bmp = self._get_cairo_bmp(mdc, key, drawn_rect, isSelected,
                                              grid._view_frozen)
            else:
                bmp = self._get_cairo_bmp(mdc, key, drawn_rect, isSelected,
                                          grid._view_frozen)

            # Put resulting bmp into cache
            self.cell_cache[cell_cache_key] = bmp

        dc.Blit(drawn_rect.x, drawn_rect.y,
                drawn_rect.width, drawn_rect.height,
                mdc, 0, 0, wx.COPY)

        # Draw cursor
        if grid.actions.cursor[:2] == (row, col):
            self.update_cursor(dc, grid, row, col)

# end of class GridRenderer


class RowLabelRenderer(glr.GridLabelRenderer):
    """Row label renderer mixin class that highlights the current line"""

    def Draw(self, grid, dc, rect, row):
        rect.y -= 1
        if row == grid.actions.cursor[0]:
            color = get_color(config["selection_color"])
        else:
            color = get_color(config["label_color"])

        dc.SetPen(wx.TRANSPARENT_PEN)
        dc.SetBrush(wx.Brush(color))
        dc.DrawRectangleRect(rect)
        hAlign, vAlign = grid.GetRowLabelAlignment()
        text = grid.GetRowLabelValue(row)
        if row != grid.actions.cursor[0]:
            self.DrawBorder(grid, dc, rect)
        self.DrawText(grid, dc, rect, text, hAlign, vAlign)

# end of class RowLabelRenderer


class ColLabelRenderer(glr.GridLabelRenderer):
    """Column label renderer mixin class that highlights the current line"""

    def Draw(self, grid, dc, rect, col):
        rect.x -= 1
        if col == grid.actions.cursor[1]:
            color = get_color(config["selection_color"])

        else:
            color = get_color(config["label_color"])

        dc.SetPen(wx.TRANSPARENT_PEN)
        dc.SetBrush(wx.Brush(color))
        dc.DrawRectangleRect(rect)
        hAlign, vAlign = grid.GetColLabelAlignment()
        text = grid.GetColLabelValue(col)
        if col != grid.actions.cursor[1]:
            self.DrawBorder(grid, dc, rect)
        self.DrawText(grid, dc, rect, text, hAlign, vAlign)

# end of class ColLabelRenderer
