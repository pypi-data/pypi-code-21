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
from . import blocks
import numpy as np
import json

def toHex(x):
    """Convert bytes x into a string containing hexadecimal values"""
    return "".join([hex(ord(c))[2:].zfill(2) for c in x])


class MekoLevel:
    blocktypes = blocks.BlockTypes()

    def __init__(self, code=None, jsonfile=None, jsondata=None):
        # Currently all levels are 16x16x16.
        self.size = (16, 16, 16)

        if code is not None:
            self.loadCode(code)
        elif jsonfile is not None:
            self.loadJSON(jsonfile)
        elif jsondata is not None:
            self.fromJSON(jsondata)

    def loadCode(self, code):
        # storing each data into an list/array
        hex_data = []
        for data in code:
            hex_data.append(toHex(data))
            # hex_data.append(data)

        tmp_data = hex_data[:]
        # getting the title
        self.title = ''
        size_title = int(tmp_data.pop(0), 16)
        while (size_title):
            self.title += (tmp_data.pop(0)).decode('hex')
            size_title -= 1

        # getting the author
        self.author = ''
        size_author = int(tmp_data.pop(0), 16)
        while (size_author):
            self.author += (tmp_data.pop(0)).decode('hex')
            size_author -= 1

        # a xyz matrix of objects. Indexed [z][y][x]
        self.matrix_object = []

        for z in range(0, self.size[2]):
            blocks_y = []
            for y in range(0, self.size[1]):
                blocks_x = []
                for x in range(0, self.size[0]):
                    identifier = tmp_data.pop(0)
                    # print z,y,x,identifier
                    blocktype = self.blocktypes.values[int(identifier, 16)]['blocktype']
                    subtype = None
                    if blocktype.subtypes is not None:
                        subtype = int(tmp_data.pop(0), 16)

                    # print(int(identifier, 16), subtype)
                    block = blocks.Block(blocktype, subtype)
                    blocks_x.append(block)
                blocks_y.append(blocks_x)
            self.matrix_object.append(blocks_y)
        try:
            pass
        except:
            print('ERROR: invalid level format (not enougth data)')

    def setBlock(self, x, y, z, blocktype, subtype=None):
        self.matrix_object[z][y][x] = blocks.Block(blocktype, subtype)

    @staticmethod
    def sparse_blocks(matrix_object):
        """Generators (x, y, z, block) tuples for each non-air block in the matrix.

        Blocks are generated in x, y, z order

        Args:
            - matrix_object (3D list of Block): matrix of all blocks in the level

        Returns:
            generator supplying (x, y, z, block) tuples for all non-air blocks.

        """
        for z, xyslice in enumerate(matrix_object):
            for y, row in enumerate(xyslice):
                for x, block in enumerate(row):
                    block_val = block.blocktype.value
                    if block_val != MekoLevel.blocktypes.AIR.value:
                        yield (x, y, z, block)

    def getBlocks(self):
        """Get a list of all non-air blocks in the level

        Returns:
            a list of tuples (x, y, z, block)

        """
        return list(self.sparse_blocks(self.matrix_object))

    def getBlockMatrix(self):
        """Get the full 16x16x16 matrix of blocks, including air blocks"""
        return self.matrix_object

    def toJsonData(self):
        listBlocks = []
        pos_x = pos_y = pos_z = 0
        for z in self.matrix_object:
            pos_y = 0
            for y in z:
                pos_x = 0
                for x in y:
                    block_name = x.blocktype.name.lower()
                    if block_name != 'air':
                        subtypes = self.blocktypes.values[x.blocktype.value]['subtypes']
                        subtype = subtypes[x.subtype] if subtypes is not None else None
                        block = {
                            'name': block_name,
                            'pos': [pos_x,pos_y,pos_z],
                        }
                        if subtype is not None:
                            block['rot'] = [n for n in subtype.rot]
                        listBlocks.append(block)
                    pos_x += 1
                pos_y += 1
            pos_z += 1

        JSON_data = {}
        JSON_data['data'] = listBlocks
        JSON_data['title'] = self.title
        JSON_data['author'] = self.author
        return JSON_data
    def toJson(self):
        return json.dumps(self.toJsonData())

    def saveJSON(self, JSON_file):
        JSON_data = self.toJson()
        if type(JSON_file) == str:
            with open(JSON_file, 'w') as f:
                f.write(JSON_data)
                print "JSON  saved:", JSON_file
                return True
        else:
            JSON_file.write(JSON_data)
            print "JSON  saved:", JSON_file.name if hasattr(JSON_file,"name") else JSON_file
            return True
        return False

    def fromJSON(self, json_data):
        coord = {}
        JSON_data = json.loads(json_data)

        if 'title' in JSON_data and 'author' in JSON_data and 'data' in JSON_data:
            self.title = JSON_data['title']
            self.author = JSON_data['author']
            listBlocks = JSON_data['data']
            for block in listBlocks:
                if block is not None:
                    coord[tuple(block['pos'])] = block

            self.matrix_object = []
            for z in range(0, self.size[2]):
                blocks_y = []
                for y in range(0, self.size[1]):
                    blocks_x = []
                    for x in range(0, self.size[0]):
                        c = (x,y,z)
                        subtype = None
                        if c in coord:
                            block = coord[c]
                            blocktype = self.blocktypes.names[block['name']]['blocktype']
                            if blocktype.subtypes is not None and 'rot' in block:
                                subtype = 0
                                rot = block['rot']
                                for subt in blocktype.subtypes:
                                    if subt.rot == tuple(rot):
                                        subtype = subt.value
                                        break
                        else:
                            blocktype = self.blocktypes.values[0]['blocktype']

                        block = blocks.Block(blocktype, subtype)
                        blocks_x.append(block)
                    blocks_y.append(blocks_x)
                self.matrix_object.append(blocks_y)
        else:
            print 'Not enough argument in JSON'

    def loadJSON(self, JSON_file):
        with open(JSON_file, 'r') as f:
            JSON_data = f.read()
            self.fromJSON(JSON_data)
            return True
        return False

    def toHex(self):
        """Encode this level as bytes. Returns a hexadecimal string"""
        level_str = ''
        level_str += toHex(chr(len(self.title))) + toHex(self.title)
        level_str += toHex(chr(len(self.author))) + toHex(self.author)
        for z in self.matrix_object:
            for y in z:
                for x in y:
                    level_str += x.toHex()
        return level_str

    def toBytes(self):
        """Encode this level as a bytearray"""
        return bytearray.fromhex(self.toHex())

    def replace(self,
                blocktype_src,
                blocktype_dst,
                subtype_scope=None,
                x_scope=None,
                y_scope=None,
                z_scope=None):
        '''
        Method to replace one block type by another, depending on scopes criteria
        :param blocktype_src: Block type object
        :param blocktype_dst: Block type object
        :param subtype_scope: A list or dict of subtypes to match. If dict type, keys define the list and values the subtype to replace with
        :param x_scope: A list of x positions to match
        :param y_scope: A list of y positions to match
        :param z_scope: A list of z positions to match
        :return: None
        '''
        pos_z = 0
        for z in self.matrix_object:
            pos_y = 0
            for y in z:
                pos_x = 0
                for x in y:
                    if x.blocktype == blocktype_src:
                        if (x_scope is None or pos_x in x_scope) and \
                           (y_scope is None or pos_y in y_scope) and \
                           (z_scope is None or pos_z in z_scope):

                            if type(subtype_scope) is list:
                                if x.subtype in subtype_scope:
                                    x.blocktype = blocktype_dst
                                    # print 'replaced:', pos_x, pos_y, pos_z
                            elif type(subtype_scope) is dict:
                                if x.subtype in subtype_scope.keys():
                                    x.blocktype = blocktype_dst
                                    x.subtype = subtype_scope[x.subtype]
                            else:
                                x.blocktype = blocktype_dst
                                # print 'replaced:', pos_x, pos_y, pos_z
                    pos_x += 1
                pos_y += 1
            pos_z += 1

    def rot90(self):
        m = np.array(self.matrix_object, dtype=object)
        m = np.swapaxes(m,1,2) # rotation axis --> y, not x
        m = np.rot90(m)
        m = np.swapaxes(m,1,2)
        self.matrix_object = m.tolist()

        # Rotate each block: depends from the rot90 subtype attribute
        for z in self.matrix_object:
            for y in z:
                for x in y:
                    blocktype = x.blocktype
                    subtypes = self.blocktypes.values[blocktype.value]['subtypes']
                    if subtypes is not None and x.subtype in subtypes:
                        subtype = subtypes[x.subtype] # get from the original subtype
                        if subtype.rot90 is not None:
                            x.subtype = subtype.rot90.value

    def __iter__(self, transform=None):
        """Iterate over all blocks in the level

        Without a transform function, orders blocks with x varying the fastest
        followed by z and with y (the vertical axis) varying the slowest. This
        is equivalent to `transform=lambda yzx: (yzx[2],yzx[0],yzx[1])`.

        The transform argument takes a bijective function over the set of block
        indices. This can be used to change the order of iteration.

        Args:
            - transform ((int,int,int) -> (int,int,int)): A function transforming
                the block index (x,y,z) to some new (x,y,z)

        Returns: Iterator of all blocks
        """
        # Tuples of all valid indices, in (0, 1, 2) order
        indices = iter((x, y, z) for x in range(self.size[0]) for y in range(self.size[1]) for z in range(self.size[2]))
        if transform:
            indices = itertools.imap(transform, indices)
        return iter(self.matrix_object[indices[2]][indices[1]][indices[0]] for index in indices)

    def getBounds(self, ignore_blocks=None):
        """Get the bounding box for non-air blocks in this level

        Args:
            - ignore_blocks (list of BlockType): list of block types to ignore when computing the bounding box.
                Defaults to water and air.
        Returns:
            (xmin, xmax, ymin, ymax, zmin, zmax) inclusive

        """
        d = len(self.matrix_object)

        if ignore_blocks is None:
            ignore_blocks = [self.blocktypes.AIR, self.blocktypes.WATER]

        # Set bounds to first slice encountered with a block
        for xmin in range(0, d):
            if any(self.matrix_object[z][y][xmin].blocktype not in ignore_blocks for y in range(d) for z in range(d)):
                break
        for xmax in range(d - 1, -1, -1):
            if any(self.matrix_object[z][y][xmax].blocktype not in ignore_blocks for y in range(d) for z in range(d)):
                break
        for ymin in range(0, d):
            if any(self.matrix_object[z][ymin][x].blocktype not in ignore_blocks for z in range(d) for x in range(d)):
                break
        for ymax in range(d - 1, -1, -1):
            if any(self.matrix_object[z][ymax][x].blocktype not in ignore_blocks for z in range(d) for x in range(d)):
                break
        for zmin in range(0, d):
            if any(self.matrix_object[zmin][y][x].blocktype not in ignore_blocks for y in range(d) for x in range(d)):
                break
        for zmax in range(d - 1, -1, -1):
            if any(self.matrix_object[zmax][y][x].blocktype not in ignore_blocks for y in range(d) for x in range(d)):
                break
        return (xmin, xmax, ymin, ymax, zmin, zmax)
