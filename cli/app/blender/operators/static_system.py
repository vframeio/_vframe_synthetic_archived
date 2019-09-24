
import sys
from os.path import join
from pathlib import Path
import importlib
import math
import random
from dataclasses import dataclass

import bpy

import numpy as np

sys.path.append('/work/vframe_synthetic/cli')
# reload application python modules for Blender
from app.utils import log_utils, color_utils
importlib.reload(log_utils)
importlib.reload(color_utils)
from app.blender.materials import colorfill
importlib.reload(colorfill)


# shortcuts
log = log_utils.Logger.getLogger()
ColorFillMaterial = colorfill.ColorFillMaterial


# ---------------------------------------------------------------------------
# Static System Manager
# ---------------------------------------------------------------------------

@dataclass
class SceneObjectMetadata:
  """Variable names match config YAML"""
  name: str
  material: str
  trainable: bool
  description: str = ''
  label: str = ''
  color: int = 0x000000
  label_index: int = None
  trainable: bool = False
  material_slots: list = None

  @property
  def rgba_norm(self):
    return color_utils.rgb_packed_to_rgba_norm(self.color)

  @property
  def material_mask(self):
    return f'{self.material}_cf'

  
class SceneObject:

  def __init__(self, metadata):
    self.metadata = metadata
    # if orphan colorfill exists, override with new
    if metadata.material_mask in bpy.data.materials.keys():
      _mat_cf_tmp = bpy.data.materials.get(metadata.material_mask)
      bpy.data.materials.remove(_mat_cf_tmp)
    # generate new colorfill material. Data is stored in blender. Discard var
    _mat_cf_tmp = ColorFillMaterial(metadata.material_mask, metadata.rgba_norm)
    # init metadata material slots
    scene_obj = bpy.data.objects.get(self.metadata.name)
    self.material_slots = [ms.material for ms in scene_obj.material_slots]

  def mask(self):
    """Switches material to colorfill mask material name"""
    scene_obj = bpy.data.objects.get(self.metadata.name)
    mat_cf = bpy.data.materials.get(self.metadata.material_mask)
    scene_obj.active_material = mat_cf
    mat_slots = self.material_slots
    for i in range(len(self.material_slots)):
      scene_obj.material_slots[i].material = mat_cf


  def unmask(self):
    """Switches material to default material name"""
    scene_obj = bpy.data.objects.get(self.metadata.name)
    mat_real = bpy.data.materials.get(self.metadata.material)
    scene_obj.active_material = mat_real
    mat_slots = self.material_slots
    for i in range(len(self.material_slots)):
      scene_obj.material_slots[i].material = self.material_slots[i]


  def cleanup(self):
    """Rests objects to original settings
    """
    self.unmask()


  def as_annotation(self):
    """Returns metadata formatted for CSV"""
    return self.metadata



class StaticSystem:

  _annotation_meta = []
  _scene_objects = []

  def __init__(self, cfg):
    # find max number of trainable objects
    self.cfg = cfg
    cfg_sys = self.cfg.get('static_system')
    n_trainable = sum(1 for o in cfg_sys.get('objects') if o.get('trainable', False))
    color_range = color_utils.create_palette_rgba(n_trainable)  # allocate color spectrum

    for idx, o in enumerate(cfg_sys.get('objects')):
      meta = SceneObjectMetadata(**o)
      if meta.trainable:
        # use dynamically allocated color
        rgba_norm = color_range[idx]
        meta.color = color_utils.rgba_norm_to_packed_int(rgba_norm)
        rgba_int = [int(x * 255) for x in rgba_norm]
      else:
        # use fixed color
        rgba_int = color_utils.rgb_packed_to_rgba_norm(o.get('color', 0x000000))

      o['color'] = rgba_int
      self._scene_objects.append(SceneObject(meta))


  def get_annotation_meta(self):
    """Returns annotation metadata"""

    annotation_meta = []
    s = self.cfg.get('static_system', {})
    for obj_idx, o in enumerate(s.get('objects')):
      if o.get('trainable'):
        name = o.get('name')
        log.debug(f'name: {name}')
        label = o.get('label', None)
        label_index = o.get('label_index', None)
        if label_index is None or label is None:
          log.error(f'"label_index" and "label" missing for {namel}. Skipped.')
          continue
        description = o.get('description', 'Default description')
        rgba = o.get('color')  # dynamically allocated color
        r,g,b = rgba[:3]
        log.debug(f'rgb: {r}, {g}, {b}')
        anno_obj = {
          'color_r':r,
          'color_g': g,
          'color_b':b,
          'description': description,
          'label': label,
          'label_index': label_index,
          'mat_idx': 0,  # only used for emitter
          'object_idx': obj_idx,
          }
        annotation_meta.append(anno_obj)
    return annotation_meta


  def mask(self):
    for o in self._scene_objects:
      o.mask()


  def unmask(self):
    for o in self._scene_objects:
      o.unmask()


  def cleanup(self):
    for o in self._scene_objects:
      o.cleanup()