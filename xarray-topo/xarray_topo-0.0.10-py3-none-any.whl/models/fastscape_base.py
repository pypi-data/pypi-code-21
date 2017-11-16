"""Implementation of FastScape's base model using the xarray-simlab
framework.

This module provides both a `xsimlab.Model` object and subclasses of
`xsimlab.Process`.

This base model allows to simulate the evolution of topography as a
result of block uplift vs. channel erosion by stream power law.

"""
import numpy as np

from xsimlab import (Model, Process, Variable, ForeignVariable,
                     VariableGroup, diagnostic, IntegerVariable,
                     FloatVariable, ValidationError)

from ..algos import flow_routing
from ..algos import bedrock_channel
from ..algos import hillslope_erosion


class StackedGridXY(Process):
    """A 2-dimensional regular grid with grid nodes stacked in
    1-dimension.

    The grid is stacked along the 'node' dimension.

    """
    x_size = IntegerVariable((), optional=True,
                             description='nb. of nodes in x')
    y_size = IntegerVariable((), optional=True,
                             description='nb. of nodes in y')
    x_length = FloatVariable((), optional=True,
                             description='total grid length in x')
    y_length = FloatVariable((), optional=True,
                             description='total grid length in y')
    x_spacing = FloatVariable((), optional=True,
                              description='node spacing in x')
    y_spacing = FloatVariable((), optional=True,
                              description='node spacing in y')
    x_origin = FloatVariable((), optional=True, default_value=0.,
                             description='grid x-origin')
    y_origin = FloatVariable((), optional=True, default_value=0.,
                             description='grid y-origin')
    x = Variable('x', provided=True)
    y = Variable('y', provided=True)

    class Meta:
        time_dependent = False

    def _validate_grid_params(self, size, length, spacing):
        params = {'size': size, 'length': length, 'spacing': spacing}
        provided_params = {k for k, v in params.items()
                           if np.asscalar(v.value) is not None}

        if provided_params == {'size', 'spacing', 'length'}:
            if (size.value - 1) * spacing.value == length.value:
                provided_params = {'size', 'length'}

        if provided_params == {'size', 'length'}:
            spacing.value = length.value / (size.value - 1)
        elif provided_params == {'spacing', 'length'}:
            size.value = int(length.value / spacing.value)
        elif provided_params == {'size', 'spacing'}:
            length.value = spacing.value * (size.value - 1)
        else:
            raise ValidationError("Invalid combination of size (%d), "
                                  "spacing (%s) and length (%s)"
                                  % (size.value, spacing.value, length.value))

    def validate(self):
        self._validate_grid_params(self.x_size, self.x_length, self.x_spacing)
        self._validate_grid_params(self.y_size, self.y_length, self.y_spacing)

    def initialize(self):
        self.x.value = np.linspace(self.x_origin.value,
                                   self.x_origin.value + self.x_length.value,
                                   self.x_size.value)
        self.y.value = np.linspace(self.y_origin.value,
                                   self.y_origin.value + self.y_length.value,
                                   self.y_size.value)


class BoundaryFacesXY(Process):
    """Boundary conditions where each face of the grid in
    both x and y is considered as a boundary.

    """
    x_size = ForeignVariable(StackedGridXY, 'x_size')
    y_size = ForeignVariable(StackedGridXY, 'y_size')
    active_nodes = Variable(('y', 'x'), provided=True)

    class Meta:
        time_dependent = False

    def initialize(self):
        mask = np.ones((self.y_size.value, self.x_size.value), dtype=bool)
        bound_indexers = [0, -1, (slice(None), 0), (slice(None), -1)]

        for idx in bound_indexers:
            mask[idx] = False

        self.active_nodes.value = mask


class TotalErosion(Process):
    """Sum of all (vertical) erosion processes."""

    erosion = Variable(('y', 'x'), provided=True)
    erosion_vars = VariableGroup('erosion')

    def run_step(self, *args):
        self.erosion.state = sum((v.state for v in self.erosion_vars))


class TotalRockUplift(Process):
    """Sum of all (vertical) rock uplift processes."""

    uplift = Variable(('y', 'x'), provided=True)
    uplift_vars = VariableGroup('uplift')

    def run_step(self, *args):
        self.uplift.state = sum((v.state for v in self.uplift_vars))


class Topography(Process):
    """Topography evolution resulting from the balance between
    total rock uplift and total erosion.

    This process has also two diagnostics available:
    topographic slope and curvature.

    """
    elevation = FloatVariable(('y', 'x'), description='topographic elevation')
    total_erosion = ForeignVariable(TotalErosion, 'erosion')
    total_uplift = ForeignVariable(TotalRockUplift, 'uplift')

    def initialize(self):
        self.elevation_change = np.zeros_like(self.elevation.state)

    def run_step(self, *args):
        self.elevation_change = (
            self.total_uplift.state - self.total_erosion.state)

    def finalize_step(self):
        self.elevation.state += self.elevation_change

    @diagnostic
    def slope(self):
        """topographic slope"""
        raise NotImplementedError()

    @diagnostic({'units': '1/m'})
    def curvature(self):
        """topographic curvature"""
        raise NotImplementedError()


class FlowRouterD8(Process):
    """Compute flow receivers using D8 and also compute the node
    ordering stack following Braun and Willet method.

    """
    pit_method = Variable((), default_value='mst_linear')

    x_size = ForeignVariable(StackedGridXY, 'x_size')
    y_size = ForeignVariable(StackedGridXY, 'y_size')
    x_spacing = ForeignVariable(StackedGridXY, 'x_spacing')
    y_spacing = ForeignVariable(StackedGridXY, 'y_spacing')
    active_nodes = ForeignVariable(BoundaryFacesXY, 'active_nodes')
    elevation = ForeignVariable(Topography, 'elevation')

    receivers = Variable(('y', 'x'), provided=True)
    dist2receivers = Variable(('y', 'x'), provided=True)
    ndonors = Variable(('y', 'x'), provided=True)
    donors = Variable(('y', 'x', 'd8'), provided=True)
    stack = Variable(('y', 'x'), provided=True)
    basins = Variable(('y', 'x'), provided=True)
    outlets = Variable(('y', 'x'), provided=True)
    pits = Variable(('y', 'x'), provided=True)

    def initialize(self):
        nx = self.x_size.value.item()
        ny = self.y_size.value.item()
        nnodes = ny * nx
        self.nnodes = nnodes

        self._receivers = np.arange(nnodes, dtype=np.intp)
        self._dist2receivers = np.zeros(nnodes)

        self._ndonors = np.zeros(nnodes, dtype=np.uint8)
        self._donors = np.empty((nnodes, 8), dtype=np.intp)
        self._stack = np.empty(nnodes, dtype=np.intp)
        self._basins = np.empty(nnodes, dtype=np.intp)
        self._outlets = np.empty(nnodes, dtype=np.intp)
        self._pits = np.empty(nnodes, dtype=np.intp)

        self._elevation = self.elevation.state.ravel()
        self._active_nodes = self.active_nodes.value.ravel()

        self.receivers.value = self._receivers.reshape((ny, nx))
        self.dist2receivers.value = self._dist2receivers.reshape((ny, nx))

        self.ndonors.value = self._ndonors.reshape((ny, nx))
        self.donors.value = self._donors.reshape((ny, nx, 8))
        self.stack.value = self._stack.reshape((ny, nx))
        self.basins.value = self._basins.reshape((ny, nx))
        self.outlets.value = self._outlets.reshape((ny, nx))
        self.pits.value = self._pits.reshape((ny, nx))

        if self.pit_method.value == 'no_resolve':
            self.correct_receivers = False
        else:
            self.correct_receivers = True

        self._nbasins = 0
        self._npits = 0

    def run_step(self, *args):
        flow_routing.reset_receivers(self._receivers, self.nnodes)
        flow_routing.compute_receivers_d8(
            self._receivers, self._dist2receivers,
            self._elevation,
            self.x_size.value.item(), self.y_size.value.item(),
            self.x_spacing.value.item(), self.y_spacing.value.item())
        flow_routing.compute_donors(self._ndonors, self._donors,
                                    self._receivers, self.nnodes)
        flow_routing.compute_stack(self._stack,
                                   self._ndonors, self._donors,
                                   self._receivers,
                                   self.nnodes)

        self._nbasins = flow_routing.compute_basins(
            self._basins, self._outlets,
            self._stack, self._receivers, self.nnodes)
        self._npits = flow_routing.compute_pits(
            self._pits, self._outlets, self._active_nodes, self._nbasins)

        if self.correct_receivers and self._npits:
            flow_routing.correct_flowrouting(
                self._receivers, self._dist2receivers,
                self._ndonors, self._donors,
                self._stack, self._nbasins, self._basins,
                self._outlets,
                self._active_nodes, self._elevation,
                self.x_size.value.item(), self.y_size.value.item(),
                self.x_spacing.value.item(), self.y_spacing.value.item(),
                method=self.pit_method.value)
            self._nbasins = flow_routing.compute_basins(
                self._basins, self._outlets,
                self._stack, self._receivers, self.nnodes)

    # TODO: add `dims` argument to @diagnostic in xarray-simlab
    # @diagnostic
    # def nbasins(self):
    #     return self._nbasins

    # @diagnostic
    # def npits(self):
    #     return self._npits

    # @diagnostic
    # def outlets_mask(self):
    #     mask = np.zeros(self.nnodes, dtype=bool)
    #     mask[self.outlets.value[:self._nbasins]] = True
    #     return mask

    # @diagnostic
    # def pits_mask(self):
    #     mask = np.zeros(self.nnodes, dtype=bool)
    #     mask[self.pits.value[:self._npits]] = True
    #     return mask


class PropagateArea(Process):
    """Compute drainage area."""

    dx = ForeignVariable(StackedGridXY, 'x_spacing')
    dy = ForeignVariable(StackedGridXY, 'y_spacing')
    receivers = ForeignVariable(FlowRouterD8, 'receivers')
    stack = ForeignVariable(FlowRouterD8, 'stack')
    area = Variable(('y', 'x'), provided=True, description='drainage area')

    def initialize(self):
        self.grid_cell_area = self.dx.value * self.dy.value
        self.area.state = np.empty(self.receivers.state.shape)

        self._area = self.area.state.ravel()
        self._receivers = self.receivers.value.ravel()
        self._stack = self.stack.value.ravel()

    def run_step(self, *args):
        self._area[:] = self.grid_cell_area
        flow_routing.propagate_area(self._area, self._stack, self._receivers)


class StreamPower(Process):
    """Compute channel erosion using the stream power law."""

    k_coef = FloatVariable((), description='stream-power constant')
    m_exp = FloatVariable((),
                          description='stream-power drainage area exponent')
    n_exp = FloatVariable((), description='stream-power slope exponent')
    erosion = Variable(('y', 'x'), provided=True, group='erosion')

    receivers = ForeignVariable(FlowRouterD8, 'receivers')
    dist2receivers = ForeignVariable(FlowRouterD8, 'dist2receivers')
    stack = ForeignVariable(FlowRouterD8, 'stack')
    area = ForeignVariable(PropagateArea, 'area')
    elevation = ForeignVariable(Topography, 'elevation')

    def initialize(self):
        self.tolerance = 1e-3
        self.nnodes = self.elevation.value.size
        self.erosion.state = np.zeros_like(self.elevation.state)

        self._erosion = self.erosion.state.ravel()
        self._receivers = self.receivers.value.ravel()
        self._dist2receivers = self.dist2receivers.value.ravel()
        self._stack = self.stack.value.ravel()
        self._area = self.area.value.ravel()
        self._elevation = self.elevation.state.ravel()

    def run_step(self, dt):
        # TODO: check xarray-simlab issue #15
        bedrock_channel.erode_spower(
            self._erosion, self._elevation,
            self._stack, self._receivers,
            self._dist2receivers, self._area,
            self.k_coef.value.item(),
            self.m_exp.value.item(),
            self.n_exp.value.item(),
            dt, self.tolerance, self.nnodes)


class LinearDiffusion(Process):
    """Compute hillslope erosion as linear diffusion process."""

    k_coef = FloatVariable((), description='diffusivity')
    erosion = Variable(('y', 'x'), provided=True, group='erosion')
    elevation = ForeignVariable(Topography, 'elevation')
    dx = ForeignVariable(StackedGridXY, 'x_spacing')
    dy = ForeignVariable(StackedGridXY, 'y_spacing')
    nx = ForeignVariable(StackedGridXY, 'x_size')
    ny = ForeignVariable(StackedGridXY, 'y_size')

    def initialize(self):
        self.erosion.state = np.zeros_like(self.elevation.state)

    def run_step(self, dt):
        # TODO: check xarray-simlab issue #15
        hillslope_erosion.erode_linear_diffusion(
            self.erosion.state, self.elevation.state,
            self.k_coef.value.item(), dt,
            self.dx.value.item(), self.dy.value.item(),
            self.nx.value.item(), self.ny.value.item())


class BlockUplift(Process):
    """Compute block uplift."""

    u_coef = FloatVariable([(), ('y', 'x')], description='uplift rate')
    active_nodes = ForeignVariable(BoundaryFacesXY, 'active_nodes')
    uplift = Variable((), provided=True, group='uplift')

    def initialize(self):
        self.mask = self.active_nodes.value
        self.uplift.state = np.zeros_like(self.mask, dtype='f')

    def run_step(self, dt):
        u_rate = self.u_coef.value
        # TODO: check xarray-simlab issue #15
        if u_rate.ndim:
            u_rate = u_rate[self.mask]

        self.uplift.state[self.mask] = u_rate * dt


fastscape_base_model = Model(
    {'grid': StackedGridXY,
     'boundaries': BoundaryFacesXY,
     'block_uplift': BlockUplift,
     'flow_routing': FlowRouterD8,
     'area': PropagateArea,
     'spower': StreamPower,
     'diffusion': LinearDiffusion,
     'erosion': TotalErosion,
     'uplift': TotalRockUplift,
     'topography': Topography}
)
