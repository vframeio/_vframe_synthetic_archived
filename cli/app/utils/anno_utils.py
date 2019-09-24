"""
Annotation utility helpers
"""

import numpy as np
import cv2 as cv

from app.models.bbox import BBoxNorm, BBoxDim


def color_mask_to_rect(im, color, non_zero_thresh=40):
  '''Converts color masks areas to BBoxes for RGB image
  :param im: (numpy) image in RGB
  :param color: RGB uint8 color tuple
  :param non_zero_threshold: minimum number of non-zero pixels
  :returns (BBoxNorm) or None
  '''
  im_mask = np.zeros_like(im, dtype = "uint8")
  dim = im.shape[:2][::-1]

  indices = np.all(im == color, axis=-1)
  im_mask[indices] = [255, 255, 255]

  im_gray = cv.cvtColor(im_mask, cv.COLOR_RGB2GRAY)
  if cv.countNonZero(im_gray) > non_zero_thresh:
    xywh = cv.boundingRect(im_gray)
    bbox_norm = BBoxDim.from_xywh_dim(xywh, dim).as_bbox_norm()
    return bbox_norm
  else:
    return None


# def fuzz_color(color):
#   '''Adds/Sub one color value in every direction'
#   :param color: color as uint8 (255,255,255)
#   :returns (list) of original plus neighbor colors
#   '''
#   c = list(color).copy()
#   colors = [c]
#   # minus
#   colors.append([max(0, c[0] - 1), c[1], c[2]])  # R-1
#   colors.append([c[0], max(0, c[1] - 1), c[2]])  # G-1
#   colors.append([c[0], c[1], max(0, c[2] - 1)])  # B-1
#   colors.append([max(0, x - 1) if x is not 0 else 0 for x in c])  # RGB-1
#   # add
#   colors.append([min(255, c[0] + 1), c[1], c[2]])  # R+1
#   colors.append([c[0], min(255, c[1] + 1), c[2]])  # R+1
#   colors.append([c[0], c[1], min(255, c[2] + 1)])  # R+1
#   colors.append([min(255, x + 1) if x is not 0 else 0 for x in c])  # R+1
#   return colors
