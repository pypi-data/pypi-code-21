from .data.data import Data
from .units import Units

def radius_of_earth():
    '''

Return a radius of the Earth.

:Returns:

    radius_of_earth: cf.Data

    '''
    return Data(6371229.0, 'meters')

def relative_vorticity(u, v, cyclic=None, one_sided_at_boundary=False):
    '''

Calculate the relative vorticity using centred finite
differences. According to the formula given here:

https://www.ncl.ucar.edu/Document/Functions/Built-in/uv2vr_cfd.shtml

"According to H.B. Bluestein [Synoptic-Dynamic Meteorology in
Midlatitudes, 1992, Oxford Univ. Press p113-114], let D represent the
partial derivative, a the radius of the earth, phi the latitude and
dx2/dy2 the appropriate longitudinal and latitudinal spacing,
respectively. Then, letting j be the latitude y-subscript, and i be
the longitude x-subscript:

    rv = Dv/Dx - Du/Dy + (u/a)*tan(phi)


    rv(j,i) = (v(j,i+1)-v(j,i-1))/dx2(j)
              - (u(j+1,i)-u(j-1,i))/dy2(j)
              + (u(j,i)/a)*tan(phi(j))

The last term accounts for the convergence of the meridians on a
sphere."

The grid may be global or limited area. If missing values are present
then missing values will be returned at points where the centred
finite difference could not be calculated. The boundary conditions may
be cyclic in longitude. The noncyclic boundaries may either be filled
with missing values or calculated with off-centre finite differences.

:Parameters:

    u: cf.Field
        A field containing the x-wind. Must be on the same grid as the
        y-wind.

    v: cf.Field
        A field containing the y-wind. Must be on the same grid as the
        x-wind.

    cyclic: `bool`, optional
        Whether the longitude is cyclic or not. By default this is
        autodetected.

    one_sided_at_boundary: `bool`, optional
        If True then if the field is not cyclic off-centre finite
        differences are calculated at the boundaries, otherwise
        missing values are used at the boundaries.

:Returns:

    rv: cf.Field
        The relative vorticity calculated with centred finite
        differences.

    '''

    # Get the standard names of u and v
    u_std_name = u.getprop('standard_name', None)
    v_std_name = v.getprop('standard_name', None)

    # Copy u and v
    u = u.copy()
    v = v.copy()

    # Get the X and Y coordinates
    (u_x_key, u_y_key), (u_x, u_y) = u._regrid_get_cartesian_coords('u',
                                                                    ('X', 'Y'))
    (v_x_key, v_y_key), (v_x, v_y) = v._regrid_get_cartesian_coords('v',
                                                                    ('X', 'Y'))

    if not u_x.equals(v_x) or not u_y.equals(v_y):
        raise ValueError('u and v must be on the same grid.')
    #--- End: if

    # Check for lat/long
    is_latlong = ((u_x.Units.islongitude and u_y.Units.islatitude) or
                  (u_x.units == 'degrees' and u_y.units == 'degrees'))

    # Check for cyclicity
    if cyclic is None:
        if is_latlong:
            cyclic = u.iscyclic(u_x_key)
        else:
            cyclic = False
        #--- End: if
    #--- End: if

    # Find the relative vorticity
    if is_latlong:
        # Save the units of the X and Y coordinates
        x_units = u_x.Units
        y_units = u_y.Units

        # Change the units of the lat/longs to radians
        u_x.Units = Units('radians')
        u_y.Units = Units('radians')
        v_x.Units = Units('radians')
        v_y.Units = Units('radians')

        # Find cos and tan of latitude
        cos_lat = u_y.cos()
        tan_lat = u_y.tan()

        # Reshape for broadcasting
        u_shape = [1] * u.ndim
        u_y_index = u.data_axes().index(u_y_key)
        u_shape[u_y_index] = u_y.size

        v_shape = [1] * v.ndim
        v_y_index = v.data_axes().index(v_y_key)
        v_shape[v_y_index] = v_y.size

        # Calculate the correction term
        corr = u.copy()
        corr.Data *= tan_lat.array.reshape(u_shape)

        # Calculate the derivatives
        v.derivative(v_x_key, cyclic=cyclic,
                     one_sided_at_boundary=one_sided_at_boundary, i=True)
        v.Data /= cos_lat.array.reshape(v_shape)
        u.derivative(u_y_key, one_sided_at_boundary=one_sided_at_boundary,
                     i=True)

        # Calculate the relative vorticity
        rv = v - u + corr
        a = radius_of_earth()
        rv.Data /= a

        # Convert the units of latitude and longitude to canonical units
        rv.dim('X').Units = x_units
        rv.dim('Y').Units = y_units

    else:
        rv = v.derivative(v_x_key, one_sided_at_boundary=one_sided_at_boundary,
                          i=True) - \
             u.derivative(u_y_key, one_sided_at_boundary=one_sided_at_boundary,
                          i=True)
    #--- End: if

    # Convert the units of relative vorticity to canonical units
    rv.Units = Units('s-1')

    # Set the standard name if appropriate and delete the long_name
    if ((u_std_name == 'eastward_wind' and v_std_name == 'northward_wind') or
        (u_std_name == 'x_wind' and v_std_name == 'y_wind')):
        rv.standard_name = 'atmosphere_relative_vorticity'
    elif rv.hasprop('standard_name'):
        del rv.standard_name
    #--- End: if
    if rv.hasprop('long_name'):
        del rv.long_name
    
    return rv
#--- End: def
