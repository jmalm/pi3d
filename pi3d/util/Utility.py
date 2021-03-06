import copy
import math
import numpy
import bisect

from numpy import sqrt, sin, cos, tan, subtract, dot

from pi3d.constants import *
from pi3d.util.Ctypes import c_bytes

RECT_NORMALS = c_bytes((0, 0, -1,
                        0, 0, -1,
                        0, 0, -1,
                        0, 0, -1))

RECT_TRIANGLES = c_bytes((3, 0, 1,
                          3, 1, 2))

def rect_triangles():
  opengles.glDrawElements(GL_TRIANGLES, 6, GL_UNSIGNED_BYTE, RECT_TRIANGLES)

# TODO: not exact sure what this does but we do it a lot.
def texture_min_mag():
  for f in [GL_TEXTURE_MIN_FILTER, GL_TEXTURE_MAG_FILTER]:
    opengles.glTexParameterf(GL_TEXTURE_2D, f, ctypes.c_float(GL_LINEAR))

def sqsum(*args):
  """Return the sum of the squares of its arguments.

  DEPRECATED:  use numpy.dot(x, x).
  """
  return numpy.dot(args, args)

def magnitude(*args):
  """Return the magnitude (root mean square) of the vector."""
  return numpy.sqrt(numpy.dot(args, args))

def distance(v1, v2):
  """Return the distance between two points."""
  return magnitude(*subtract(v2, v1))

def from_polar(direction=0.0, magnitude=1.0):
  """
  Convert polar coordinates into Cartesian (x, y) coordinates.

  Arguments:

  *direction*
    Vector angle in degrees.
  *magnitude*
    Vector length.
  """
  return from_polar_rad(math.radians(direction), magnitude)

def from_polar_rad(direction=0.0, magnitude=1.0):
  """
  Convert polar coordinates into Cartesian (x, y) coordinates.

  Arguments:

  *direction*
    Vector angle in radians.
  *magnitude*
    Vector length.
  """
  return magnitude * numpy.cos(direction), magnitude * numpy.sin(direction)

def load_identity():
  opengles.glLoadIdentity()

def dotproduct(x1, y1, z1, x2, y2, z2):
  """Return the dot product of two 3-dimensional vectors given by coordinates.
  """
  return x1 * x2 + y1 * y2 + z1 * z2

def crossproduct(x1, y1, z1, x2, y2, z2):
  """Return the cross product of two 3-dimensional vectors given by coordinates.
  """
  return y1 * z2 - z1 * y2, z1 * x2 - x1 * z2, x1 * y2 - y1 * x2

def translate_matrix(vec):
  """Return a matrix that translates by the given vector."""
  m = [[0] * 4] * 4
  for i in range(4):
    m[i][i] = 1.0
  for i in range(3):
    m[3][i] = vec[i]
  return m

def vec_sub(x, y):
  """Return the difference between two vectors."""
  return [a - b for a, b in zip(x, y)]

def vec_dot(x, y):
  """Return the dot product of two vectors."""
  return sum(a * b for a, b in zip(x, y))

def vec_cross(a,b):
  """Return the cross product of two vectors."""
  return [a[1] * b[2] - a[2] * b[1],
          a[2] * b[0] - a[0] * b[2],
          a[0] * b[1] - a[1] * b[0]]

def vec_normal(vec):
  """Return a vector normalized to unit length for a vector of non-zero length,
  otherwise returns the original vector."""
  n = sqrt(sum(x ** 2 for x in vec)) or 1
  return [x / n for x in vec]

def billboard_matrix():
  """Return a matrix that copies x, y and sets z to 0.9."""
  return [[1.0, 0.0, 0.0, 0.0],
          [0.0, 1.0, 0.0, 0.0],
          [0.0, 0.0, 0.0, 0.0],
          [0.0, 0.0, 0.9, 1.0]]

# TODO: We should use numpy for all of these.
def mat_mult(x, y):
  """Return the product of two 4x4 matrices."""
  return [[sum(x[i][j] * y[j][k] for j in range(4))
          for k in range(4)]
          for i in range(4)]

def mat_transpose(x):
  """Return the transposition of a 4x4 matrix."""
  return [[x[k][i] for k in range(4)] for i in range(4)]

def vec_mat_mult(vec, mat):
  """Return the product of a 4-d vector and a 4x4 matrix.

  Arguments:
    *vec*
      A vector of length 4.
    *mat*
      A 4x4 matrix.

  """
  return [sum(vec[j] * mat[j][k] for j in range(4)) for k in range(4)]

def transform(matrix, x, y, z, rx, ry, rz, sx, sy, sz, cx, cy, cz):
  """
  Rotate, scale and translate a 4x4 matrix.

  Arguments:
    *matrix*
      A 4x4 matrix to transform.
    *x, y, z*
      Translation in x, y and z axes.
    *rx, ry, rx*
      Rotations in x, y, and x axes.
    *sx, sy, sz*
      Scale factor in x, y, z axes.
    *cx, cy, cz*
      Center of the rotation.
  """
  # TODO: do we really need this?  Wouldn't the separate parts suffice?
  #
  # TODO: the idea of translating then scaling then performing an inverse
  # translation seems like it wouldn't work?
  #

  matrix = copy.deepcopy(matrix)
  # TODO: is a copy really needed?  Surely translate returns a new matrix?

  matrix = translate(matrix, (x - cx, y - cy, z - cz))
  matrix = rotate(matrix, rx, ry, rz)
  if sx != 1.0 or sy != 1.0 or sz != 1.0:
    matrix = scale(matrix, sx, sy, sz)
  return translate(matrix, (cx, cy, cz))

def scale(matrix, sx, sy, sz):
  """
  Scale a 4x4 matrix.

  Arguments:
    *sx, sy, sz*
      Scale factor in x, y, z axes.
  """
  return mat_mult([[sx, 0, 0, 0],
                   [0, sy, 0, 0],
                   [0, 0, sz, 0],
                   [0, 0, 0, 1]], matrix)

def translate(matrix, vec):
  """
  Translate a 4x4 matrix by a 3-vector

  Arguments:
    *matrix*
      The 4x4 matrix to translate.
    *vec*
      A 3-vector translation in x, y, z axes.
  """
  return mat_mult([[1, 0, 0, 0],
                   [0, 1, 0, 0],
                   [0, 0, 1, 0],
                   [vec[0], vec[1], vec[2], 1]], matrix)

def rotate(matrix, rx, ry, rz):
  """
  Rotate a 4x4 matrix.

  Arguments:
    *matrix*
      A 4x4 matrix.
    *rx, ry, rx*
      Rotations in x, y, and x axes.
  """
  if rz:
    matrix = rotateZ(matrix, rz)
  if rx:
    matrix = rotateX(matrix, rx)
  if ry:
    matrix = rotateY(matrix, ry)
  return matrix

def rotateX(matrix, angle):
  """
  Rotate a 4x4 matrix around the x axis.

  Arguments:
    *matrix*
      A 4x4 matrix.
    *angle*
      Angle of rotation around the x axis.
  """
  angle = math.radians(angle)
  c = cos(angle)
  s = sin(angle)
  return mat_mult([[1, 0, 0, 0],
                   [0, c, s, 0],
                   [0, -s, c, 0],
                   [0, 0, 0, 1]],
                  matrix)

def rotateY(matrix, angle):
  """
  Rotate a 4x4 matrix around the y axis.

  Arguments:
    *matrix*
      A 4x4 matrix.
    *angle*
      Angle of rotation around the y axis.
  """
  angle = math.radians(angle)
  c = numpy.cos(angle)
  s = numpy.sin(angle)
  return mat_mult([[c, 0, -s, 0],
                   [0, 1, 0, 0],
                   [s, 0, c, 0],
                   [0, 0, 0, 1]],
                  matrix)

def rotateZ(matrix, angle):
  """
  Rotate a 4x4 matrix around the z axis.

  Arguments:
    *matrix*
      A 4x4 matrix.
    *angle*
      Angle of rotation around the z axis.
  """
  angle = math.radians(angle)
  c = numpy.cos(angle)
  s = numpy.sin(angle)
  return mat_mult([[c, s, 0, 0],
                   [-s, c, 0, 0],
                   [0, 0, 1, 0],
                   [0, 0, 0, 1]],
                  matrix)

# TODO: this next one is also not used in the codebase.

def angle_between(x1, y1, x2, y2, x3, y3):
  """
  Return the angle between two 3-vectors, or 0.0 if one or the other vector is
  empty.

  Arguments:
    *x1, y1, z1*
      The coordinates of the first vector.
    *x2, y2, z2*
      The coordinates of the second vector.
  """
  a = x2 - x1
  b = y2 - y1
  c = x2 - x3
  d = y2 - y3

  sqab = sqrt(a * a + b * b)
  sqcd = sqrt(c * c + d * d)
  l = sqab * sqcd
  if l == 0.0:
    return 0.0

  aa = (a * c + b * d) / l
  if aa == -1.0:
    return math.pi
  if aa == 0.0:
    return math.pi / 2
    # TODO: this was originally 0!  But if two vectors have a dot product
    # of zero, they are surely at right angles?

  dist = (a * y3 - b * x3  +  x1 * b - y1 * a) / sqab
  angle = acos(aa)

  if dist > 0.0:
    return math.pi / 2.0 - angle
  else:
    return angle

def draw_level_of_detail(here, there, mlist):
  """
  Level Of Detail checking and rendering.  The shader and texture information
  must be set for all the buf objects in each model before draw_level_of_detail
  is called.

  Arguments:
    *here*
      An (x, y, z) tuple or array of view point.
    *there*
      An (x, y, z) tuple or array of model position.
    *mlist*
      A list of (distance, model) pairs with increasing distance, e.g.::

        [[20, model1], [100, model2], [250, None]]

      draw_level_of_detail() selects the first model that is more distant than
      the distance between the two points *here* and *there*, falling back to
      the last model otherwise.  The model None is not rendered and is a good
      way to make sure that nothing is drawn past a certain distance.
  """
  dist = distance(here, there)

  index = bisect.bisect_left(mlist, [dist, None])
  model = mlist[min(index, len(mlist) - 1)][1]
  model.position(there[0], there[1], there[2])
  model.draw()

"""
# TODO: None of these functions is actually called in the codebase.

def ctype_resize(array, new_size):
  resize(array, sizeof(array._type_) * new_size)
  return (array._type_ * new_size).from_address(addressof(array))

def showerror():
  return opengles.glGetError()

def limit(x, below, above):
  return max(min(x, above), below)

def angle_vecs(x1, y1, x2, y2, x3, y3):
  a = x2 - x1
  b = y2 - y1
  c = x2 - x3
  d = y2 - y3

  sqab = magnitude(a, b)
  sqcd = magnitude(c, d)
  l = sqab * sqcd
  if l == 0.0:  # TODO: comparison between floats.
    l = 0.0001
  aa = ((a * c) + (b * d)) / l
  if aa == -1.0:  # TODO: comparison between floats.
    return math.pi
  if aa == 0.0:   # TODO: comparison between floats.
    return 0.0
  dist = (a * y3 - b * x3 + x1 * b - y1 * a) / sqab
  angle = math.acos(aa)

  if dist > 0.0:
    return math.pi * 2 - angle
  else:
    return angle

def calc_normal(x1, y1, z1, x2, y2, z2):
  dx = x2 - x1
  dy = y2 - y1
  dz = z2 - z1
  mag = magnitude(dx, dy, dz)
  return (dx / mag, dy / mag, dz / mag)

def rotate(rotx, roty, rotz):
  # TODO: why the reverse order?
  rotatef(rotz, 0, 0, 1)
  rotatef(roty, 0, 1, 0)
  rotatef(rotx, 1, 0, 0)
"""
