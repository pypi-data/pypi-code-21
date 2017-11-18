def solid_cylinder(mass_kg, radius_m):
    return 0.5 * mass_kg * radius_m ** 2


def cylinder_about_center(mass_kg, radius_m, length_m):
    return 0.25 * mass_kg * radius_m ** 2 + mass_kg * length_m ** 2 / 12


def solid_sphere(mass_kg, radius_m):
    return 2. / 5 * mass_kg * radius_m ** 2


def thin_spherical_shell(mass_kg, radius_m):
    return 2. / 3 * mass_kg * radius_m ** 2


def rod_about_end(mass_kg, length_m):
    return mass_kg * length_m ** 2 / 3


def parallel_axis(mass_kg, distance_m):
    return mass_kg * distance_m ** 2
