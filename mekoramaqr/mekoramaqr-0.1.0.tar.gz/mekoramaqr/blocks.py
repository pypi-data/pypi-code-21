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

from __future__ import unicode_literals

# NOTE: Rotation axis is Y and not Z as usually
class BlockType:
    def __init__(self, value, name, direction=None, rot=(0, 0, 0), rot90=None, subtypes = None):
        self.name = name
        self.value = value
        self.subtypes = subtypes
        self.rot90 = rot90
        self.rot = rot

        '''
        None - No specific direction
        BS - Bottom/South
        BE - Bottom/East
        BN - Bottom/North
        BW - Bottom/West
        TN - Top/North
        TE - Top/East
        TS - Top/South
        TW - Top/West
        NE - North/East
        NW - North/West
        SW - South/West
        SE - South/East
        '''
        self.direction = direction

    def __repr__(self):
        return "BlockType({!r},{!r},direction={!r},rot={!r},rot90={!r}, ({} subtypes))"\
                .format(self.value, self.name, self.direction, self.rot,
                        self.rot90, len(self.subtypes) if self.subtypes else 0)

class BlockTypes:
    def __init__(self):
        self.AIR = BlockType(0, "Air")
        self.STONE = BlockType(1, "Stone")
        self.BRICK = BlockType(2, "Brick")
        self.WIN = BlockType(4, "Win")
        self.STONE_STAIR = BlockType(5, "StoneStair", subtypes=[
            BlockType(0x00, "StoneStair", direction='BN', rot=(0,0,0), rot90 = BlockType(0x01, "StoneStair", direction='BW')),  # Official
            BlockType(0x01, "StoneStair", direction='BW', rot=(0,1,0), rot90 = BlockType(0x02, "StoneStair", direction='BS')),
            BlockType(0x02, "StoneStair", direction='BS', rot=(0,2,0), rot90 = BlockType(0x03, "StoneStair", direction='BE')),
            BlockType(0x03, "StoneStair", direction='BE', rot=(0,3,0), rot90 = BlockType(0x00, "StoneStair", direction='BN')),

            BlockType(0x04, "StoneStair", direction='TN', rot=(1,0,0), rot90 = BlockType(0x05, "StoneStair", direction='TW')),  # Official
            BlockType(0x05, "StoneStair", direction='TW', rot=(1,0,3), rot90 = BlockType(0x06, "StoneStair", direction='TS')),
            BlockType(0x06, "StoneStair", direction='TS', rot=(1,0,2), rot90 = BlockType(0x07, "StoneStair", direction='TE')),
            BlockType(0x07, "StoneStair", direction='TE', rot=(1,0,1), rot90 = BlockType(0x04, "StoneStair", direction='TN')),

            BlockType(0x08, "StoneStair", direction='TS', rot=(2,0,0), rot90 = BlockType(0x09, "StoneStair", direction='TE')),  # Non official
            BlockType(0x09, "StoneStair", direction='TE', rot=(2,3,0), rot90 = BlockType(0x0a, "StoneStair", direction='TN')),
            BlockType(0x0a, "StoneStair", direction='TN', rot=(2,2,0), rot90 = BlockType(0x0b, "StoneStair", direction='TW')),
            BlockType(0x0b, "StoneStair", direction='TW', rot=(2,1,0), rot90 = BlockType(0x08, "StoneStair", direction='TS')),

            BlockType(0x0c, "StoneStair", direction='BS', rot=(3,0,0), rot90 = BlockType(0x0d, "StoneStair", direction='BE')),  # Non official
            BlockType(0x0d, "StoneStair", direction='BE', rot=(3,0,1), rot90 = BlockType(0x0e, "StoneStair", direction='BN')),
            BlockType(0x0e, "StoneStair", direction='BN', rot=(3,0,2), rot90 = BlockType(0x0f, "StoneStair", direction='BW')),
            BlockType(0x0f, "StoneStair", direction='BW', rot=(3,0,3), rot90 = BlockType(0x0c, "StoneStair", direction='BS')),

            BlockType(0x10, "StoneStair", direction='NE', rot=(0,0,1), rot90 = BlockType(0x11, "StoneStair", direction='NW')),  # Official
            BlockType(0x11, "StoneStair", direction='NW', rot=(0,1,1), rot90 = BlockType(0x12, "StoneStair", direction='SW')),
            BlockType(0x12, "StoneStair", direction='SW', rot=(0,2,1), rot90 = BlockType(0x13, "StoneStair", direction='SE')),
            BlockType(0x13, "StoneStair", direction='SE', rot=(0,3,1), rot90 = BlockType(0x10, "StoneStair", direction='NE')),

            BlockType(0x14, "StoneStair", direction='NW', rot=(0,0,3), rot90 = BlockType(0x15, "StoneStair", direction='SW')),  # Non official
            BlockType(0x15, "StoneStair", direction='SW', rot=(0,1,3), rot90 = BlockType(0x16, "StoneStair", direction='SE')),
            BlockType(0x16, "StoneStair", direction='SE', rot=(0,2,3), rot90 = BlockType(0x17, "StoneStair", direction='NE')),
            BlockType(0x17, "StoneStair", direction='NE', rot=(0,3,3), rot90 = BlockType(0x14, "StoneStair", direction='NW')),
        ])
        self.STONE_WEDGE = BlockType(7, "StoneWedge", subtypes=[
            BlockType(0x00, "StoneWedge", direction='BN', rot=(0,0,0), rot90=BlockType(0x01, "StoneWedge", direction='BW')),  # Official
            BlockType(0x01, "StoneWedge", direction='BW', rot=(0,1,0), rot90=BlockType(0x02, "StoneWedge", direction='BS')),
            BlockType(0x02, "StoneWedge", direction='BS', rot=(0,2,0), rot90=BlockType(0x03, "StoneWedge", direction='BE')),
            BlockType(0x03, "StoneWedge", direction='BE', rot=(0,3,0), rot90=BlockType(0x00, "StoneWedge", direction='BN')),

            BlockType(0x04, "StoneWedge", direction='TN', rot=(1,0,0), rot90=BlockType(0x05, "StoneWedge", direction='TW')),  # Official
            BlockType(0x05, "StoneWedge", direction='TW', rot=(1,0,3), rot90=BlockType(0x06, "StoneWedge", direction='TS')),
            BlockType(0x06, "StoneWedge", direction='TS', rot=(1,0,2), rot90=BlockType(0x07, "StoneWedge", direction='TE')),
            BlockType(0x07, "StoneWedge", direction='TE', rot=(1,0,1), rot90=BlockType(0x04, "StoneWedge", direction='TN')),

            BlockType(0x08, "StoneWedge", direction='TS', rot=(2,0,0), rot90=BlockType(0x09, "StoneWedge", direction='TE')),  # Non official
            BlockType(0x09, "StoneWedge", direction='TE', rot=(2,3,0), rot90=BlockType(0x0a, "StoneWedge", direction='TN')),
            BlockType(0x0a, "StoneWedge", direction='TN', rot=(2,2,0), rot90=BlockType(0x0b, "StoneWedge", direction='TW')),
            BlockType(0x0b, "StoneWedge", direction='TW', rot=(2,1,0), rot90=BlockType(0x08, "StoneWedge", direction='TS')),

            BlockType(0x0c, "StoneWedge", direction='BS', rot=(3,0,0), rot90=BlockType(0x0d, "StoneWedge", direction='BE')),  # Non official
            BlockType(0x0d, "StoneWedge", direction='BE', rot=(3,0,1), rot90=BlockType(0x0e, "StoneWedge", direction='BN')),
            BlockType(0x0e, "StoneWedge", direction='BN', rot=(3,0,2), rot90=BlockType(0x0f, "StoneWedge", direction='BW')),
            BlockType(0x0f, "StoneWedge", direction='BW', rot=(3,0,3), rot90=BlockType(0x0c, "StoneWedge", direction='BS')),

            BlockType(0x10, "StoneWedge", direction='NE', rot=(0,0,1), rot90=BlockType(0x11, "StoneWedge", direction='NW')),  # Official
            BlockType(0x11, "StoneWedge", direction='NW', rot=(0,1,1), rot90=BlockType(0x12, "StoneWedge", direction='SW')),
            BlockType(0x12, "StoneWedge", direction='SW', rot=(0,2,1), rot90=BlockType(0x13, "StoneWedge", direction='SE')),
            BlockType(0x13, "StoneWedge", direction='SE', rot=(0,3,1), rot90=BlockType(0x10, "StoneWedge", direction='NE')),

            BlockType(0x14, "StoneWedge", direction='NW', rot=(0,0,3), rot90=BlockType(0x15, "StoneWedge", direction='SW')),  # Non official
            BlockType(0x15, "StoneWedge", direction='SW', rot=(0,1,3), rot90=BlockType(0x16, "StoneWedge", direction='SE')),
            BlockType(0x16, "StoneWedge", direction='SE', rot=(0,2,3), rot90=BlockType(0x17, "StoneWedge", direction='NE')),
            BlockType(0x17, "StoneWedge", direction='NE', rot=(0,3,3), rot90=BlockType(0x14, "StoneWedge", direction='NW')),
        ])
        self.WATER = BlockType(11, "Water")
        self.GRASS = BlockType(12, "Grass")
        self.B_BOT = BlockType(15, "B-bot", subtypes=[
            BlockType(0x00, "B-bot", direction='S', rot=(0,0,0), rot90=BlockType(0x01, "B-bot", direction='E')),
            BlockType(0x01, "B-bot", direction='E', rot=(0,1,0), rot90=BlockType(0x02, "B-bot", direction='N')),
            BlockType(0x02, "B-bot", direction='N', rot=(0,2,0), rot90=BlockType(0x03, "B-bot", direction='W')),
            BlockType(0x03, "B-bot", direction='W', rot=(0,3,0), rot90=BlockType(0x00, "B-bot", direction='S')),
        ])
        self.ZAPPER = BlockType(16, "Zapper", subtypes=[
            BlockType(0x00, "Zapper", direction="BT", rot=(0,0,0)),  # Only this one is official...
            BlockType(0x01, "Zapper", direction="BT", rot=(0,1,0)),
            BlockType(0x02, "Zapper", direction="BT", rot=(0,2,0)),
            BlockType(0x03, "Zapper", direction="BT", rot=(0,3,0)),

            BlockType(0x04, "Zapper", direction="NS", rot=(1,0,0), rot90=BlockType(0x05, "Zapper", direction="WE")),
            BlockType(0x05, "Zapper", direction="WE", rot=(1,0,3), rot90=BlockType(0x06, "Zapper", direction="SN")),
            BlockType(0x06, "Zapper", direction="SN", rot=(1,0,2), rot90=BlockType(0x07, "Zapper", direction="EW")),
            BlockType(0x07, "Zapper", direction="EW", rot=(1,0,1), rot90=BlockType(0x04, "Zapper", direction="NS")),

            BlockType(0x08, "Zapper", direction="TB", rot=(2,0,0)),
            BlockType(0x09, "Zapper", direction="TB", rot=(2,3,0)),
            BlockType(0x0a, "Zapper", direction="TB", rot=(2,2,0)),
            BlockType(0x0b, "Zapper", direction="TB", rot=(2,1,0)),

            BlockType(0x0c, "Zapper", direction="SN", rot=(3,0,0), rot90=BlockType(0x0d, "Zapper", direction="EW")),
            BlockType(0x0d, "Zapper", direction="EW", rot=(3,0,1), rot90=BlockType(0x0e, "Zapper", direction="NS")),
            BlockType(0x0e, "Zapper", direction="NS", rot=(3,0,2), rot90=BlockType(0x0f, "Zapper", direction="WE")),
            BlockType(0x0f, "Zapper", direction="WE", rot=(3,0,3), rot90=BlockType(0x0c, "Zapper", direction="SN")),

            BlockType(0x10, "Zapper", direction="EW", rot=(0,0,1), rot90=BlockType(0x11, "Zapper", direction="NS")),
            BlockType(0x11, "Zapper", direction="NS", rot=(0,1,1), rot90=BlockType(0x12, "Zapper", direction="WE")),
            BlockType(0x12, "Zapper", direction="WE", rot=(0,2,1), rot90=BlockType(0x13, "Zapper", direction="SN")),
            BlockType(0x13, "Zapper", direction="SN", rot=(0,3,1), rot90=BlockType(0x10, "Zapper", direction="EW")),

            BlockType(0x14, "Zapper", direction="WE", rot=(0,0,3), rot90=BlockType(0x15, "Zapper", direction="SN")),
            BlockType(0x15, "Zapper", direction="SN", rot=(0,1,3), rot90=BlockType(0x16, "Zapper", direction="EW")),
            BlockType(0x16, "Zapper", direction="EW", rot=(0,2,3), rot90=BlockType(0x17, "Zapper", direction="NS")),
            BlockType(0x17, "Zapper", direction="NS", rot=(0,3,3), rot90=BlockType(0x14, "Zapper", direction="WE")),
        ])
        self.DRAGGABLE = BlockType(17, "Draggable")
        self.DESERT = BlockType(18, "Desert")
        self.MOTOR = BlockType(22, "Motor", subtypes=[
            BlockType(0x00, "Motor", direction='S', rot=(0,0,0), rot90=BlockType(0x01, "Motor", direction='E')),  # Official
            BlockType(0x01, "Motor", direction='E', rot=(0,1,0), rot90=BlockType(0x02, "Motor", direction='N')),  # Official
            BlockType(0x02, "Motor", direction='N', rot=(0,2,0), rot90=BlockType(0x03, "Motor", direction='W')),  # Official
            BlockType(0x03, "Motor", direction='W', rot=(0,3,0), rot90=BlockType(0x00, "Motor", direction='S')),  # Official

            BlockType(0x04, "Motor", direction='D', rot=(1,0,0), rot90=BlockType(0x05, "Motor", direction='D')),  # Official
            BlockType(0x05, "Motor", direction='D', rot=(1,0,3), rot90=BlockType(0x06, "Motor", direction='D')),
            BlockType(0x06, "Motor", direction='D', rot=(1,0,2), rot90=BlockType(0x07, "Motor", direction='D')),
            BlockType(0x07, "Motor", direction='D', rot=(1,0,1), rot90=BlockType(0x04, "Motor", direction='D')),

            BlockType(0x08, "Motor", direction='N', rot=(2,0,0), rot90=BlockType(0x09, "Motor", direction='W')),
            BlockType(0x09, "Motor", direction='W', rot=(2,3,0), rot90=BlockType(0x0a, "Motor", direction='S')),
            BlockType(0x0a, "Motor", direction='S', rot=(2,2,0), rot90=BlockType(0x0b, "Motor", direction='E')),
            BlockType(0x0b, "Motor", direction='E', rot=(2,1,0), rot90=BlockType(0x08, "Motor", direction='N')),

            BlockType(0x0c, "Motor", direction='U', rot=(3,0,0), rot90=BlockType(0x0d, "Motor", direction='U')),  # Official
            BlockType(0x0d, "Motor", direction='U', rot=(3,0,1), rot90=BlockType(0x0e, "Motor", direction='U')),
            BlockType(0x0e, "Motor", direction='U', rot=(3,0,2), rot90=BlockType(0x0f, "Motor", direction='U')),
            BlockType(0x0f, "Motor", direction='U', rot=(3,0,3), rot90=BlockType(0x0c, "Motor", direction='U')),

            BlockType(0x10, "Motor", direction='S', rot=(0,0,1), rot90=BlockType(0x11, "Motor", direction='E')),
            BlockType(0x11, "Motor", direction='E', rot=(0,1,1), rot90=BlockType(0x12, "Motor", direction='N')),
            BlockType(0x12, "Motor", direction='N', rot=(0,2,1), rot90=BlockType(0x13, "Motor", direction='W')),
            BlockType(0x13, "Motor", direction='W', rot=(0,3,1), rot90=BlockType(0x10, "Motor", direction='S')),

            BlockType(0x14, "Motor", direction='S', rot=(0,0,3), rot90=BlockType(0x15, "Motor", direction='E')),
            BlockType(0x15, "Motor", direction='E', rot=(0,1,3), rot90=BlockType(0x16, "Motor", direction='N')),
            BlockType(0x16, "Motor", direction='N', rot=(0,2,3), rot90=BlockType(0x17, "Motor", direction='W')),
            BlockType(0x17, "Motor", direction='W', rot=(0,3,3), rot90=BlockType(0x14, "Motor", direction='S')),
        ])
        self.METAL = BlockType(25, "Metal")
        self.R_BOT = BlockType(26, "R-bot", subtypes=[
            BlockType(0x00, "R-bot", direction='S', rot=(0,0,0), rot90=BlockType(0x01, "R-bot", direction='E')),
            BlockType(0x01, "R-bot", direction='E', rot=(0,1,0), rot90=BlockType(0x02, "R-bot", direction='N')),
            BlockType(0x02, "R-bot", direction='N', rot=(0,2,0), rot90=BlockType(0x03, "R-bot", direction='W')),
            BlockType(0x03, "R-bot", direction='W', rot=(0,3,0), rot90=BlockType(0x00, "R-bot", direction='S')),
        ])
        self.EYE = BlockType(27, "Eye")
        self.CURVED_RAIL = BlockType(30,"CurvedRail", subtypes=[
            BlockType(0x00, "CurvedRail", direction='SE', rot=(0,0,0), rot90=BlockType(0x01, "CurvedRail", direction='NE')),  # Official
            BlockType(0x01, "CurvedRail", direction='NE', rot=(0,1,0), rot90=BlockType(0x02, "CurvedRail", direction='NW')),
            BlockType(0x02, "CurvedRail", direction='NW', rot=(0,2,0), rot90=BlockType(0x03, "CurvedRail", direction='SW')),
            BlockType(0x03, "CurvedRail", direction='SW', rot=(0,3,0), rot90=BlockType(0x00, "CurvedRail", direction='SE')),

            BlockType(0x04, "CurvedRail", direction='BE', rot=(1,0,0), rot90=BlockType(0x05, "CurvedRail", direction='BN')),  # Official
            BlockType(0x05, "CurvedRail", direction='BN', rot=(1,0,3), rot90=BlockType(0x06, "CurvedRail", direction='BW')),
            BlockType(0x06, "CurvedRail", direction='BW', rot=(1,0,2), rot90=BlockType(0x07, "CurvedRail", direction='BS')),
            BlockType(0x07, "CurvedRail", direction='BS', rot=(1,0,1), rot90=BlockType(0x04, "CurvedRail", direction='BE')),

            BlockType(0x08, "CurvedRail", direction='NE', rot=(2,0,0), rot90 = BlockType(0x09, "CurvedRail", direction='NW')),  # Non official
            BlockType(0x09, "CurvedRail", direction='NW', rot=(2,3,0), rot90 = BlockType(0x0a, "CurvedRail", direction='SW')),
            BlockType(0x0a, "CurvedRail", direction='SW', rot=(2,2,0), rot90 = BlockType(0x0b, "CurvedRail", direction='SE')),
            BlockType(0x0b, "CurvedRail", direction='SE', rot=(2,1,0), rot90 = BlockType(0x08, "CurvedRail", direction='NE')),

            BlockType(0x0c, "CurvedRail", direction='TE', rot=(3,0,0), rot90 = BlockType(0x0d, "CurvedRail", direction='TN')),  # Non official
            BlockType(0x0d, "CurvedRail", direction='TN', rot=(3,0,1), rot90 = BlockType(0x0e, "CurvedRail", direction='TW')),
            BlockType(0x0e, "CurvedRail", direction='TW', rot=(3,0,2), rot90 = BlockType(0x0f, "CurvedRail", direction='TS')),
            BlockType(0x0f, "CurvedRail", direction='TS', rot=(3,0,3), rot90 = BlockType(0x0c, "CurvedRail", direction='TE')),

            BlockType(0x10, "CurvedRail", direction='TS', rot=(0,0,1), rot90=BlockType(0x11, "CurvedRail", direction='TE')),  # Official
            BlockType(0x11, "CurvedRail", direction='TE', rot=(0,1,1), rot90=BlockType(0x12, "CurvedRail", direction='TN')),
            BlockType(0x12, "CurvedRail", direction='TN', rot=(0,2,1), rot90=BlockType(0x13, "CurvedRail", direction='TW')),
            BlockType(0x13, "CurvedRail", direction='TW', rot=(0,3,1), rot90=BlockType(0x10, "CurvedRail", direction='TS')),

            BlockType(0x14, "CurvedRail", direction='BS', rot=(0,0,3), rot90 = BlockType(0x15, "CurvedRail", direction='BE')),  # Non official
            BlockType(0x15, "CurvedRail", direction='BE', rot=(0,1,3), rot90 = BlockType(0x16, "CurvedRail", direction='BN')),
            BlockType(0x16, "CurvedRail", direction='BN', rot=(0,2,3), rot90 = BlockType(0x17, "CurvedRail", direction='BW')),
            BlockType(0x17, "CurvedRail", direction='BW', rot=(0,3,3), rot90 = BlockType(0x14, "CurvedRail", direction='BS')),
        ])
        self.METAL_HALF_PILLAR = BlockType(32, "MetalHalfPillar", subtypes=[
            BlockType(0x00, "MetalHalfPillar", direction='YS', rot=(0,0,0), rot90=BlockType(0x01, "MetalHalfPillar", direction='YE')),  # Official
            BlockType(0x01, "MetalHalfPillar", direction='YE', rot=(0,1,0), rot90=BlockType(0x02, "MetalHalfPillar", direction='YN')),
            BlockType(0x02, "MetalHalfPillar", direction='YN', rot=(0,2,0), rot90=BlockType(0x03, "MetalHalfPillar", direction='YW')),
            BlockType(0x03, "MetalHalfPillar", direction='YW', rot=(0,3,0), rot90=BlockType(0x00, "MetalHalfPillar", direction='YS')),

            BlockType(0x04, "MetalHalfPillar", direction='ZB', rot=(1,0,0), rot90=BlockType(0x07, "MetalHalfPillar", direction='XB')),  # Non official

            BlockType(0x05, "MetalHalfPillar", direction='XB', rot=(1,0,3), rot90=BlockType(0x06, "MetalHalfPillar", direction='ZB')),  # official
            BlockType(0x06, "MetalHalfPillar", direction='ZB', rot=(1,0,2), rot90=BlockType(0x05, "MetalHalfPillar", direction='XB')),

            BlockType(0x07, "MetalHalfPillar", direction='XB', rot=(1,0,1), rot90=BlockType(0x04, "MetalHalfPillar", direction='ZB')),  # Non official

            BlockType(0x08, "MetalHalfPillar", direction='YN', rot=(2,0,0), rot90=BlockType(0x09, "MetalHalfPillar", direction='YW')),  # Non official
            BlockType(0x09, "MetalHalfPillar", direction='YW', rot=(2,3,0), rot90=BlockType(0x0a, "MetalHalfPillar", direction='YS')),
            BlockType(0x0a, "MetalHalfPillar", direction='YS', rot=(2,2,0), rot90=BlockType(0x0b, "MetalHalfPillar", direction='YE')),
            BlockType(0x0b, "MetalHalfPillar", direction='YE', rot=(2,1,0), rot90=BlockType(0x08, "MetalHalfPillar", direction='YN')),

            BlockType(0x0c, "MetalHalfPillar", direction='ZT', rot=(3,0,0), rot90=BlockType(0x0f, "MetalHalfPillar", direction='XT')),  # official

            BlockType(0x0d, "MetalHalfPillar", direction='XT', rot=(3,0,1), rot90=BlockType(0x0e, "MetalHalfPillar", direction='ZT')),  # Non official
            BlockType(0x0e, "MetalHalfPillar", direction='ZT', rot=(3,0,2), rot90=BlockType(0x0f, "MetalHalfPillar", direction='XT')),

            BlockType(0x0f, "MetalHalfPillar", direction='XT', rot=(3,0,3), rot90=BlockType(0x0c, "MetalHalfPillar", direction='ZT')),  # official

            BlockType(0x10, "MetalHalfPillar", direction='XS', rot=(0,0,1), rot90=BlockType(0x11, "MetalHalfPillar", direction='ZE')),  # Non Official
            BlockType(0x11, "MetalHalfPillar", direction='ZE', rot=(0,1,1), rot90=BlockType(0x12, "MetalHalfPillar", direction='XN')),
            BlockType(0x12, "MetalHalfPillar", direction='XN', rot=(0,2,1), rot90=BlockType(0x13, "MetalHalfPillar", direction='ZW')),
            BlockType(0x13, "MetalHalfPillar", direction='ZW', rot=(0,3,1), rot90=BlockType(0x10, "MetalHalfPillar", direction='XS')),

            BlockType(0x14, "MetalHalfPillar", direction='XS', rot=(0,0,3), rot90=BlockType(0x15, "MetalHalfPillar", direction='ZE')),  # official
            BlockType(0x15, "MetalHalfPillar", direction='ZE', rot=(0,1,3), rot90=BlockType(0x16, "MetalHalfPillar", direction='XN')),
            BlockType(0x16, "MetalHalfPillar", direction='XN', rot=(0,2,3), rot90=BlockType(0x17, "MetalHalfPillar", direction='ZW')),
            BlockType(0x17, "MetalHalfPillar", direction='ZW', rot=(0,3,3), rot90=BlockType(0x14, "MetalHalfPillar", direction='XS')),
        ])
        self.RAIL = BlockType(33, "Rail", subtypes=[
            BlockType(0x00, "Rail", direction='X', rot=(0,0,1), rot90=BlockType(0x01, "Rail", direction='Z')),  # Official
            BlockType(0x01, "Rail", direction='Z', rot=(0,1,1), rot90=BlockType(0x02, "Rail", direction='X')),
            BlockType(0x02, "Rail", direction='X', rot=(0,2,1), rot90=BlockType(0x03, "Rail", direction='Z')),
            BlockType(0x03, "Rail", direction='Z', rot=(0,3,1), rot90=BlockType(0x00, "Rail", direction='X')),  # Official

            BlockType(0x04, "Rail", direction='X', rot=(1,0,1), rot90=BlockType(0x05, "Rail", direction='Z')),
            BlockType(0x05, "Rail", direction='Z', rot=(1,0,2), rot90=BlockType(0x06, "Rail", direction='X')),
            BlockType(0x06, "Rail", direction='X', rot=(1,0,3), rot90=BlockType(0x07, "Rail", direction='Z')),
            BlockType(0x07, "Rail", direction='Z', rot=(1,0,0), rot90=BlockType(0x04, "Rail", direction='X')),

            BlockType(0x08, "Rail", direction='X', rot=(0,0,3), rot90=BlockType(0x09, "Rail", direction='Z')),
            BlockType(0x09, "Rail", direction='Z', rot=(0,1,3), rot90=BlockType(0x0a, "Rail", direction='X')),
            BlockType(0x0a, "Rail", direction='X', rot=(0,2,3), rot90=BlockType(0x0b, "Rail", direction='Z')),
            BlockType(0x0b, "Rail", direction='Z', rot=(0,3,3), rot90=BlockType(0x08, "Rail", direction='X')),

            BlockType(0x0c, "Rail", direction='X', rot=(3,0,1), rot90=BlockType(0x0d, "Rail", direction='Z')),
            BlockType(0x0d, "Rail", direction='Z', rot=(3,0,2), rot90=BlockType(0x0e, "Rail", direction='X')),
            BlockType(0x0e, "Rail", direction='X', rot=(3,0,3), rot90=BlockType(0x0f, "Rail", direction='Z')),
            BlockType(0x0f, "Rail", direction='Z', rot=(3,0,0), rot90=BlockType(0x0c, "Rail", direction='X')),

            BlockType(0x10, "Rail", direction='Y', rot=(0,0,0), rot90=BlockType(0x11, "Rail", direction='Y')),
            BlockType(0x11, "Rail", direction='Y', rot=(0,1,0), rot90=BlockType(0x12, "Rail", direction='Y')),
            BlockType(0x12, "Rail", direction='Y', rot=(0,2,0), rot90=BlockType(0x13, "Rail", direction='Y')),
            BlockType(0x13, "Rail", direction='Y', rot=(0,3,0), rot90=BlockType(0x10, "Rail", direction='Y')),

            BlockType(0x14, "Rail", direction='Y', rot=(2,0,0), rot90=BlockType(0x15, "Rail", direction='Y')),  # Official
            BlockType(0x15, "Rail", direction='Y', rot=(2,3,0), rot90=BlockType(0x16, "Rail", direction='Y')),
            BlockType(0x16, "Rail", direction='Y', rot=(2,2,0), rot90=BlockType(0x17, "Rail", direction='Y')),
            BlockType(0x17, "Rail", direction='Y', rot=(2,1,0), rot90=BlockType(0x14, "Rail", direction='Y')),


            # BlockType(0x00, "Rail(X)", rot=(0,0,0), rot90 = BlockType(0x03, "Rail(Z)")),
            # BlockType(0x03, "Rail(Z)", rot=(0,0,1), rot90 = BlockType(0x00, "Rail(X)")),
            # BlockType(0x14, "Rail(Y)", rot=(0,1,0)),
        ])
        self.STONE_PILLAR = BlockType(35, "StonePillar", subtypes=[
            BlockType(0x00, "StonePillar", direction='Y', rot=(0,0,0), rot90=BlockType(0x01, "StonePillar", direction='Y')),  # Official
            BlockType(0x01, "StonePillar", direction='Y', rot=(0,1,0), rot90=BlockType(0x02, "StonePillar", direction='Y')),
            BlockType(0x02, "StonePillar", direction='Y', rot=(0,2,0), rot90=BlockType(0x03, "StonePillar", direction='Y')),
            BlockType(0x03, "StonePillar", direction='Y', rot=(0,3,0), rot90=BlockType(0x00, "StonePillar", direction='Y')),

            BlockType(0x04, "StonePillar", direction='Z', rot=(1,0,0), rot90=BlockType(0x05, "StonePillar", direction='X')),
            BlockType(0x05, "StonePillar", direction='X', rot=(1,0,3), rot90=BlockType(0x06, "StonePillar", direction='Z')),
            BlockType(0x06, "StonePillar", direction='Z', rot=(1,0,2), rot90=BlockType(0x07, "StonePillar", direction='X')),
            BlockType(0x07, "StonePillar", direction='X', rot=(1,0,1), rot90=BlockType(0x04, "StonePillar", direction='Z')),

            BlockType(0x08, "StonePillar", direction='Y', rot=(2,0,0), rot90 = BlockType(0x09, "StonePillar", direction='Y')),
            BlockType(0x09, "StonePillar", direction='Y', rot=(2,3,0), rot90 = BlockType(0x0a, "StonePillar", direction='Y')),
            BlockType(0x0a, "StonePillar", direction='Y', rot=(2,2,0), rot90 = BlockType(0x0b, "StonePillar", direction='Y')),
            BlockType(0x0b, "StonePillar", direction='Y', rot=(2,1,0), rot90 = BlockType(0x08, "StonePillar", direction='Y')),

            BlockType(0x0c, "StonePillar", direction='Z', rot=(3,0,0), rot90 = BlockType(0x0d, "StonePillar", direction='X')),  # Official
            BlockType(0x0d, "StonePillar", direction='X', rot=(3,0,1), rot90 = BlockType(0x0e, "StonePillar", direction='Z')),
            BlockType(0x0e, "StonePillar", direction='Z', rot=(3,0,2), rot90 = BlockType(0x0f, "StonePillar", direction='X')),
            BlockType(0x0f, "StonePillar", direction='X', rot=(3,0,3), rot90 = BlockType(0x0c, "StonePillar", direction='Z')),

            BlockType(0x10, "StonePillar", direction='X', rot=(0,0,1), rot90=BlockType(0x11, "StonePillar", direction='Z')),
            BlockType(0x11, "StonePillar", direction='Z', rot=(0,1,1), rot90=BlockType(0x12, "StonePillar", direction='X')),
            BlockType(0x12, "StonePillar", direction='X', rot=(0,2,1), rot90=BlockType(0x13, "StonePillar", direction='Z')),
            BlockType(0x13, "StonePillar", direction='Z', rot=(0,3,1), rot90=BlockType(0x10, "StonePillar", direction='X')),

            BlockType(0x14, "StonePillar", direction='X', rot=(0,0,3), rot90 = BlockType(0x15, "StonePillar", direction='Z')),  # Official
            BlockType(0x15, "StonePillar", direction='Z', rot=(0,1,3), rot90 = BlockType(0x16, "StonePillar", direction='X')),
            BlockType(0x16, "StonePillar", direction='X', rot=(0,2,3), rot90 = BlockType(0x17, "StonePillar", direction='Z')),
            BlockType(0x17, "StonePillar", direction='Z', rot=(0,3,3), rot90 = BlockType(0x14, "StonePillar", direction='X')),

            # BlockType(0x00, "StonePillar(Y)", "SP", rot=(0,0,0)),
            # BlockType(0x0c, "StonePillar(Z)", "SP", rot=(1,0,0), rot90 = BlockType(0x14, "StonePillar(X)", "SP")),
            # BlockType(0x14, "StonePillar(X)", "SP", rot=(0,0,1), rot90 = BlockType(0x0c, "StonePillar(Z)", "SP")),
        ])
        self.BALL = BlockType(37, "Ball")
        self.METAL_PILLAR = BlockType(39, "MetalPillar", subtypes=[
            BlockType(0x00, "MetalPillar", direction='Y', rot=(0,0,0), rot90=BlockType(0x01, "MetalPillar", direction='Y')),  # Official
            BlockType(0x01, "MetalPillar", direction='Y', rot=(0,1,0), rot90=BlockType(0x02, "MetalPillar", direction='Y')),
            BlockType(0x02, "MetalPillar", direction='Y', rot=(0,2,0), rot90=BlockType(0x03, "MetalPillar", direction='Y')),
            BlockType(0x03, "MetalPillar", direction='Y', rot=(0,3,0), rot90=BlockType(0x00, "MetalPillar", direction='Y')),

            BlockType(0x04, "MetalPillar", direction='Z', rot=(1,0,0), rot90=BlockType(0x05, "MetalPillar", direction='X')),
            BlockType(0x05, "MetalPillar", direction='X', rot=(1,0,3), rot90=BlockType(0x06, "MetalPillar", direction='Z')),
            BlockType(0x06, "MetalPillar", direction='Z', rot=(1,0,2), rot90=BlockType(0x07, "MetalPillar", direction='X')),
            BlockType(0x07, "MetalPillar", direction='X', rot=(1,0,1), rot90=BlockType(0x04, "MetalPillar", direction='Z')),

            BlockType(0x08, "MetalPillar", direction='Y', rot=(2,0,0), rot90 = BlockType(0x09, "MetalPillar", direction='Y')),
            BlockType(0x09, "MetalPillar", direction='Y', rot=(2,3,0), rot90 = BlockType(0x0a, "MetalPillar", direction='Y')),
            BlockType(0x0a, "MetalPillar", direction='Y', rot=(2,2,0), rot90 = BlockType(0x0b, "MetalPillar", direction='Y')),
            BlockType(0x0b, "MetalPillar", direction='Y', rot=(2,1,0), rot90 = BlockType(0x08, "MetalPillar", direction='Y')),

            BlockType(0x0c, "MetalPillar", direction='Z', rot=(3,0,0), rot90 = BlockType(0x0d, "MetalPillar", direction='X')),  # Official
            BlockType(0x0d, "MetalPillar", direction='X', rot=(3,0,1), rot90 = BlockType(0x0e, "MetalPillar", direction='Z')),
            BlockType(0x0e, "MetalPillar", direction='Z', rot=(3,0,2), rot90 = BlockType(0x0f, "MetalPillar", direction='X')),
            BlockType(0x0f, "MetalPillar", direction='X', rot=(3,0,3), rot90 = BlockType(0x0c, "MetalPillar", direction='Z')),

            BlockType(0x10, "MetalPillar", direction='X', rot=(0,0,1), rot90=BlockType(0x11, "MetalPillar", direction='Z')),
            BlockType(0x11, "MetalPillar", direction='Z', rot=(0,1,1), rot90=BlockType(0x12, "MetalPillar", direction='X')),
            BlockType(0x12, "MetalPillar", direction='X', rot=(0,2,1), rot90=BlockType(0x13, "MetalPillar", direction='Z')),
            BlockType(0x13, "MetalPillar", direction='Z', rot=(0,3,1), rot90=BlockType(0x10, "MetalPillar", direction='X')),

            BlockType(0x14, "MetalPillar", direction='X', rot=(0,0,3), rot90 = BlockType(0x15, "MetalPillar", direction='Z')),  # Official
            BlockType(0x15, "MetalPillar", direction='Z', rot=(0,1,3), rot90 = BlockType(0x16, "MetalPillar", direction='X')),
            BlockType(0x16, "MetalPillar", direction='X', rot=(0,2,3), rot90 = BlockType(0x17, "MetalPillar", direction='Z')),
            BlockType(0x17, "MetalPillar", direction='Z', rot=(0,3,3), rot90 = BlockType(0x14, "MetalPillar", direction='X')),
        ])
        self.SLIDER = BlockType(41, "Slider", subtypes=[
            BlockType(0x00, "Slider", direction='X', rot=(0,0,1), rot90=BlockType(0x01, "Slider", direction='Z')),  # Official
            BlockType(0x01, "Slider", direction='Z', rot=(0,1,1), rot90=BlockType(0x02, "Slider", direction='X')),
            BlockType(0x02, "Slider", direction='X', rot=(0,2,1), rot90=BlockType(0x03, "Slider", direction='Z')),
            BlockType(0x03, "Slider", direction='Z', rot=(0,3,1), rot90=BlockType(0x00, "Slider", direction='X')),  # Official

            BlockType(0x04, "Slider", direction='X', rot=(1,0,1), rot90=BlockType(0x05, "Slider", direction='Z')),
            BlockType(0x05, "Slider", direction='Z', rot=(1,0,2), rot90=BlockType(0x06, "Slider", direction='X')),
            BlockType(0x06, "Slider", direction='X', rot=(1,0,3), rot90=BlockType(0x07, "Slider", direction='Z')),
            BlockType(0x07, "Slider", direction='Z', rot=(1,0,0), rot90=BlockType(0x04, "Slider", direction='X')),

            BlockType(0x08, "Slider", direction='X', rot=(0,0,3), rot90=BlockType(0x09, "Slider", direction='Z')),
            BlockType(0x09, "Slider", direction='Z', rot=(0,1,3), rot90=BlockType(0x0a, "Slider", direction='X')),
            BlockType(0x0a, "Slider", direction='X', rot=(0,2,3), rot90=BlockType(0x0b, "Slider", direction='Z')),
            BlockType(0x0b, "Slider", direction='Z', rot=(0,3,3), rot90=BlockType(0x08, "Slider", direction='X')),

            BlockType(0x0c, "Slider", direction='X', rot=(3,0,1), rot90=BlockType(0x0d, "Slider", direction='Z')),
            BlockType(0x0d, "Slider", direction='Z', rot=(3,0,2), rot90=BlockType(0x0e, "Slider", direction='X')),
            BlockType(0x0e, "Slider", direction='X', rot=(3,0,3), rot90=BlockType(0x0f, "Slider", direction='Z')),
            BlockType(0x0f, "Slider", direction='Z', rot=(3,0,0), rot90=BlockType(0x0c, "Slider", direction='X')),

            BlockType(0x10, "Slider", direction='Y', rot=(0,0,0), rot90=BlockType(0x11, "Slider", direction='Y')),
            BlockType(0x11, "Slider", direction='Y', rot=(0,1,0), rot90=BlockType(0x12, "Slider", direction='Y')),
            BlockType(0x12, "Slider", direction='Y', rot=(0,2,0), rot90=BlockType(0x13, "Slider", direction='Y')),
            BlockType(0x13, "Slider", direction='Y', rot=(0,3,0), rot90=BlockType(0x10, "Slider", direction='Y')),

            BlockType(0x14, "Slider", direction='Y', rot=(2,0,0), rot90=BlockType(0x15, "Slider", direction='Y')),  # Official
            BlockType(0x15, "Slider", direction='Y', rot=(2,3,0), rot90=BlockType(0x16, "Slider", direction='Y')),
            BlockType(0x16, "Slider", direction='Y', rot=(2,2,0), rot90=BlockType(0x17, "Slider", direction='Y')),
            BlockType(0x17, "Slider", direction='Y', rot=(2,1,0), rot90=BlockType(0x14, "Slider", direction='Y')),
        ])
        self.FENCE = BlockType(43, "Fence", subtypes=[
            BlockType(0x00, "Fence", direction='XY', rot=(0,0,0), rot90=BlockType(0x01, "Fence", direction='ZY')),  # Official
            BlockType(0x01, "Fence", direction='ZY', rot=(0,1,0), rot90=BlockType(0x02, "Fence", direction='XY')),
            BlockType(0x02, "Fence", direction='XY', rot=(0,2,0), rot90=BlockType(0x03, "Fence", direction='ZY')),
            BlockType(0x03, "Fence", direction='ZY', rot=(0,3,0), rot90=BlockType(0x00, "Fence", direction='XY')),  # Official

            BlockType(0x04, "Fence", direction='XZ', rot=(1,0,0), rot90=BlockType(0x05, "Fence", direction='ZX')),  # Official
            BlockType(0x05, "Fence", direction='ZX', rot=(1,0,3), rot90=BlockType(0x06, "Fence", direction='XZ')),
            BlockType(0x06, "Fence", direction='XZ', rot=(1,0,2), rot90=BlockType(0x07, "Fence", direction='ZX')),
            BlockType(0x07, "Fence", direction='ZX', rot=(1,0,1), rot90=BlockType(0x04, "Fence", direction='XZ')),  # Official

            BlockType(0x08, "Fence", direction='XY', rot=(2,0,0), rot90=BlockType(0x09, "Fence", direction='ZY')),
            BlockType(0x09, "Fence", direction='ZY', rot=(2,3,0), rot90=BlockType(0x0a, "Fence", direction='XY')),
            BlockType(0x0a, "Fence", direction='XY', rot=(2,2,0), rot90=BlockType(0x0b, "Fence", direction='ZY')),
            BlockType(0x0b, "Fence", direction='ZY', rot=(2,1,0), rot90=BlockType(0x08, "Fence", direction='XY')),

            BlockType(0x0c, "Fence", direction='XZ', rot=(3,0,0), rot90=BlockType(0x0d, "Fence", direction='ZX')),
            BlockType(0x0d, "Fence", direction='ZX', rot=(3,0,1), rot90=BlockType(0x0e, "Fence", direction='XZ')),
            BlockType(0x0e, "Fence", direction='XZ', rot=(3,0,2), rot90=BlockType(0x0f, "Fence", direction='ZX')),
            BlockType(0x0f, "Fence", direction='ZX', rot=(3,0,3), rot90=BlockType(0x0c, "Fence", direction='XZ')),

            BlockType(0x10, "Fence", direction='YX', rot=(0,0,1), rot90=BlockType(0x11, "Fence", direction='YZ')),  # Official
            BlockType(0x11, "Fence", direction='YZ', rot=(0,1,1), rot90=BlockType(0x12, "Fence", direction='YX')),
            BlockType(0x12, "Fence", direction='YX', rot=(0,2,1), rot90=BlockType(0x13, "Fence", direction='YZ')),
            BlockType(0x13, "Fence", direction='YZ', rot=(0,3,1), rot90=BlockType(0x10, "Fence", direction='YX')),  # Official

            BlockType(0x14, "Fence", direction='YX', rot=(0,0,3), rot90=BlockType(0x15, "Fence", direction='YZ')),
            BlockType(0x15, "Fence", direction='YZ', rot=(0,1,3), rot90=BlockType(0x16, "Fence", direction='YX')),
            BlockType(0x16, "Fence", direction='YX', rot=(0,2,3), rot90=BlockType(0x17, "Fence", direction='YZ')),
            BlockType(0x17, "Fence", direction='YZ', rot=(0,3,3), rot90=BlockType(0x14, "Fence", direction='YX')),
        ])

        # Hidden/New blocks
        self.TRASH = BlockType(6, "Trash")

        self.GRASS_WEDGE = BlockType(8, "GrassWedge", subtypes=[
            BlockType(0x00, "GrassWedge", direction='BN', rot=(0,0,0), rot90=BlockType(0x01, "GrassWedge", direction='BW')),  # Official
            BlockType(0x01, "GrassWedge", direction='BW', rot=(0,1,0), rot90=BlockType(0x02, "GrassWedge", direction='BS')),
            BlockType(0x02, "GrassWedge", direction='BS', rot=(0,2,0), rot90=BlockType(0x03, "GrassWedge", direction='BE')),
            BlockType(0x03, "GrassWedge", direction='BE', rot=(0,3,0), rot90=BlockType(0x00, "GrassWedge", direction='BN')),

            BlockType(0x04, "GrassWedge", direction='TN', rot=(1,0,0), rot90=BlockType(0x05, "GrassWedge", direction='TW')),  # Official
            BlockType(0x05, "GrassWedge", direction='TW', rot=(1,0,3), rot90=BlockType(0x06, "GrassWedge", direction='TS')),
            BlockType(0x06, "GrassWedge", direction='TS', rot=(1,0,2), rot90=BlockType(0x07, "GrassWedge", direction='TE')),
            BlockType(0x07, "GrassWedge", direction='TE', rot=(1,0,1), rot90=BlockType(0x04, "GrassWedge", direction='TN')),

            BlockType(0x08, "GrassWedge", direction='TS', rot=(2,0,0), rot90=BlockType(0x09, "GrassWedge", direction='TE')),  # Non official
            BlockType(0x09, "GrassWedge", direction='TE', rot=(2,3,0), rot90=BlockType(0x0a, "GrassWedge", direction='TN')),
            BlockType(0x0a, "GrassWedge", direction='TN', rot=(2,2,0), rot90=BlockType(0x0b, "GrassWedge", direction='TW')),
            BlockType(0x0b, "GrassWedge", direction='TW', rot=(2,1,0), rot90=BlockType(0x08, "GrassWedge", direction='TS')),

            BlockType(0x0c, "GrassWedge", direction='BS', rot=(3,0,0), rot90=BlockType(0x0d, "GrassWedge", direction='BE')),  # Non official
            BlockType(0x0d, "GrassWedge", direction='BE', rot=(3,0,1), rot90=BlockType(0x0e, "GrassWedge", direction='BN')),
            BlockType(0x0e, "GrassWedge", direction='BN', rot=(3,0,2), rot90=BlockType(0x0f, "GrassWedge", direction='BW')),
            BlockType(0x0f, "GrassWedge", direction='BW', rot=(3,0,3), rot90=BlockType(0x0c, "GrassWedge", direction='BS')),

            BlockType(0x10, "GrassWedge", direction='NE', rot=(0,0,1), rot90=BlockType(0x11, "GrassWedge", direction='NW')),  # Official
            BlockType(0x11, "GrassWedge", direction='NW', rot=(0,1,1), rot90=BlockType(0x12, "GrassWedge", direction='SW')),
            BlockType(0x12, "GrassWedge", direction='SW', rot=(0,2,1), rot90=BlockType(0x13, "GrassWedge", direction='SE')),
            BlockType(0x13, "GrassWedge", direction='SE', rot=(0,3,1), rot90=BlockType(0x10, "GrassWedge", direction='NE')),

            BlockType(0x14, "GrassWedge", direction='NW', rot=(0,0,3), rot90=BlockType(0x15, "GrassWedge", direction='SW')),  # Non official
            BlockType(0x15, "GrassWedge", direction='SW', rot=(0,1,3), rot90=BlockType(0x16, "GrassWedge", direction='SE')),
            BlockType(0x16, "GrassWedge", direction='SE', rot=(0,2,3), rot90=BlockType(0x17, "GrassWedge", direction='NE')),
            BlockType(0x17, "GrassWedge", direction='NE', rot=(0,3,3), rot90=BlockType(0x14, "GrassWedge", direction='NW')),
        ])

        self.GOLDEN_BALL = BlockType(9, "GoldenBall")  # tested but can't see the benefit... has been reported to behave weirdly

        self.BUTTON = BlockType(10, "Button", subtypes=[
            BlockType(0x00, "Button", direction='Y', rot=(0, 0, 0), rot90=BlockType(0x01, "Button", direction='Y')),  # Official
            BlockType(0x01, "Button", direction='Y', rot=(0, 1, 0), rot90=BlockType(0x02, "Button", direction='Y')),
            BlockType(0x02, "Button", direction='Y', rot=(0, 2, 0), rot90=BlockType(0x03, "Button", direction='Y')),
            BlockType(0x03, "Button", direction='Y', rot=(0, 3, 0), rot90=BlockType(0x00, "Button", direction='Y')),

            BlockType(0x04, "Button", direction='Z', rot=(1, 0, 0), rot90=BlockType(0x05, "Button", direction='X')),
            BlockType(0x05, "Button", direction='X', rot=(1, 0, 3), rot90=BlockType(0x06, "Button", direction='Z')),
            BlockType(0x06, "Button", direction='Z', rot=(1, 0, 2), rot90=BlockType(0x07, "Button", direction='X')),
            BlockType(0x07, "Button", direction='X', rot=(1, 0, 1), rot90=BlockType(0x04, "Button", direction='Z')),

            BlockType(0x08, "Button", direction='Y', rot=(2, 0, 0), rot90=BlockType(0x09, "Button", direction='Y')),
            BlockType(0x09, "Button", direction='Y', rot=(2, 3, 0), rot90=BlockType(0x0a, "Button", direction='Y')),
            BlockType(0x0a, "Button", direction='Y', rot=(2, 2, 0), rot90=BlockType(0x0b, "Button", direction='Y')),
            BlockType(0x0b, "Button", direction='Y', rot=(2, 1, 0), rot90=BlockType(0x08, "Button", direction='Y')),

            BlockType(0x0c, "Button", direction='Z', rot=(3, 0, 0), rot90=BlockType(0x0d, "Button", direction='X')),  # Official
            BlockType(0x0d, "Button", direction='X', rot=(3, 0, 1), rot90=BlockType(0x0e, "Button", direction='Z')),
            BlockType(0x0e, "Button", direction='Z', rot=(3, 0, 2), rot90=BlockType(0x0f, "Button", direction='X')),
            BlockType(0x0f, "Button", direction='X', rot=(3, 0, 3), rot90=BlockType(0x0c, "Button", direction='Z')),

            BlockType(0x10, "Button", direction='X', rot=(0, 0, 1), rot90=BlockType(0x11, "Button", direction='Z')),
            BlockType(0x11, "Button", direction='Z', rot=(0, 1, 1), rot90=BlockType(0x12, "Button", direction='X')),
            BlockType(0x12, "Button", direction='X', rot=(0, 2, 1), rot90=BlockType(0x13, "Button", direction='Z')),
            BlockType(0x13, "Button", direction='Z', rot=(0, 3, 1), rot90=BlockType(0x10, "Button", direction='X')),

            BlockType(0x14, "Button", direction='X', rot=(0, 0, 3), rot90=BlockType(0x15, "Button", direction='Z')),  # Official
            BlockType(0x15, "Button", direction='Z', rot=(0, 1, 3), rot90=BlockType(0x16, "Button", direction='X')),
            BlockType(0x16, "Button", direction='X', rot=(0, 2, 3), rot90=BlockType(0x17, "Button", direction='Z')),
            BlockType(0x17, "Button", direction='Z', rot=(0, 3, 3), rot90=BlockType(0x14, "Button", direction='X')),
        ])

        self.BRICK_PILLAR = BlockType(13, "BrickPillar", subtypes=[
            BlockType(0x14, "BrickPillar(X)", rot90 = BlockType(0x0c, "BrickPillar(Z)", "SP")),
            BlockType(0x00, "BrickPillar(Y)"),
            BlockType(0x0c, "BrickPillar(Z)", rot90 = BlockType(0x14, "BrickPillar(X)", "SP")),
        ])

        self.STONE_CORNER = BlockType(14, "StoneCorner", subtypes=[
            BlockType(0x00, "StoneCorner", direction='NW', rot=(0,0,0), rot90=BlockType(0x01, "StoneCorner", direction='SW')),  # Official
            BlockType(0x01, "StoneCorner", direction='SW', rot=(0,1,0), rot90=BlockType(0x02, "StoneCorner", direction='SE')),
            BlockType(0x02, "StoneCorner", direction='SE', rot=(0,2,0), rot90=BlockType(0x03, "StoneCorner", direction='NE')),
            BlockType(0x03, "StoneCorner", direction='NE', rot=(0,3,0), rot90=BlockType(0x00, "StoneCorner", direction='NW')),

            BlockType(0x04, "StoneCorner", direction='TW', rot=(1,0,0), rot90=BlockType(0x05, "StoneCorner", direction='TS')),  # Official
            BlockType(0x05, "StoneCorner", direction='TS', rot=(1,0,3), rot90=BlockType(0x06, "StoneCorner", direction='TE')),
            BlockType(0x06, "StoneCorner", direction='TE', rot=(1,0,2), rot90=BlockType(0x07, "StoneCorner", direction='TN')),
            BlockType(0x07, "StoneCorner", direction='TN', rot=(1,0,1), rot90=BlockType(0x04, "StoneCorner", direction='TW')),

            BlockType(0x08, "StoneCorner", direction='SW', rot=(2,0,0), rot90 = BlockType(0x09, "StoneCorner", direction='SE')),  # Non official
            BlockType(0x09, "StoneCorner", direction='SE', rot=(2,0,3), rot90 = BlockType(0x0a, "StoneCorner", direction='NE')),
            BlockType(0x0a, "StoneCorner", direction='NE', rot=(2,0,2), rot90 = BlockType(0x0b, "StoneCorner", direction='NW')),
            BlockType(0x0b, "StoneCorner", direction='NW', rot=(2,0,1), rot90 = BlockType(0x08, "StoneCorner", direction='SW')),

            BlockType(0x0c, "StoneCorner", direction='BW', rot=(3,0,0), rot90 = BlockType(0x0d, "StoneCorner", direction='BS')),  # Non official
            BlockType(0x0d, "StoneCorner", direction='BS', rot=(3,0,1), rot90 = BlockType(0x0e, "StoneCorner", direction='BE')),
            BlockType(0x0e, "StoneCorner", direction='BE', rot=(3,0,2), rot90 = BlockType(0x0f, "StoneCorner", direction='BN')),
            BlockType(0x0f, "StoneCorner", direction='BN', rot=(3,0,3), rot90 = BlockType(0x0c, "StoneCorner", direction='BW')),

            BlockType(0x10, "StoneCorner", direction='BN', rot=(0,0,1), rot90=BlockType(0x11, "StoneCorner", direction='BW')),  # Official
            BlockType(0x11, "StoneCorner", direction='BW', rot=(0,1,1), rot90=BlockType(0x12, "StoneCorner", direction='BS')),
            BlockType(0x12, "StoneCorner", direction='BS', rot=(0,2,1), rot90=BlockType(0x13, "StoneCorner", direction='BE')),
            BlockType(0x13, "StoneCorner", direction='BE', rot=(0,3,1), rot90=BlockType(0x10, "StoneCorner", direction='BN')),

            BlockType(0x14, "StoneCorner", direction='TN', rot=(0,0,3), rot90 = BlockType(0x15, "StoneCorner", direction='TW')),  # Non official
            BlockType(0x15, "StoneCorner", direction='TW', rot=(0,1,3), rot90 = BlockType(0x16, "StoneCorner", direction='TS')),
            BlockType(0x16, "StoneCorner", direction='TS', rot=(0,2,3), rot90 = BlockType(0x17, "StoneCorner", direction='TE')),
            BlockType(0x17, "StoneCorner", direction='TE', rot=(0,3,3), rot90 = BlockType(0x14, "StoneCorner", direction='TN')),
        ])

        self.WHEEL = BlockType(19, "Wheel", subtypes=[
            BlockType(0x00, "Wheel", direction='W', rot=(0,0,0), rot90=BlockType(0x01, "Wheel", direction='S')),
            BlockType(0x01, "Wheel", direction='S', rot=(0,1,0), rot90=BlockType(0x02, "Wheel", direction='E')),  # Buggy (not rotating)
            BlockType(0x02, "Wheel", direction='E', rot=(0,2,0), rot90=BlockType(0x03, "Wheel", direction='N')),
            BlockType(0x03, "Wheel", direction='N', rot=(0,3,0), rot90=BlockType(0x00, "Wheel", direction='W')),  # Buggy (not rotating)

            BlockType(0x04, "Wheel", direction='W', rot=(1,0,0), rot90=BlockType(0x01, "Wheel", direction='S')),  # Working but strange a in double with 0x00
            BlockType(0x0c, "Wheel", direction='W', rot=(3,0,0), rot90=BlockType(0x01, "Wheel", direction='S')),  # Working but strange a in double with 0x00

            # The others combinations are just not attaching wheels in different directions.
        ])

        self.METAL_STAIR = BlockType(20, "MetalStair", subtypes=[
            BlockType(0x00, "MetalStair", direction='BN', rot=(0, 0, 0), rot90=BlockType(0x01, "MetalStair", direction='BW')),  # Official
            BlockType(0x01, "MetalStair", direction='BW', rot=(0, 1, 0), rot90=BlockType(0x02, "MetalStair", direction='BS')),
            BlockType(0x02, "MetalStair", direction='BS', rot=(0, 2, 0), rot90=BlockType(0x03, "MetalStair", direction='BE')),
            BlockType(0x03, "MetalStair", direction='BE', rot=(0, 3, 0), rot90=BlockType(0x00, "MetalStair", direction='BN')),

            BlockType(0x04, "MetalStair", direction='TN', rot=(1, 0, 0), rot90=BlockType(0x05, "MetalStair", direction='TW')),  # Official
            BlockType(0x05, "MetalStair", direction='TW', rot=(1, 0, 3), rot90=BlockType(0x06, "MetalStair", direction='TS')),
            BlockType(0x06, "MetalStair", direction='TS', rot=(1, 0, 2), rot90=BlockType(0x07, "MetalStair", direction='TE')),
            BlockType(0x07, "MetalStair", direction='TE', rot=(1, 0, 1), rot90=BlockType(0x04, "MetalStair", direction='TN')),

            BlockType(0x08, "MetalStair", direction='TS', rot=(2, 0, 0), rot90=BlockType(0x09, "MetalStair", direction='TE')),  # Non official
            BlockType(0x09, "MetalStair", direction='TE', rot=(2, 3, 0), rot90=BlockType(0x0a, "MetalStair", direction='TN')),
            BlockType(0x0a, "MetalStair", direction='TN', rot=(2, 2, 0), rot90=BlockType(0x0b, "MetalStair", direction='TW')),
            BlockType(0x0b, "MetalStair", direction='TW', rot=(2, 1, 0), rot90=BlockType(0x08, "MetalStair", direction='TS')),

            BlockType(0x0c, "MetalStair", direction='BS', rot=(3, 0, 0), rot90=BlockType(0x0d, "MetalStair", direction='BE')),  # Non official
            BlockType(0x0d, "MetalStair", direction='BE', rot=(3, 0, 1), rot90=BlockType(0x0e, "MetalStair", direction='BN')),
            BlockType(0x0e, "MetalStair", direction='BN', rot=(3, 0, 2), rot90=BlockType(0x0f, "MetalStair", direction='BW')),
            BlockType(0x0f, "MetalStair", direction='BW', rot=(3, 0, 3), rot90=BlockType(0x0c, "MetalStair", direction='BS')),

            BlockType(0x10, "MetalStair", direction='NE', rot=(0, 0, 1), rot90=BlockType(0x11, "MetalStair", direction='NW')),  # Official
            BlockType(0x11, "MetalStair", direction='NW', rot=(0, 1, 1), rot90=BlockType(0x12, "MetalStair", direction='SW')),
            BlockType(0x12, "MetalStair", direction='SW', rot=(0, 2, 1), rot90=BlockType(0x13, "MetalStair", direction='SE')),
            BlockType(0x13, "MetalStair", direction='SE', rot=(0, 3, 1), rot90=BlockType(0x10, "MetalStair", direction='NE')),

            BlockType(0x14, "MetalStair", direction='NW', rot=(0, 0, 3), rot90=BlockType(0x15, "MetalStair", direction='SW')),  # Non official
            BlockType(0x15, "MetalStair", direction='SW', rot=(0, 1, 3), rot90=BlockType(0x16, "MetalStair", direction='SE')),
            BlockType(0x16, "MetalStair", direction='SE', rot=(0, 2, 3), rot90=BlockType(0x17, "MetalStair", direction='NE')),
            BlockType(0x17, "MetalStair", direction='NE', rot=(0, 3, 3), rot90=BlockType(0x14, "MetalStair", direction='NW')),
        ])

        self.METAL_CORNER = BlockType(21, "MetalCorner", subtypes=[
            BlockType(0x00, "MetalCorner", direction='NW', rot=(0,0,0), rot90=BlockType(0x01, "MetalCorner", direction='SW')),  # Official
            BlockType(0x01, "MetalCorner", direction='SW', rot=(0,1,0), rot90=BlockType(0x02, "MetalCorner", direction='SE')),
            BlockType(0x02, "MetalCorner", direction='SE', rot=(0,2,0), rot90=BlockType(0x03, "MetalCorner", direction='NE')),
            BlockType(0x03, "MetalCorner", direction='NE', rot=(0,3,0), rot90=BlockType(0x00, "MetalCorner", direction='NW')),

            BlockType(0x04, "MetalCorner", direction='TW', rot=(1,0,0), rot90=BlockType(0x05, "MetalCorner", direction='TS')),  # Official
            BlockType(0x05, "MetalCorner", direction='TS', rot=(1,0,3), rot90=BlockType(0x06, "MetalCorner", direction='TE')),
            BlockType(0x06, "MetalCorner", direction='TE', rot=(1,0,2), rot90=BlockType(0x07, "MetalCorner", direction='TN')),
            BlockType(0x07, "MetalCorner", direction='TN', rot=(1,0,1), rot90=BlockType(0x04, "MetalCorner", direction='TW')),

            BlockType(0x08, "MetalCorner", direction='SW', rot=(2,0,0), rot90 = BlockType(0x09, "MetalCorner", direction='SE')),  # Non official
            BlockType(0x09, "MetalCorner", direction='SE', rot=(2,0,3), rot90 = BlockType(0x0a, "MetalCorner", direction='NE')),
            BlockType(0x0a, "MetalCorner", direction='NE', rot=(2,0,2), rot90 = BlockType(0x0b, "MetalCorner", direction='NW')),
            BlockType(0x0b, "MetalCorner", direction='NW', rot=(2,0,1), rot90 = BlockType(0x08, "MetalCorner", direction='SW')),

            BlockType(0x0c, "MetalCorner", direction='BW', rot=(3,0,0), rot90 = BlockType(0x0d, "MetalCorner", direction='BS')),  # Non official
            BlockType(0x0d, "MetalCorner", direction='BS', rot=(3,0,1), rot90 = BlockType(0x0e, "MetalCorner", direction='BE')),
            BlockType(0x0e, "MetalCorner", direction='BE', rot=(3,0,2), rot90 = BlockType(0x0f, "MetalCorner", direction='BN')),
            BlockType(0x0f, "MetalCorner", direction='BN', rot=(3,0,3), rot90 = BlockType(0x0c, "MetalCorner", direction='BW')),

            BlockType(0x10, "MetalCorner", direction='BN', rot=(0,0,1), rot90=BlockType(0x11, "MetalCorner", direction='BW')),  # Official
            BlockType(0x11, "MetalCorner", direction='BW', rot=(0,1,1), rot90=BlockType(0x12, "MetalCorner", direction='BS')),
            BlockType(0x12, "MetalCorner", direction='BS', rot=(0,2,1), rot90=BlockType(0x13, "MetalCorner", direction='BE')),
            BlockType(0x13, "MetalCorner", direction='BE', rot=(0,3,1), rot90=BlockType(0x10, "MetalCorner", direction='BN')),

            BlockType(0x14, "MetalCorner", direction='TN', rot=(0,0,3), rot90 = BlockType(0x15, "MetalCorner", direction='TW')),  # Non official
            BlockType(0x15, "MetalCorner", direction='TW', rot=(0,1,3), rot90 = BlockType(0x16, "MetalCorner", direction='TS')),
            BlockType(0x16, "MetalCorner", direction='TS', rot=(0,2,3), rot90 = BlockType(0x17, "MetalCorner", direction='TE')),
            BlockType(0x17, "MetalCorner", direction='TE', rot=(0,3,3), rot90 = BlockType(0x14, "MetalCorner", direction='TN')),
        ])

        self.COPPER = BlockType(23, "Copper")
        self.STONE_ALT = BlockType(24, "Alternative stone")

        self.UNKNOWN_0 = BlockType(28,"Unknown?")  # Leads to corrupted data
        self.STONE_ALT2 = BlockType(29,"Alternative stone") # BUGGY: Next coordinates behave strangely after the block

        self.STONE_PILLAR_ALT = BlockType(31,"StonePillarAlt", subtypes=[
            BlockType(0x00, "StonePillarAlt(NS)", rot90=BlockType(0x01, "StonePillarAlt(NE)")), # Normal-South
            BlockType(0x01, "StonePillarAlt(NE)", rot90=BlockType(0x02, "StonePillarAlt(NN)")),
            BlockType(0x02, "StonePillarAlt(NN)", rot90=BlockType(0x03, "StonePillarAlt(NW)")),
            BlockType(0x03, "StonePillarAlt(NW)", rot90=BlockType(0x00, "StonePillarAlt(NS)")),
            BlockType(0x14, "StonePillarAlt(SS)", rot90=BlockType(0x15, "StonePillarAlt(SE)")),  # Side-South
            BlockType(0x15, "StonePillarAlt(SE)", rot90=BlockType(0x16, "StonePillarAlt(SN)")),
            BlockType(0x16, "StonePillarAlt(SN)", rot90=BlockType(0x17, "StonePillarAlt(SW)")),
            BlockType(0x17, "StonePillarAlt(SW)", rot90=BlockType(0x14, "StonePillarAlt(SS)")),
            BlockType(0x0c, "StonePillarAlt(UZ)", rot90=BlockType(0x0f, "StonePillarAlt(UX)")),  # Up/Z-Axis
            BlockType(0x05, "StonePillarAlt(DX)", rot90=BlockType(0x06, "StonePillarAlt(DZ)")),  # Down/X-Axis
            BlockType(0x06, "StonePillarAlt(DZ)", rot90=BlockType(0x05, "StonePillarAlt(DX)")),  # Down/Z-Axis
            BlockType(0x0f, "StonePillarAlt(UX)", rot90=BlockType(0x0c, "StonePillarAlt(UZ)")),
        ])

        self.STONE_HALF_PILLAR = BlockType(34,"StoneHalfPillar", subtypes=[
            BlockType(0x00, "StoneHalfPillar", direction='YS', rot=(0,0,0), rot90=BlockType(0x01, "StoneHalfPillar", direction='YE')),  # Official
            BlockType(0x01, "StoneHalfPillar", direction='YE', rot=(0,1,0), rot90=BlockType(0x02, "StoneHalfPillar", direction='YN')),
            BlockType(0x02, "StoneHalfPillar", direction='YN', rot=(0,2,0), rot90=BlockType(0x03, "StoneHalfPillar", direction='YW')),
            BlockType(0x03, "StoneHalfPillar", direction='YW', rot=(0,3,0), rot90=BlockType(0x00, "StoneHalfPillar", direction='YS')),

            BlockType(0x04, "StoneHalfPillar", direction='ZB', rot=(1,0,0), rot90=BlockType(0x07, "StoneHalfPillar", direction='XB')),  # Non official

            BlockType(0x05, "StoneHalfPillar", direction='XB', rot=(1,0,3), rot90=BlockType(0x06, "StoneHalfPillar", direction='ZB')),  # official
            BlockType(0x06, "StoneHalfPillar", direction='ZB', rot=(1,0,2), rot90=BlockType(0x05, "StoneHalfPillar", direction='XB')),

            BlockType(0x07, "StoneHalfPillar", direction='XB', rot=(1,0,1), rot90=BlockType(0x04, "StoneHalfPillar", direction='ZB')),  # Non official

            BlockType(0x08, "StoneHalfPillar", direction='YN', rot=(2,0,0), rot90=BlockType(0x09, "StoneHalfPillar", direction='YW')),  # Non official
            BlockType(0x09, "StoneHalfPillar", direction='YW', rot=(2,3,0), rot90=BlockType(0x0a, "StoneHalfPillar", direction='YS')),
            BlockType(0x0a, "StoneHalfPillar", direction='YS', rot=(2,2,0), rot90=BlockType(0x0b, "StoneHalfPillar", direction='YE')),
            BlockType(0x0b, "StoneHalfPillar", direction='YE', rot=(2,1,0), rot90=BlockType(0x08, "StoneHalfPillar", direction='YN')),

            BlockType(0x0c, "StoneHalfPillar", direction='ZT', rot=(3,0,0), rot90=BlockType(0x0f, "StoneHalfPillar", direction='XT')),  # official

            BlockType(0x0d, "StoneHalfPillar", direction='XT', rot=(3,0,1), rot90=BlockType(0x0e, "StoneHalfPillar", direction='ZT')),  # Non official
            BlockType(0x0e, "StoneHalfPillar", direction='ZT', rot=(3,0,2), rot90=BlockType(0x0f, "StoneHalfPillar", direction='XT')),

            BlockType(0x0f, "StoneHalfPillar", direction='XT', rot=(3,0,3), rot90=BlockType(0x0c, "StoneHalfPillar", direction='ZT')),  # official

            BlockType(0x10, "StoneHalfPillar", direction='XS', rot=(0,0,1), rot90=BlockType(0x11, "StoneHalfPillar", direction='ZE')),  # Non Official
            BlockType(0x11, "StoneHalfPillar", direction='ZE', rot=(0,1,1), rot90=BlockType(0x12, "StoneHalfPillar", direction='XN')),
            BlockType(0x12, "StoneHalfPillar", direction='XN', rot=(0,2,1), rot90=BlockType(0x13, "StoneHalfPillar", direction='ZW')),
            BlockType(0x13, "StoneHalfPillar", direction='ZW', rot=(0,3,1), rot90=BlockType(0x10, "StoneHalfPillar", direction='XS')),

            BlockType(0x14, "StoneHalfPillar", direction='XS', rot=(0,0,3), rot90=BlockType(0x15, "StoneHalfPillar", direction='ZE')),  # official
            BlockType(0x15, "StoneHalfPillar", direction='ZE', rot=(0,1,3), rot90=BlockType(0x16, "StoneHalfPillar", direction='XN')),
            BlockType(0x16, "StoneHalfPillar", direction='XN', rot=(0,2,3), rot90=BlockType(0x17, "StoneHalfPillar", direction='ZW')),
            BlockType(0x17, "StoneHalfPillar", direction='ZW', rot=(0,3,3), rot90=BlockType(0x14, "StoneHalfPillar", direction='XS')),

            # BlockType(0x00, "StoneHalfPillar(NS)", rot90=BlockType(0x01, "StoneHalfPillar(NE)")), # Normal-South
            # BlockType(0x01, "StoneHalfPillar(NE)", rot90=BlockType(0x02, "StoneHalfPillar(NN)")),
            # BlockType(0x02, "StoneHalfPillar(NN)", rot90=BlockType(0x03, "StoneHalfPillar(NW)")),
            # BlockType(0x03, "StoneHalfPillar(NW)", rot90=BlockType(0x00, "StoneHalfPillar(NS)")),
            # BlockType(0x14, "StoneHalfPillar(SS)", rot90=BlockType(0x15, "StoneHalfPillar(SE)")),  # Side-South
            # BlockType(0x15, "StoneHalfPillar(SE)", rot90=BlockType(0x16, "StoneHalfPillar(SN)")),
            # BlockType(0x16, "StoneHalfPillar(SN)", rot90=BlockType(0x17, "StoneHalfPillar(SW)")),
            # BlockType(0x17, "StoneHalfPillar(SW)", rot90=BlockType(0x14, "StoneHalfPillar(SS)")),
            # BlockType(0x0c, "StoneHalfPillar(UZ)", rot90=BlockType(0x0f, "StoneHalfPillar(UX)")),  # Up/Z-Axis
            # BlockType(0x05, "StoneHalfPillar(DX)", rot90=BlockType(0x06, "StoneHalfPillar(DZ)")),  # Down/X-Axis
            # BlockType(0x06, "StoneHalfPillar(DZ)", rot90=BlockType(0x05, "StoneHalfPillar(DX)")),  # Down/Z-Axis
            # BlockType(0x0f, "StoneHalfPillar(UX)", rot90=BlockType(0x0c, "StoneHalfPillar(UZ)")),
        ])

        self.DRAGGABLE_PILLAR = BlockType(36,"DraggablePillar", subtypes=[
            BlockType(0x00, "DraggablePillar", direction='Y', rot=(0,0,0), rot90=BlockType(0x01, "DraggablePillar", direction='Y')),  # Official
            BlockType(0x01, "DraggablePillar", direction='Y', rot=(0,1,0), rot90=BlockType(0x02, "DraggablePillar", direction='Y')),
            BlockType(0x02, "DraggablePillar", direction='Y', rot=(0,2,0), rot90=BlockType(0x03, "DraggablePillar", direction='Y')),
            BlockType(0x03, "DraggablePillar", direction='Y', rot=(0,3,0), rot90=BlockType(0x00, "DraggablePillar", direction='Y')),

            BlockType(0x04, "DraggablePillar", direction='Z', rot=(1,0,0), rot90=BlockType(0x05, "DraggablePillar", direction='X')),
            BlockType(0x05, "DraggablePillar", direction='X', rot=(1,0,3), rot90=BlockType(0x06, "DraggablePillar", direction='Z')),
            BlockType(0x06, "DraggablePillar", direction='Z', rot=(1,0,2), rot90=BlockType(0x07, "DraggablePillar", direction='X')),
            BlockType(0x07, "DraggablePillar", direction='X', rot=(1,0,1), rot90=BlockType(0x04, "DraggablePillar", direction='Z')),

            BlockType(0x08, "DraggablePillar", direction='Y', rot=(2,0,0), rot90 = BlockType(0x09, "DraggablePillar", direction='Y')),
            BlockType(0x09, "DraggablePillar", direction='Y', rot=(2,3,0), rot90 = BlockType(0x0a, "DraggablePillar", direction='Y')),
            BlockType(0x0a, "DraggablePillar", direction='Y', rot=(2,2,0), rot90 = BlockType(0x0b, "DraggablePillar", direction='Y')),
            BlockType(0x0b, "DraggablePillar", direction='Y', rot=(2,1,0), rot90 = BlockType(0x08, "DraggablePillar", direction='Y')),

            BlockType(0x0c, "DraggablePillar", direction='Z', rot=(3,0,0), rot90 = BlockType(0x0d, "DraggablePillar", direction='X')),  # Official
            BlockType(0x0d, "DraggablePillar", direction='X', rot=(3,0,1), rot90 = BlockType(0x0e, "DraggablePillar", direction='Z')),
            BlockType(0x0e, "DraggablePillar", direction='Z', rot=(3,0,2), rot90 = BlockType(0x0f, "DraggablePillar", direction='X')),
            BlockType(0x0f, "DraggablePillar", direction='X', rot=(3,0,3), rot90 = BlockType(0x0c, "DraggablePillar", direction='Z')),

            BlockType(0x10, "DraggablePillar", direction='X', rot=(0,0,1), rot90=BlockType(0x11, "DraggablePillar", direction='Z')),
            BlockType(0x11, "DraggablePillar", direction='Z', rot=(0,1,1), rot90=BlockType(0x12, "DraggablePillar", direction='X')),
            BlockType(0x12, "DraggablePillar", direction='X', rot=(0,2,1), rot90=BlockType(0x13, "DraggablePillar", direction='Z')),
            BlockType(0x13, "DraggablePillar", direction='Z', rot=(0,3,1), rot90=BlockType(0x10, "DraggablePillar", direction='X')),

            BlockType(0x14, "DraggablePillar", direction='X', rot=(0,0,3), rot90 = BlockType(0x15, "DraggablePillar", direction='Z')),  # Official
            BlockType(0x15, "DraggablePillar", direction='Z', rot=(0,1,3), rot90 = BlockType(0x16, "DraggablePillar", direction='X')),
            BlockType(0x16, "DraggablePillar", direction='X', rot=(0,2,3), rot90 = BlockType(0x17, "DraggablePillar", direction='Z')),
            BlockType(0x17, "DraggablePillar", direction='Z', rot=(0,3,3), rot90 = BlockType(0x14, "DraggablePillar", direction='X')),
        ])

        self.METAL_SHINY = BlockType(38,"Shiny Metal") # Shiny stone

        self.COPPER_ALT1 = BlockType(40, "CopperAlt1") # Next to metalpillar
        self.COPPER_ALT2 = BlockType(42, "CopperAlt2") # Next to Slider
        self.COPPER_ALT3 = BlockType(44, "CopperAlt3") # Next to Fence
        self.COPPER_ALT4 = BlockType(45, "CopperAlt4")
        self.COPPER_ALT5 = BlockType(46, "CopperAlt5")
        self.COPPER_ALT6 = BlockType(47, "CopperAlt6")

        # List available blocks by values with their original subtypes
        self.map = self.__dict__.keys()

        self.values = {}
        self.names = {}
        for typename in self.map:
            blocktype = getattr(self, typename)
            self.values[blocktype.value] = {
                'blocktype': blocktype,
                'subtypes': None if blocktype.subtypes is None else {b.value: b for b in blocktype.subtypes}
            }
            self.names[blocktype.name.lower()] = {
                'blocktype': blocktype,
                'subtypes': None if blocktype.subtypes is None else {b.rot: b for b in blocktype.subtypes}
            }


class Block:

    def __init__(self, blocktype, subtype = None):
        self.blocktype = blocktype
        self.subtype = subtype

    def toHex(self):
        _toHex = lambda x: "".join([hex(ord(c))[2:].zfill(2) for c in x])

        hexstr = _toHex(chr(self.blocktype.value))
        return hexstr if self.subtype is None else (hexstr + _toHex(chr(self.subtype)))

    def __repr__(self):
        return "Block({!r}, {!r})".format(repr(self.blocktype), repr(self.subtype))

    def __str__(self):
        return "Block of {}, subtype {}".format(self.blocktype.name, self.subtype.name if self.subtype else "None")
