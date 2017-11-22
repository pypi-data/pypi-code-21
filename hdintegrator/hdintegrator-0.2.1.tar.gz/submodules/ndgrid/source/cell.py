'''
Cell class of NdGrid.

Copyright 2017 Ilja Honkonen

NdGrid is free software: you can redistribute it and/or modify
it under the terms of the GNU Lesser General Public License
version 3 as published by the Free Software Foundation.

NdGrid is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
GNU Lesser General Public License for more details.

You should have received a copy of the GNU Lesser General
Public License along with Foobar. If not, see
<http://www.gnu.org/licenses/>.
'''


'''
Cartesian geometry cell in arbitrary dimensions.

An instance of NdGrid consists of one or more cells.
'''
class cell:

	'''
	Creates a cell without dimension(s).
	'''
	def __init__(self):
		self.volume = dict()
		self.data = dict()

	'''
	Returns dimensions of this cell.
	'''
	def get_dimensions(self):
		return [dim for dim in self.volume]

	'''
	Returns start and end coordinates of this cell in given dimension as a tuple.

	Raises ValueError if given dimension doesn't exist.
	'''
	def get_extent(self, dim):
		if dim in self.volume:
			return self.volume[dim]
		else:
			raise ValueError("Given dimension doesn't exist")

	'''
	Sets start and ennd coordinates of this cell in given dimension to given values.
	'''
	def set_extent(self, dim, start, end):
		if end <= start:
			raise ValueError('end <= start: ' + str(end) + ', ' + str(start))
		self.volume[dim] = (start, end)

	'''
	Removes given dimension from this cell if it exists, otherwise does nothing.
	'''
	def remove_extent(self, dim):
		if dim in self.volume:
			self.volume.pop(dim)

	'''
	Returns a dictionary of all extents of this cell.
	'''
	def get_extents(self):
		return self.volume

	'''
	Returns two new cells as if this cell was split in given dimension at given position.

	If pos == None cell is split in middle along given dimension.
	Doesn't copy this cell's data member to new cells.
	'''
	def split(self, dim, pos = None):
		first, second = cell(), cell()
		for d in self.volume.keys():
			extent = self.volume[d]
			first.set_extent(d, extent[0], extent[1])
			second.set_extent(d, extent[0], extent[1])

		start = self.volume[dim][0]
		end = self.volume[dim][1]
		mid = (start + end) / 2
		if pos != None:
			mid = pos
		first.set_extent(dim = dim, start = start, end = mid)
		second.set_extent(dim = dim, start = mid, end = end)
		return first, second
