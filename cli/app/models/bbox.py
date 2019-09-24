"""
VFRAME BBox classes. Used in all VFRAME repos
"""

import random
import math
from dataclasses import dataclass

# ---------------------------------------------------------------------------
#
# Point classes
#
# ---------------------------------------------------------------------------

@dataclass
class Point:
  x: float
  y: float

  def distance(self, p):
    dx = self.x - p.x
    dy = self.y - p.y
    return int(math.sqrt(math.pow(dx, 2) + math.pow(dy, 2)))


@dataclass
class PointNorm(Point):
  x: float
  y: float


@dataclass
class PointDim(Point):
  x: int
  y: int


# ---------------------------------------------------------------------------
#
# Bounding Box base class
#
# ---------------------------------------------------------------------------

@dataclass
class BBox:
  x1: float
  y1: float
  x2: float
  y2: float

  @property
  def w(self):
    return (self.x2 - self.x1)
  
  @property
  def width(self):
    return self.w

  @property
  def h(self):
    return (self.y2 - self.y1)
  
  @property
  def height(self):
    return self.h

  @property
  def area(self):
    return self.w * self.h
  
  @property
  def p1(self):
    return PointNorm(self.x1, self.y1)

  @property
  def p2(self):
    return PointNorm(self.x2, self.y2)

  @property
  def xyxy(self):
    return (self.x1, self.y1, self.x2, self.y2)
  
  @property
  def xywh(self):
    return (self.x1, self.y1, self.w, self.h)

  def to_bbox_labeled(self, label, label_index, color, fn):
    return BBoxLabeled(self.x1, self.y1, self.x2, self.y2, label, label_index, color, fn)
  
  def jitter(self, per):
    '''Jitters the center xy and the wh of BBox
    :returns (BBoxNorm) jittered
    '''
    amtw = per * self.w
    amth = per *self.h
    w = self.w + (self.w * random.uniform(-amtw, amtw))
    h = self.h + (self.h * random.uniform(-amth, amth))
    cx = self.cx + (self.cx * random.uniform(-amtw, amtw))
    cy = self.cy + (self.cy * random.uniform(-amth, amth))
    x1, y1 = np.clip((cx - w/2, cy - h/2), 0.0, 1.0)
    x2, y2 = np.clip((cx + w/2, cy + h/2), 0.0, 1.0)
    return BBox(x1, y1, x2, y2)

  def contains_point(self, p):
    '''Checks if this BBox contains the normalized point
    :param p: (Point)
    :returns (bool)
    '''
    return (p.x >= self.x1 and p.x <= self.x2 and p.y >= self.y1 and p.y <= self.y2)

  def contains_bbox(self, b):
    '''Checks if this BBox fully contains another BBox
    :param b: (BBox)
    :returns (bool)
    '''
    return (b.x1 >= self.x1 and b.x2 <= self.x2 and b.y1 >= self.y1 and b.y2 <= self.y2)

  @property
  def cx(self):
    pass

  @property
  def cy(self):
    pass

  # TODO
  def to_square(self):
    pass

  def to_expanded(self):
    pass

  @classmethod
  def translate(self, xyxy):
    pass

  
# ---------------------------------------------------------------------------
#
# Bounding Box normalized coords
#
# ---------------------------------------------------------------------------


@dataclass
class BBoxNorm:
  
  x1: float
  y1: float
  x2: float
  y2: float

  @property
  def cx(self):
    return self.x1 + (self.width / 2)

  @property
  def cy(self):
    return self.y1 + (self.height / 2)

  # TODO
  def to_square(self):
    pass

  def to_expanded(self):
    pass

  @classmethod
  def translate(self, xyxy):
    x1, y1, x2, y2 = xyxy
    xyxy = (self.x1 + x1, self.y1 + y1, self.x2 + x, self.y2 + y2)
    xyxy = [min(1.0, max(0.0, a)) for a in xyxy]
    return cls(*xyxy)

  def expand_per(self, per):
    """Expands BBox by percentage
    :param per: (float) percentage to expand 0.0 - 1.0
    :returns (BBoxNorm) expanded
    """
    dw, dh = [(self.w * per), (self.h * per)]
    x1, y1, x2, y2 = list(np.array(self._rect) + np.array([-dw, -dh, dw, dh]))
    # threshold expanded rectangle
    x1 = max(x1, 0.0)
    y1 = max(y1, 0.0)
    x2 = min(x2, 1.0)
    y2 = min(y2, 1.0)
    return BBoxNorm(x1, y1, x2, y2)

  def to_bbox_dim(self, dim):
    w,h = dim
    x1,y1,x2,y2 = list(map(int, (self.x1 * w, self.y1 * h, self.x2 * w, self.y2 * h)))
    return BBoxDim(x1, y1, x2, y2, dim)

  def to_labeled(self, label, label_index, fn):
    return BBoxNormLabel(self.x1, self.y1, self.x2, self.y2, label, label_index, fn)

  @classmethod
  def from_bbox_dim(cls, rd):
    w,h = rd.dim
    x1,y1,x2,y2 = list(map(int, (rd.x1 / w, rd.y1 / h, rd.x2 / w, rd.y2 / h)))
    return cls(x1, y1, x2, y2)
  
  @classmethod
  def from_xywh(cls, xywh):
    x, y, w, h = xywh
    x1, y1, x2, y2 = (x, y, x + w, y + h)
    return cls(x1, y1, x2, y2)

  @classmethod
  def from_cxcywh(cls, cxcywh):
    cx, cy, w, h = cxcywh
    x1 = cx - w/2
    y1 = cy - h/2
    x2 = cx + w/2
    y2 = cy + h/2
    return cls(x1, y1, x2, y2)



# ---------------------------------------------------------------------------
#
# Bounding Box with dimension
#
# ---------------------------------------------------------------------------

@dataclass
class BBoxDim(BBoxNorm):
  
  x1: int
  y1: int
  x2: int
  y2: int  
  dim: (int, int)

  @property
  def cx(self):
    return int(self.x1 + (self.width // 2))

  @property
  def cy(self):
    return int(self.y1 + (self.height // 2))

  @classmethod
  def translate(self, xyxy):
    w,h = self.dim
    x1, y1, x2, y2 = xyxy
    x1 = max(0, min(w, self.x1 + x1))
    y1 = max(0, min(h, self.y1 + y1))
    x2 = max(0, min(w, self.x2 + x2))
    y2 = max(0, min(h, self.y2 + y2))
    return cls(x1, y1, x2, y2, self.dim)

  # TODO
  def to_square(self):
    pass

  def to_expanded(self):
    pass

  def as_bbox_norm(self):
    w,h = self.dim
    x1,y1,x2,y2 = (self.x1 / w, self.y1 / h, self.x2 / w, self.y2 / h)
    return BBoxNorm(x1, y1, x2, y2)
  
  def to_expanded(self, ltrb, redistribute=True):
    """Expands BBox by number of pixels
    :param box: (tuple) left, top, right, bottom
    :returns (BBoxDim) in pixel dimensions
    """
    print('Not yet implemented')


  def to_labeled(self, label, label_index, fn):
    return BBoxDimLabel(label, label_index, fn)

  @classmethod
  def from_bbox_norm(cls, rn, dim):
    w,h = dim
    x1,y1,x2,y2 = list(map(int, (rn.x1 * w, rn.y1 * h, rn.x2 * w, rn.y2 * h)))
    return cls(x1, y1, x2, y2, dim)

  @classmethod
  def from_xywh_dim(cls, xywh, dim):
    x,y,w,h = xywh
    return cls(x, y, x + w, y + h, dim)


@dataclass
class BBoxNormLabel(BBoxNorm):
  '''Represent general BBox'''
  label: str
  label_index: int
  filename: str

  def to_colored(self, color_hex):
    return BBoxNormLabelColor(self.x1, self.y1, self.x2, self.y2, 
      self.label, self.label_index, self.filename, color_hex)

@dataclass
class BBoxDimLabel(BBoxDim):
  '''Represent general BBox info
  '''
  label: str
  label_index: int
  filename: str

  def to_colored(self, color_hex):
    return BBoxDimLabelColor(self.x1, self.y1, self.x2, self.y2, 
      self.label, self.label_index, self.filename, color_hex)

@dataclass
class BBoxNormLabelColor(BBoxNormLabel):
  '''Represent BBox info from pixel masks as norm floats. 
  Used for Blender mask annotations
  '''
  color: str

@dataclass
class BBoxDimLabelColor(BBoxDimLabel):
  '''Represent BBox info from pixel masks as int. 
  Used for Blender mask annotations
  '''
  color: str


