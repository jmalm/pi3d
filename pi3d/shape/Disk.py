from __future__ import absolute_import, division, print_function, unicode_literals

from math import pi

from pi3d.constants import *
from pi3d.Buffer import Buffer
from pi3d.util import Utility
from pi3d.Shape import Shape

class Disk(Shape):
  """ 3d model inherits from Shape"""
  def __init__(self, camera=None, light=None, radius=1, sides=12, name="", x=0.0, y=0.0, z=0.0,
               rx=0.0, ry=0.0, rz=0.0, sx=1.0, sy=1.0, sz=1.0,
               cx=0.0, cy=0.0, cz=0.0):
    """uses standard constructor for Shape extra Keyword arguments:

      *radius*
        Radius of disk.
      *sides*
        Number of sides to polygon representing disk.
    """
    super(Disk, self).__init__(camera, light, name, x, y, z, rx, ry, rz, sx, sy, sz,
                               cx, cy, cz)

    if VERBOSE:
      print("Creating disk ...")

    self.verts = []
    self.norms = []
    self.inds = []
    self.texcoords = []
    self.ttype = GL_TRIANGLES
    self.sides = sides

    st = 2 * pi / sides
    for j in range(-1, 1):
      self._add_vertex((0.0, -0.1*j, 0.0), (0.0, -j, 0.0), (0.5, 0.5))
      for r in range(sides+1):
        ca, sa = Utility.from_polar_rad(r * st)
        self._add_vertex((radius * sa, 0.0, radius * ca),
                        (0.0, -j - 0.1*j, 0.0), (sa * 0.5 + 0.5, ca * 0.5 + 0.5))
      if j == -1:
        v0, v1, v2 = 0, 1, 2
      else:
        v0, v1, v2 = sides + 2, sides + 4, sides + 3 # i.e. reverse direction to show on back
      for r in range(sides):
        self._add_tri((v0, r + v1, r + v2))

    self.but = []
    self.buf.append(Buffer(self, self.verts, self.texcoords, self.inds, self.norms))

