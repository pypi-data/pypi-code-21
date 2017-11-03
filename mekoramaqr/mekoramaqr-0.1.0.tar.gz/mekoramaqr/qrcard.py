# MekoramaQR
# Copyright (C) 2017 by MekoramaQR contributors

# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.

# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.

# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <https://www.gnu.org/licenses/>.

from enum import Enum

import blocks
import math
import os.path
import logging
import itertools
from PIL import Image, ImageFont, ImageDraw
import textwrap
import numpy as np
from functools import reduce

from .mekolevel import MekoLevel
from .mekoqr import MekoQR
from .blocks import BlockType, Block
from . import get_resource

# reference unit; translation to get to next block along x axis
_sprite_unit_u = 18
_sprite_unit_v = 11
# sprite size, including clear padding
_sprite_width = 72
_sprite_height = 88


class WaterSprite(object):
    """Associates a WATER blocktype with a particular sprite.

    The direction property is used to determine the sprite direction, which is kind of a hack.
    """

    _sprites = Image.open(get_resource("water_sprite.png"))

    def __init__(self, direction, sprite_pos):
        """Create WaterSprite

        Args:
            direction: block direction string
            sprite_pos: sprite index within the tiled sprite file, or list of indices to combine

        """
        self.blocktype = BlockType(11, "Water", direction=direction)

        def cropsprite(i):
            """Crop sprite i out of a strip"""
            return self._sprites.crop((
                i * _sprite_width,
                0,
                (i + 1) * _sprite_width,
                _sprite_height))

        if type(sprite_pos) == int:
            self.sprite = cropsprite(sprite_pos)
        else:
            self.sprite = reduce(Image.alpha_composite,  # combine sprites
                map(cropsprite, sprite_pos))  # crop out sprite

    def toblock(self):
        return Block(self.blocktype)


class WaterSpriteTypes(Enum):
    """Enum of all WATER sprite directions.
    """

    LEFT = WaterSprite("Z", 0)
    RIGHT = WaterSprite("X", 1)
    TOP = WaterSprite("Y", 2)
    TOP_LEFT = WaterSprite("YZ", 3)
    TOP_RIGHT = WaterSprite("XY", 4)
    CORNER = WaterSprite("XYZ", 5)
    LEFT_RIGHT = WaterSprite("XZ", [0, 1])

    def toblock(self):
        return self.value.toblock()

    @classmethod
    def get_sprite_from_dir(cls, direction):
        """

        Args:
            direction: direction string

        Returns:
            WaterSpriteTypes instance whose value has the matching type

        """
        return next(itertools.ifilter(lambda w: w.value.blocktype.direction == direction, iter(cls)))


class Preview(object):
    """Create a 2D preview of a mekorama level"""

    def __init__(self, level=None, background=(0, 0, 0, 0), center=(0, 0, 0)):
        """Create a blank preview

        Args:
            - level (MekoLevel): (optional) add the mekolevel to this preview
            - background (tuple of int): background color, as (r, g, b, a) tuple
                between 0 and 255. Default: clear
            - center (tuple of float): block coordinate (x,y,z) for the center
                of this preview. Defaults to (0, 0, 0).
        """
        self._sprite_coords = None
        # reference unit; translation to get to next block along x axis
        self._sprite_unit_u = _sprite_unit_u
        self._sprite_unit_v = _sprite_unit_v
        # sprite size, including clear padding
        self._sprite_width = _sprite_width
        self._sprite_height = _sprite_height

        # full dimensions
        self._width = 32 * self._sprite_unit_u
        self._height = 32 * 2 * self._sprite_unit_v
        self._sprite = Image.open(get_resource("iso_sprites.png"))
        self._unknown_sprite = Image.open(get_resource("unknown_sprite.png"))
        self._water_sprite = Image.open(get_resource("water_sprite.png"))
        self.center = center
        self.background = background
        self.clear()

        if level:
            self.center_on_level(level)
            self.add_level(level)

    def clear(self):
        """Clears the image, resetting to just the background"""
        self._preview = Image.new(
            mode='RGBA',
            size=(self._width, self._height),
            color=self.background)

    @property
    def sprite_coords(self):
        """Getter for the coordinates of each block within the sprite map

        Returns:
            dict mapping block values to a rectangle (left, top, right, bottom)

        """
        if self._sprite_coords is None:
            # sprites are arranged on a grid with this size

            bt = blocks.BlockTypes()
            # grid position
            grid_pos = [
                (bt.STONE, (0, 0, 0)),
                (bt.BRICK, (0, 0, 0)),
                (bt.WIN, (0, 0, 0)),
                (bt.STONE_STAIR, (0, 0, 0)),
                (bt.STONE_STAIR, (0, 1, 0)),
                (bt.STONE_STAIR, (0, 2, 0)),
                (bt.STONE_STAIR, (0, 3, 0)),
                (bt.STONE_STAIR, (1, 0, 0)),
                (bt.STONE_STAIR, (1, 0, 3)),
                (bt.STONE_STAIR, (1, 0, 2)),
                (bt.STONE_STAIR, (1, 0, 1)),
                (bt.STONE_STAIR, (0, 0, 1)),
                (bt.STONE_STAIR, (0, 1, 1)),
                (bt.STONE_STAIR, (0, 2, 1)),
                (bt.STONE_STAIR, (0, 3, 1)),
                (bt.STONE_WEDGE, (0, 0, 0)),
                (bt.STONE_WEDGE, (0, 1, 0)),
                (bt.STONE_WEDGE, (0, 2, 0)),
                (bt.STONE_WEDGE, (0, 3, 0)),
                (bt.STONE_WEDGE, (1, 0, 0)),
                (bt.STONE_WEDGE, (1, 0, 3)),
                (bt.STONE_WEDGE, (1, 0, 2)),
                (bt.STONE_WEDGE, (1, 0, 1)),
                (bt.STONE_WEDGE, (0, 0, 1)),
                (bt.STONE_WEDGE, (0, 1, 1)),
                (bt.STONE_WEDGE, (0, 2, 1)),
                (bt.STONE_WEDGE, (0, 3, 1)),
                (bt.GRASS, (0, 0, 0)),
                (bt.B_BOT, (0, 0, 0)),
                (bt.B_BOT, (0, 1, 0)),
                (bt.B_BOT, (0, 2, 0)),
                (bt.B_BOT, (0, 3, 0)),
                (bt.ZAPPER, (0, 0, 0)),
                (bt.ZAPPER, (1, 0, 0)),
                (bt.ZAPPER, (1, 0, 3)),
                (bt.ZAPPER, (1, 0, 2)),
                (bt.ZAPPER, (1, 0, 1)),
                (bt.ZAPPER, (2, 0, 0)),
                (bt.DRAGGABLE, (0, 0, 0)),
                (bt.DESERT, (0, 0, 0)),
                (bt.MOTOR, (0, 0, 0)),
                (bt.MOTOR, (0, 1, 0)),
                (bt.MOTOR, (0, 2, 0)),
                (bt.MOTOR, (0, 3, 0)),
                (bt.MOTOR, (1, 0, 0)),
                (bt.MOTOR, (3, 0, 0)),
                (bt.METAL, (0, 0, 0)),
                (bt.R_BOT, (0, 0, 0)),
                (bt.R_BOT, (0, 1, 0)),
                (bt.R_BOT, (0, 2, 0)),
                (bt.R_BOT, (0, 3, 0)),
                (bt.EYE, (0, 0, 0)),
                (bt.CURVED_RAIL, (0, 0, 0)),
                (bt.CURVED_RAIL, (0, 1, 0)),
                (bt.CURVED_RAIL, (0, 2, 0)),
                (bt.CURVED_RAIL, (0, 3, 0)),
                (bt.CURVED_RAIL, (1, 0, 0)),
                (bt.CURVED_RAIL, (1, 0, 3)),
                (bt.CURVED_RAIL, (1, 0, 2)),
                (bt.CURVED_RAIL, (1, 0, 1)),
                (bt.CURVED_RAIL, (0, 0, 1)),
                (bt.CURVED_RAIL, (0, 1, 1)),
                (bt.CURVED_RAIL, (0, 2, 1)),
                (bt.CURVED_RAIL, (0, 3, 1)),
                (bt.METAL_HALF_PILLAR, (0, 0, 0)),
                (bt.METAL_HALF_PILLAR, (0, 1, 0)),
                (bt.METAL_HALF_PILLAR, (0, 2, 0)),
                (bt.METAL_HALF_PILLAR, (0, 3, 0)),
                (bt.METAL_HALF_PILLAR, (1, 0, 3)),
                (bt.METAL_HALF_PILLAR, (1, 0, 2)),
                (bt.METAL_HALF_PILLAR, (3, 0, 0)),
                (bt.METAL_HALF_PILLAR, (3, 0, 3)),
                (bt.METAL_HALF_PILLAR, (0, 0, 3)),
                (bt.METAL_HALF_PILLAR, (0, 1, 3)),
                (bt.METAL_HALF_PILLAR, (0, 2, 3)),
                (bt.METAL_HALF_PILLAR, (0, 3, 3)),
                (bt.RAIL, (2, 0, 0)),
                (bt.RAIL, (0, 0, 1)),
                (bt.RAIL, (0, 3, 1)),
                (bt.STONE_PILLAR, (0, 0, 0)),
                (bt.STONE_PILLAR, (0, 0, 3)),
                (bt.STONE_PILLAR, (3, 0, 0)),
                (bt.BALL, (0, 0, 0)),
                (bt.METAL_PILLAR, (0, 0, 0)),
                (bt.METAL_PILLAR, (0, 0, 3)),
                (bt.METAL_PILLAR, (3, 0, 0)),
                (bt.SLIDER, (2, 0, 0)),
                (bt.SLIDER, (0, 0, 1)),
                (bt.SLIDER, (0, 3, 1)),
                (bt.FENCE, (0, 0, 0)),
                (bt.FENCE, (0, 3, 0)),
                (bt.FENCE, (1, 0, 0)),
                (bt.FENCE, (1, 0, 1)),
                (bt.FENCE, (0, 0, 1)),
                (bt.FENCE, (0, 3, 1)),
                # Non-standard
                (bt.GRASS_WEDGE, (0, 0, 0)),
                (bt.GRASS_WEDGE, (0, 1, 0)),
                (bt.GRASS_WEDGE, (0, 2, 0)),
                (bt.GRASS_WEDGE, (0, 3, 0)),
                (bt.GRASS_WEDGE, (1, 0, 0)),
                (bt.GRASS_WEDGE, (1, 0, 3)),
                (bt.GRASS_WEDGE, (1, 0, 2)),
                (bt.GRASS_WEDGE, (1, 0, 1)),
                (bt.GRASS_WEDGE, (0, 0, 1)),
                (bt.GRASS_WEDGE, (0, 1, 1)),
                (bt.GRASS_WEDGE, (0, 2, 1)),
                (bt.GRASS_WEDGE, (0, 3, 1)),
                (bt.GOLDEN_BALL, (0, 0, 0)),
                (bt.BUTTON, (0, 0, 0)),
                (bt.STONE_CORNER, (0, 0, 0)),
                (bt.STONE_CORNER, (0, 1, 0)),
                (bt.STONE_CORNER, (0, 2, 0)),
                (bt.STONE_CORNER, (0, 3, 0)),
                (bt.STONE_CORNER, (1, 0, 0)),
                (bt.STONE_CORNER, (1, 0, 3)),
                (bt.STONE_CORNER, (1, 0, 2)),
                (bt.STONE_CORNER, (1, 0, 1)),
                (bt.STONE_CORNER, (0, 0, 1)),
                (bt.STONE_CORNER, (0, 1, 1)),
                (bt.STONE_CORNER, (0, 2, 1)),
                (bt.STONE_CORNER, (0, 3, 1)),
                (bt.WHEEL, (0, 0, 0)),
                (bt.WHEEL, (0, 0, 3)),
                (bt.WHEEL, (3, 0, 0)),
                (bt.METAL_STAIR, (0, 0, 0)),
                (bt.METAL_STAIR, (0, 1, 0)),
                (bt.METAL_STAIR, (0, 2, 0)),
                (bt.METAL_STAIR, (0, 3, 0)),
                (bt.METAL_STAIR, (1, 0, 0)),
                (bt.METAL_STAIR, (1, 0, 3)),
                (bt.METAL_STAIR, (1, 0, 2)),
                (bt.METAL_STAIR, (1, 0, 1)),
                (bt.METAL_STAIR, (0, 0, 1)),
                (bt.METAL_STAIR, (0, 1, 1)),
                (bt.METAL_STAIR, (0, 2, 1)),
                (bt.METAL_STAIR, (0, 3, 1)),
                (bt.METAL_CORNER, (0, 0, 0)),
                (bt.METAL_CORNER, (0, 1, 0)),
                (bt.METAL_CORNER, (0, 2, 0)),
                (bt.METAL_CORNER, (0, 3, 0)),
                (bt.METAL_CORNER, (1, 0, 0)),
                (bt.METAL_CORNER, (1, 0, 3)),
                (bt.METAL_CORNER, (1, 0, 2)),
                (bt.METAL_CORNER, (1, 0, 1)),
                (bt.METAL_CORNER, (0, 0, 1)),
                (bt.METAL_CORNER, (0, 1, 1)),
                (bt.METAL_CORNER, (0, 2, 1)),
                (bt.METAL_CORNER, (0, 3, 1)),
            ]

            # convert to pixel coords
            self._sprite_coords = dict()
            for i, item in enumerate(grid_pos):
                blocktype, rot = item
                val = blocktype.value
                box = (
                    i * self._sprite_width,
                    0,
                    (i + 1) * self._sprite_width,
                    self._sprite_height)
                self.sprite_coords.setdefault(val, {})[rot] = box

        return self._sprite_coords

    def _getsprite(self, block):
        value = block.blocktype.value
        rot = block.blocktype.subtypes[block.subtype].rot if block.subtype is not None else block.blocktype.rot

        if value == MekoLevel.blocktypes.WATER.value:
            if block.blocktype.direction is not None:
                water = WaterSpriteTypes.get_sprite_from_dir(block.blocktype.direction)
                return water.value.sprite
            else:
                # Original, un-oriented water. Ignore this, as it should overlap with a WaterSprite at the same coord.
                return Image.new("RGBA", (1, 1), (0, 0, 0, 0))  # clear pixel
        if value in self.sprite_coords:
            if rot in self.sprite_coords[value]:
                box = self.sprite_coords[value][rot]
            else:
                logging.error("Unrecognized rotation %s for %s", rot, block.blocktype.name)
                box = next(iter(self.sprite_coords[value]))
            return self._sprite.crop(box)
        else:
            logging.error("Unrecognized BlockType %s", block.blocktype.name)
            # Default block
            return self._unknown_sprite

    def _pixelpos(self, blockpos):
        """Convert a (x,y,z) block position to the pixel coordinates for that sprite"""
        # Define based on sprite unit (u), which is two blocks wide
        # This could be made much more efficient if we stored the intermediate matrices between calls
        # basis vectors:
        basis = np.array([[self._sprite_unit_u, self._sprite_unit_v],
                          [0, -2 * self._sprite_unit_v],
                          [-self._sprite_unit_u, self._sprite_unit_v]]).transpose()
        centerpxl = np.array([[self._width - self._sprite_width], [self._height - self._sprite_height]]) / 2.
        centerblk = np.array(self.center).reshape(3, 1)
        xyzblk = np.array(blockpos).reshape(3, 1)
        xyzpxl = basis.dot(xyzblk - centerblk) + centerpxl
        return int(xyzpxl[0, 0]), int(xyzpxl[1, 0])

    def add_block(self, block, blockpos):
        """Adds a block to the Preview

        Blocks overlap previous blocks, so they should be added in increasing (x+y+z)

        Args:
         - blockval (int): value of the blocktype to be placed
         - blockpos (int,int,int): (x,y,z) block position. All coordinates should be less than 16.

        Returns:
            self (for chaining)

        """
        sprite = self._getsprite(block)
        pos = self._pixelpos(blockpos)

        self._preview.paste(sprite, pos, sprite)
        return self

    def center_on_level(self, level):
        """Set the preview's center to optimally show the given level

        The center is set to the center of the level's bounding box.

        Args:
            - level (MekoLevel)

        Returns:
            (x, y, z), after updating self.center.

        """
        xmin, xmax, ymin, ymax, zmin, zmax = level.getBounds()
        self.center = ((xmin + xmax) // 2,
                       (ymin + ymax) // 2,
                       (zmin + zmax) // 2)
        return self.center

    @staticmethod
    def _water_surface(level, replace=None):
        mat = level.getBlockMatrix()
        bt = level.blocktypes

        if replace is None:
            replace = [bt.AIR, bt.WATER]

        # first water encountered, searching from top down
        waterpos = next(((x, y, z)
                         for y in range(level.size[1] - 1, -1, -1)
                         for z in range(level.size[2])
                         for x in range(level.size[0])
                         if mat[z][y][x].blocktype == bt.WATER),
                        None)

        if waterpos is None:
            return

        ignore_blocks = [bt.AIR,
                         bt.WATER,
                         bt.METAL,
                         bt.SLIDER,
                         bt.DRAGGABLE,
                         bt.DRAGGABLE_PILLAR,
                         bt.B_BOT,
                         bt.R_BOT,
                         ]
        xmin, xmax, ymin, ymax, zmin, zmax = level.getBounds(ignore_blocks)

        waterblock = mat[waterpos[2]][waterpos[1]][waterpos[0]]

        # top surface
        for z in range(zmin, zmax):
            for x in range(xmin, xmax):
                if mat[z][waterpos[1]][x].blocktype in replace:
                    yield (x, waterpos[1], z, WaterSpriteTypes.TOP.toblock())
        # left surface
        for y in range(ymin, waterpos[1]):
            for x in range(xmin, xmax):
                if mat[zmax][y][x].blocktype in replace:
                    yield (x, y, zmax, WaterSpriteTypes.LEFT.toblock())
        # right surface
        for y in range(ymin, waterpos[1]):
            for z in range(zmin, zmax):
                if mat[z][y][xmax].blocktype in replace:
                    yield (xmax, y, z, WaterSpriteTypes.RIGHT.toblock())
        # topleft
        for x in range(xmin, xmax):
            if mat[zmax][waterpos[1]][x].blocktype in replace:
                yield (x, waterpos[1], zmax, WaterSpriteTypes.TOP_LEFT.toblock())
        # topright
        for z in range(zmin, zmax):
            if mat[z][waterpos[1]][xmax].blocktype in replace:
                yield (xmax, waterpos[1], z, WaterSpriteTypes.TOP_RIGHT.toblock())
        # front
        for y in range(ymin, waterpos[1]):
            if mat[zmax][y][xmax].blocktype in replace:
                yield (xmax, y, zmax, WaterSpriteTypes.LEFT_RIGHT.toblock())
        # corner
        if mat[zmax][waterpos[1]][xmax].blocktype in replace:
            yield (xmax, waterpos[1], zmax, WaterSpriteTypes.CORNER.toblock())

    def add_level(self, level):
        """Add a MekoLevel to this Preview

        Returns:
            self (for chaining)

        """
        waterblocks = self._water_surface(level)
        blocks = level.getBlocks()
        blocks.extend(waterblocks)
        blocks.sort(key=lambda x: sum(x[:3]))
        for x, y, z, blk in blocks:
            self.add_block(blk, (x, y, z))

    def create(self):
        """Create an image from the current set of blocks

        Returns:
            (Image) The rendered preview image

        """
        # Currently we render as blocks are added
        return self._preview


class MekoCard(object):
    def __init__(self, level):
        self._level = level
        self._width = 732
        self._height = 1024

    def create(self):
        # background
        card = Image.open(get_resource('card_background.png'))

        # Resize preview to fit card width
        preview_width = 584
        preview_height = 494
        preview_corner = (74, 74)
        preview = Preview(self._level, background=(0, 0, 0, 0)).create()
        scale = float(preview_width) / preview.size[0]
        preview = preview.resize(
            (preview_width, int(scale * preview.size[1])),
            Image.BICUBIC)
        # Crop top & bottom off preview
        h0 = (preview.size[1] - preview_height) // 2
        preview = preview.crop((0, h0, preview_width, h0 + preview_height))

        # Center on card
        card.paste(preview, preview_corner, preview)

        # Add text
        draw = ImageDraw.Draw(card)
        ttyfile = get_resource("dbxlnw__.ttf")
        font32 = ImageFont.truetype(ttyfile, 32)
        font58 = ImageFont.truetype(ttyfile, 58)
        font40 = ImageFont.truetype(ttyfile, 40)

        url = "mekostudio.com"
        title = textwrap.fill(level.title, 8)
        author = textwrap.fill("by %s" % (level.author), 8)

        spacing = 8
        # url_width = font32.getsize(url)[0]
        # title_width = font58.getsize(title)[0]
        # author_width = font40.getsize(author)[0]
        url_size = draw.textsize(url, font=font32, spacing=spacing)
        title_size = draw.textsize(title, font=font58, spacing=spacing)
        author_size = draw.textsize(author, font=font40, spacing=spacing)

        y = 614 - url_size[1]
        draw.text((284 - url_size[0], y), url, font=font32, align="right", spacing=spacing, fill=(180, 180, 180))
        y += url_size[1]
        y += 10
        draw.text((284 - title_size[0], y), title, font=font58, align="right", spacing=spacing, fill=(0, 186, 255))
        y += title_size[1]
        y += 8
        draw.text((284 - author_size[0], y), author, font=font40, align="right", spacing=spacing, fill=(180, 180, 180))

        # Add qrcode
        qr_corner = (304, 596)
        qr_max_size = 350
        qr = MekoQR()
        img = qr.save(level.toHex(), box_size=1)
        # Scale up to fit in 350x350
        scale = int(2 ** math.floor(math.log(float(qr_max_size) / max(img.size), 2)))
        img = img.resize((img.size[0] * scale, img.size[1] * scale))

        # overlay = Image.new(
        #             mode='RGBA',
        #             size=(qr_max_size, qr_max_size),
        #             color=(255, 0, 0, 255))
        # card.paste(overlay, qr_corner)

        card.paste(img, (qr_corner[0] + (qr_max_size - img.size[0]) // 2,
                         qr_corner[1] + (qr_max_size - img.size[1]) // 2))

        return card


if __name__ == "__main__":
    outfile = "test.png"
    infile = "mekoramaqr/test/codes/axis.png"
    infile = "mekoramaqr/test/codes/larsh-tiles.png"
    infile = "mekoramaqr/test/codes/quantumforce-all_blocks.png"
    infile = "mekoramaqr/test/codes/water.png"

    # load level
    level = None
    with open(infile, 'rb') as levelfile:
        qr = MekoQR(levelfile)
        level = MekoLevel(code=qr.code)
    bt = MekoLevel.blocktypes

    # prev = Preview()
    # prev.add_block(bt.GRASS.value, (0, 0, 0))
    # for i in range(2, 16):
    #     prev.add_block(bt.STONE.value, (i, 0, 0))
    #     prev.add_block(bt.BRICK.value, (0, i, 0))
    #     prev.add_block(bt.METAL.value, (0, 0, i))
    # if level:
    #     prev.add_level(level)
    #
    # img = prev.create()

    card = MekoCard(level)
    img = card.create()

    print("Saving to {}".format(os.path.abspath(outfile)))
    img.save(outfile)
