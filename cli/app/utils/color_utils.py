"""
Data utility helper methods
"""
import numpy as np
import colorsys
import random

def clamp(x): 
  return max(0, min(x, 255))

def rgb_norm_to_hex(rgb):
  rgb = [(255 * int(x)) for x in rgb]
  return rgb_to_hex(rgb)

def rgba_norm_to_hex(rgba):
  rgb = rgba[:3]
  rgb = [(255 * int(x)) for x in rgb]
  return rgb_to_hex(rgb)

def rgb_norm_to_int(rgb):
  return [int(255. * x) for x in rgb]

def rgba_norm_to_packed_int(rgba):
  r,g,b = rgb_norm_to_int(rgba[:3])
  packed = int('%02x%02x%02x' % (r, g, b), 16)
  return packed

def rgba_to_hsva(rgba):
  """Returns RGB norm value of RGB"""
  r,g,b,a = rgba
  hsva_norm = list(colorsys.rgb_to_hsv(r,g,b)) + [0]  # returns normalized HSV
  return hsva_norm

def rgb_int_to_hex(rgb):
  r,g,b = rgb
  return "{0:02x}{1:02x}{2:02x}".format(clamp(r), clamp(g), clamp(b))

def rgba_to_hex(rgb):
  r,g,b,a = rgba
  return "{0:02x}{1:02x}{2:02x}".format(clamp(r), clamp(g), clamp(b))

def rgba_norm_to_rgb_int(rgb):
  return [int(255. * x) for x in rgb[:3]]


def random_rgba(h=(0,1), s=(0.75,1), v=(0.25,1)):
  hsv = (random.uniform(*h), random.uniform(*s), random.uniform(*v))
  return list(colorsys.hsv_to_rgb(*hsv)) + [1]

def create_palette_rgba(n_colors):
  '''Creates RGB color palette of using full saturation and brightness'''
  hues = np.linspace(0, 1, n_colors + 2)[1:]
  colors = [tuple(list(colorsys.hsv_to_rgb(h, 1, 1)) + [1]) for h in hues]
  return colors

def create_shaded_range_rgba(rgba_norm, n_shades):
  '''Creates a range of shaded values form list of RGBA values'''
  hsva_norm = rgba_to_hsva(rgba_norm)
  h,s,v,a = hsva_norm
  values = np.linspace(1, 0, n_shades + 1)[:-1]
  return [tuple(list(colorsys.hsv_to_rgb(h, 1, v)) + [1]) for v in values]

def rgb_packed_to_rgba_norm(rgbint, alpha=255, as_float=True):
  return rgb_hex_to_rgba(rgbint, alpha=alpha, as_float=True)

def rgb_hex_to_rgba(rgbint, alpha=255, as_float=True):
  color = (rgbint // 256 // 256 % 256, rgbint // 256 % 256, rgbint % 256, alpha)
  if as_float:
    color = [c/255 for c in color]
  return tuple(color)

def hex_str2rgba(hex_val, prefix='0x', as_float=True):
  hex_str = hex_val.replace(prefix, '')
  color = list(bytes.fromhex(hex_str))
  color.append(255)  # alpha
  if as_float:
    color = [c/255 for c in color]
  return color

def rgb_hex_to_rgb(rgbint, as_float=True):
  color = (rgbint // 256 // 256 % 256, rgbint // 256 % 256, rgbint % 256)
  if as_float:
    color = [c/255 for c in color]
  return tuple(color)


def hsv_to_rgb(hsv):
  '''Converts HSV to RGB'''
  h, s, v = hsv
  if s == 0.0: 
    return (v, v, v)
  i = int(h *6. ) # XXX assume int() truncates!
  f = (h*6.)-i
  p, q, t = v * (1. - s), v * (1. - s * f), v * (1. - s * (1. - f))
  i %= 6
  if i == 0: return (v, t, p)
  if i == 1: return (q, v, p)
  if i == 2: return (p, v, t)
  if i == 3: return (p, q, v)
  if i == 4: return (t, p, v)
  if i == 5: return (v, p, q)

def norm_rgb(rgb):
  '''Normalize RGB values'''
  if any(x > 1 for x in rgb):
    return [x/255 for x in rgb]
  else:
    return rgb