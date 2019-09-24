import sys
from os.path import join
from pathlib import Path
import importlib
import math
import random

import bpy

sys.path.append('/work/vframe_synthetic/vframe_synthetic')
from app.utils import log_utils, color_utils
importlib.reload(log_utils)
importlib.reload(color_utils)
from app.blender.materials import colorfill
importlib.reload(colorfill)

# reload application python modules

# shortcuts
log = log_utils.Logger.getLogger()
ColorFillMaterial = colorfill.ColorFillMaterial

# ---------------------------------------------------------------------------
# Manage ground
# ---------------------------------------------------------------------------

class GroundManager:
  '''Manages ground material switching'''

  def __init__(self, cfg):
    cfg_ground = cfg.get('ground', {})
    self._iterations = len(cfg_ground.get('materials', []))
    self.ground_materials = cfg_ground.get('materials', [])
    self.ground_objects = self.generate_placeholders(cfg_ground)


  def generate_placeholders(self, cfg):
    '''Generates list of object names in this particle system'''
    placeholders = {}
    for o in cfg.get('objects', []):
      obj_name = o.get('name')
      obj_scene = bpy.data.objects.get(obj_name)
      if not obj_scene:
        log.error(f'{obj_name} is not an object in this scene')
      o['default_material'] = obj_scene.active_material.name
      o['material_slots_defaults'] = [ms.material.name for ms in obj_scene.material_slots]
      o['unmask_material'] = o['default_material']
      # o['ground_materials'] = self.ground_materials
      o['ground_materials'] = o.get('material')
      cf_mat_name = f'mat_{obj_name}_colorfill'
      if not cf_mat_name in bpy.data.materials.keys():
        color = color_utils.rgb_packed_to_rgba_norm(o.get('color', 0x000000))
        cfm = ColorFillMaterial(cf_mat_name, color)
      o['colorfill_material'] = cf_mat_name
      placeholders[obj_name] = o
    return placeholders

  

  def mask(self):
    '''Changes object materials to colorfill'''
    for name, base_obj in self.ground_objects.items():
      mat_name = base_obj.get('colorfill_material')
      cf_mat = bpy.data.materials.get(mat_name)
      obj_scene = bpy.data.objects.get(name)
      obj_scene.active_material = cf_mat
      for ms in obj_scene.material_slots:
        ms.material = cf_mat

  def unmask(self):
    for name, base_obj in self.ground_objects.items():
      mat = bpy.data.materials.get(base_obj.get('unmask_material'))
      obj_scene = bpy.data.objects.get(name)
      obj_scene.active_material = mat
      for i, ms in enumerate(obj_scene.material_slots):
        mat_name = base_obj['material_slots_defaults'][i]
        mat = bpy.data.materials.get(mat_name)
        ms.material = mat

  def set_ground(self, idx):
    for name, base_obj in self.ground_objects.items():
      mat_name = base_obj.get('ground_materials')[idx]
      base_obj['unmask_material'] = mat_name
      bpy.data.objects.get(name).active_material = bpy.data.materials.get(mat_name)

  def randomize(self):
    ridx = random.randint(0, len(self.ground_materials)-1)
    self.set_ground(ridx)

  def cleanup(self):
    '''Reset preferences'''
    for name, base_obj in self.ground_objects.items():
      mat_name = base_obj.get('default_material')
      log.debug(f'restore {name} to {mat_name}')
      bpy.data.objects.get(name).active_material = bpy.data.materials.get(mat_name)
      mat_name_cfg = base_obj.get('colorfill_material')
      if mat_name_cfg in bpy.data.materials.keys():
        bpy.data.materials.remove(bpy.data.materials.get(mat_name_cfg))
  
  @property
  def iterations(self):
    return self._iterations