# for alpha shape http://blog.thehumangeo.com/2014/05/12/drawing-boundaries-in-python/
# http://trimesh.readthedocs.io/en/latest/trimesh.html#module-trimesh.base
import numpy as np
import trimesh


class PointCloudSelection(object):
    def __init__(self, vertices, matrix=None):
        self.vertices = vertices
        self.matrix = matrix if matrix is not None else np.eye(4)
        self._density_estimate()
        #self._project()


    def select(self, level, region):
        vertices, triangles = self._isosurface(level)
        mesh = trimesh.Trimesh(vertices, m.triangles)
        meshes = tm.split()
        # find the overlap between all hulls and the region drawn on the screen
        hulls = [self._hull2d(mesh.vertices) for mesh in meshes]
        region = shapely.geometry.Polygon(region)
        areas = [region.intersection(hull) for hull in hulls]
        index = np.argmax(areas)
        mesh = meshes[index]
        mesh.fill_holes()
        mask = mesh.container(self.vertices)
        return mash

    def _hull2d(self, vertices):
        """Return a screen space shapely Polygon (2d) representing the hull of the vertices"""
        vertices2d = self._project(vertices)
        hull = scipy.spatial.ConvexHull(vertices2d)
        x, y = points[hull.vertices,0], points[hull.vertices,1]
        return shapely.geometry.Polygon(zip(x, y))

    def _project(self, vertices):
        """Project into screen shape, from (N,3) to (N,2)"""
        p = np.dot(self.matrix[:3, :3], vertices)
        p += self.matrix[:3,3]
        p /= self.matrix[3,3]
        return p
