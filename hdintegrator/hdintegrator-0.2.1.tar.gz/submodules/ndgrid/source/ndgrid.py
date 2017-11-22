#! /usr/bin/env python3
'''
NdGrid - N-dimensional grid library.

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


from networkx import Graph
import cell


'''
N-dimensional grid library in cartesian coordinates.
New dimensions can be added to existing cells at any time.
Supports adaptive mesh refinement but not coarsening.
'''
class ndgrid:

	'''
	Creates a new grid which consists of given cell
	'''
	def __init__(self, cell):
		self.graph = Graph()
		self.graph.add_node(cell)


	'''
	Returns a list of all grid cells.
	'''
	def get_cells(self):
		return self.graph.nodes()


	'''
	Returns a list of all neighbors of given cell.
	'''
	def get_neighbors(self, cell):
		if not cell in self.graph:
			raise ValueError('Given cell not in grid')
		return self.graph.neighbors(cell)


	'''
	Splits given grid cell along dimension dim at position pos.

	If cell doesn't have given dim it is added with extent [-1.0, 1.0].
	If pos == None cell is split in middle.

	Given cell is replaced with split cells.
	Returns split cells.
	'''
	def split(self, cell, dim, pos = None):
		if not cell in self.graph:
			raise ValueError('Given cell not in grid')

		if not dim in cell.volume:
			cell.set_extent(dim, -1.0, 1.0)

		ext = cell.get_extent(dim)
		if pos == None:
			pos = (ext[0] + ext[1]) / 2
		if pos < ext[0] or pos > ext[1]:
			raise ValueError('Given position not within cell')

		first, second = cell.split(dim, pos)
		first.data = cell.data.copy()
		second.data = cell.data.copy()

		self.graph.add_node(first)
		self.graph.add_node(second)
		self.graph.add_edge(first, second)

		neighs = self.graph.neighbors(cell)
		self.graph.remove_node(cell)
		for neigh in neighs:
			if not dim in neigh.volume:
				self.graph.add_edge(neigh, first)
				self.graph.add_edge(neigh, second)
				continue

			ext = neigh.get_extent(dim)
			if ext[0] >= pos:
				self.graph.add_edge(neigh, second)
			elif ext[1] <= pos:
				self.graph.add_edge(neigh, first)
			else:
				self.graph.add_edge(neigh, second)
				self.graph.add_edge(neigh, first)
		return first, second


	'''
	Removes given cell from grid and all edges leading to and from it.
	'''
	def remove(self, cell):
		if not cell in self.graph:
			return
		self.graph.remove_node(cell)
