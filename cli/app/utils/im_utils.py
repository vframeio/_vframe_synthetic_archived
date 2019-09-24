import logging

import cv2 as cv
from PIL import Image
import imutils
import numpy as np

log = logging.getLogger('VFRAME')

def np2pil(im, swap=True):
  """Ensure image is Pillow format
    :param im: image in numpy or PIL.Image format
    :returns: image in Pillow RGB format
  """
  try:
    im.verify()
    log.warn('Expected Numpy received PIL')
    return im
  except:
    if swap:
      im = bgr2rgb(im)
    return Image.fromarray(im.astype('uint8'), 'RGB')

def pil2np(im, swap=True):
  """Ensure image is Numpy.ndarry format
    :param im: image in numpy or PIL.Image format
    :returns: image in Numpy uint8 format
  """
  if type(im) == np.ndarray:
    log.warn('Expected PIL received Numpy')
    return im
  im = np.asarray(im, np.uint8)
  if swap:
    im = rgb2bgr(im)
  return im

def num_channels(im):
  '''Returns number of channels in numpy.ndarray image'''
  if len(im.shape) > 2:
    return im.shape[2]
  else:
    return 1

def is_grayscale(im, threshold=5):
  """Returns True if image is grayscale
  :param im: (numpy.array) image
  :return (bool) of if image is grayscale"""
  b = im[:,:,0]
  g = im[:,:,1]
  mean = np.mean(np.abs(g - b))
  return mean < threshold



############################################
# imutils (external)
# pip install imutils
############################################

def resize(im, width=0, height=0):
  """resize image using imutils. Use w/h=[0 || None] to prioritize other edge size
    :param im: a Numpy.ndarray image
    :param wh: a tuple of (width, height)
  """
  # TODO change to cv.resize and add algorithm choices
  w = width
  h = height
  if w is 0 and h is 0:
    return im
  elif w > 0 and h > 0:
    ws = im.shape[1] / w
    hs = im.shape[0] / h
    if ws > hs:
      return imutils.resize(im, width=w)
    else:
      return imutils.resize(im, height=h)
  elif w > 0 and h is 0:
    return imutils.resize(im, width=w)
  elif w is 0 and h > 0:
    return imutils.resize(im, height=h)
  else:
    return im



############################################
# OpenCV 
############################################

def bgr2gray(im):
  """Wrapper for cv2.cvtColor transform
    :param im: Numpy.ndarray (BGR)
    :returns: Numpy.ndarray (Gray)
  """
  return cv.cvtColor(im, cv.COLOR_BGR2GRAY)

def gray2bgr(im):
  """Wrapper for cv2.cvtColor transform
    :param im: Numpy.ndarray (Gray)
    :returns: Numpy.ndarray (BGR)
  """
  return cv.cvtColor(im, cv.COLOR_GRAY2BGR)

def bgr2rgb(im):
  """Wrapper for cv2.cvtColor transform
    :param im: Numpy.ndarray (BGR)
    :returns: Numpy.ndarray (RGB)
  """
  return cv.cvtColor(im, cv.COLOR_BGR2RGB)

def rgb2bgr(im):
  """Wrapper for cv2.cvtColor transform
    :param im: Numpy.ndarray (RGB)
    :returns: Numpy.ndarray (RGB)
  """
  return cv.cvtColor(im, cv.COLOR_RGB2BGR)