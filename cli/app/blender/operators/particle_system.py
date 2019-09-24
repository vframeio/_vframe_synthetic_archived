
import sys
from os.path import join
from pathlib import Path
import importlib
import math
import random
from dataclasses import dataclass

import bpy

import numpy as np

sys.path.append('/work/vframe_synthetic/vframe_synthetic')
from app.utils import log_utils, color_utils
from app.blender.materials import colorfill

# reload application python modules
importlib.reload(log_utils)
importlib.reload(color_utils)
importlib.reload(colorfill)

# shortcuts
log = log_utils.Logger.getLogger()
ColorFillMaterial = colorfill.ColorFillMaterial


# ---------------------------------------------------------------------------
# Manage Particle Systems
# ---------------------------------------------------------------------------


class ParticleSystem:

  def __init__(self, name_emitter, cfg):

    self.name_emitter = name_emitter
    self.name_particle_settings = cfg.get('settings')  # settings
    self.name_system = cfg.get('name')
    self.range_count = cfg.get('count')
    self.range_seed = cfg.get('seed')
    self.range_hair_length = cfg.get('hair', None)
    self.particle_size = cfg.get('scale')
    self.size_random = cfg.get('scale_randomness')

    if self.name_particle_settings in bpy.data.particles.keys(): 
      self.obj_particle = bpy.data.particles.get(self.name_particle_settings)
    else:
      log.error(f'Particle object "{self.name_particle_settings}" does not exist')
    try:
      self.particle_sys = bpy.data.objects.get(self.name_emitter).particle_systems.get(self.name_system)
    except Exception as e:
      log.error(f'Particle emitter: "{self.name_emitter}", system: {self.name_system} does not exist')

    # set single parameters
    self.obj_particle.size_random = self.size_random
    self.obj_particle.particle_size = self.particle_size

    self.store_defaults()


  def store_defaults(self):
    # keep a copy of default settings
    self.default_count = self.obj_particle.count
    self.default_size_random = self.obj_particle.size_random
    self.default_particle_size = self.obj_particle.particle_size
    #self.default_hair_step = self.obj_particle.hair_step
    self.default_hair_length = self.obj_particle.hair_length
    # particle system
    self.default_seed = self.particle_sys.seed


  def randint_range(self, n):
    '''Returns random int from tuple range'''
    return random.randint(n[0], n[1])

  def random_range(self, n):
    '''Returns random float from tuple range'''
    return random.uniform(n[0], n[1])

  def randomize(self):
    '''Randomize all particle settings in range'''
    r_count = self.randint_range(self.range_count)
    r_seed = self.randint_range(self.range_seed)
    self.obj_particle.count = r_count
    if self.range_hair_length:
      self.obj_particle.hair_step = self.randint_range(self.range_hair_length)
    # particle system
    self.particle_sys.seed = r_seed


  def mask(self):
    '''Hides non-trainable objects from being rendered'''
    for obj in self.partice_sys_settings:
      obj.mask()

  def unmask(self):
    '''Un-hides non-trainable objects'''
    for obj in self.partice_sys_settings:
      obj.unmask()

  def cleanup(self):
    for obj in self.partice_sys_settings:
      obj.cleanup()


  def reset(self):
    '''Restore default settings'''
    # object
    self.obj_particle.count = self.default_count
    # self.obj_particle.hair_step = self.default_hair_step
    self.obj_particle.hair_length = self.default_hair_length
    self.obj_particle.particle_size = self.default_particle_size
    self.obj_particle.size_random = self.default_size_random
    # system
    self.particle_sys.seed = self.default_seed



class Emitter:

  system_objects = {}

  def __init__(self, cfg):
    self.cfg = cfg
    self.name_emitter = self.cfg.get('name')
    self.opt_make_real = cfg.get('make_real')
    self.emitter = bpy.data.objects[self.name_emitter]
    self.trainable = cfg.get('trainable', False)
    self.opt_randomize = self.cfg.get('randomize', False)
    self.systems = [ParticleSystem(self.name_emitter, x) for x in self.cfg.get('systems')]
    

  def set_render_visibility(self, opt):
    '''Enables/disables source objects from being rendered'''
    opt = not opt
    for s in self.cfg.get('systems'):
      for o in s.get('objects'):
        name = o.get('name')
        bpy.data.objects.get(name).hide_render = opt
        #bpy.data.objects.get(name).hide_viewport = opt


  def generate_placeholders(self, cfg):
    '''Generates list of object names in this particle system'''
    placeholders = {}
    for s in cfg:
      for o in s.get('objects'):
        o['duplicates'] = []
        o['meshes'] = []
        o['randomizations'] = []
        placeholders[o.get('name')] = o
    return placeholders


  def randomize(self):
    '''Randomizes all emitter systems'''
    if self.opt_randomize:
      for s in self.systems:
        s.randomize()
  

  def make_real(self):
    
    self.system_objects = self.generate_placeholders(self.cfg.get('systems'))

    if not self.opt_make_real:
      return
    '''Makes duplicates into real objects'''
    # make emitter plane active object
    bpy.context.view_layer.objects.active = self.emitter

    # ensure all objects deselected
    for o in bpy.context.selected_objects:
      o.select_set(False)

    # copy list of names of objects before duplicating
    self.names_objects_orig = bpy.data.objects.keys()

    # add names of scene objects that aren't part of the particle system
    self.names_objects_ignore = [x for x in self.names_objects_orig if x not in self.system_objects.keys()]

    # select target object and convert particle system into objects
    self.emitter.select_set(True)
    bpy.ops.object.duplicates_make_real()
    self.emitter.select_set(False)
    # subtract list of original particle item names from list of all stage items
    self.names_objects = [x for x in bpy.data.objects.keys() if x not in self.names_objects_ignore]

    # subtract the existing object names for off-stage objects
    self.names_new = [x for x in self.names_objects if not any(y == x for y in self.system_objects.keys())]


    for new_obj_name in self.names_new:
      # split name at '.' and match before
      new_obj_stem = Path(new_obj_name).stem
      for base_name, obj in self.system_objects.items():
        # hide the source objects on stage from being rendered
        if new_obj_stem == base_name:
          obj['duplicates'].append(new_obj_name)
          # the duplicate needs a separate mesh object
          meshes = obj['meshes']
          new_mesh = bpy.data.objects.get(new_obj_name).data.copy()  # copy objects data
          new_mesh_name = f'mesh_{new_obj_name}'
          new_mesh.name = new_mesh_name
          bpy.data.objects.get(new_obj_name).data = new_mesh
          meshes.append(new_mesh_name)
          # if the object is a random-jazz items
          if obj.get('randomize_color'):
            rgb_node = bpy.data.materials.get(obj.get('material')).node_tree.nodes.get('RGB')
            rgb_node.outputs.get('Color').default_value = color_utils.random_rgba()

    self.set_render_visibility(False)


  def clear_real(self):
    '''Clears the duplicated objects from the scene/memory'''
    for base_name, obj in self.system_objects.items():
      for dupe_name in obj.get('duplicates', []):
        if dupe_name in bpy.data.objects.keys():
          scene_obj = bpy.data.objects.get(dupe_name)
          bpy.data.objects.remove(scene_obj)
      for mesh_name in obj.get('meshes', []):
        if mesh_name in bpy.data.meshes.keys():
          bpy.data.meshes.remove(bpy.data.meshes.get(mesh_name))
    self.set_render_visibility(True)



  def mask(self):
    if self.opt_make_real:
      self.emitter.hide_render = True
      self.emitter.hide_viewport = True
      for base_name, obj in self.system_objects.items():
        for idx, dupe_name in enumerate(obj.get('duplicates', [])):
          obj_scene = bpy.data.objects.get(dupe_name)
          try:
            material_cf = bpy.data.materials.get(obj.get('materials')[idx])
            obj_scene.active_material = material_cf
            #log.debug(f'set colorfill: {obj_scene.name} --> {obj.get("materials")[idx]}')
            # fill material color slots
            for material_slot in obj_scene.material_slots:
              material_slot.material = material_cf
          except Exception as e:
            log.error(f'No material for {dupe_name}, materials: {obj.get("materials")}')
    else:
      for base_name, obj in self.system_objects.items():
        material_cf = bpy.data.materials.get(obj.get('materials')[0])
        obj_scene = bpy.data.objects.get(base_name)
        obj_scene.active_material = material_cf
        for material_slot in obj_scene.material_slots:
          material_slot.material = material_cf



  def unmask(self):
    '''move this to cleanup?'''
    if self.opt_make_real:
      self.emitter.hide_render = False
      self.emitter.hide_viewport = False
    for base_name, obj in self.system_objects.items():
      if not self.opt_make_real:
        # reset to original material
        obj_scene = bpy.data.objects.get(base_name)
        material = bpy.data.materials.get(obj.get('material'))
        obj_scene.active_material = material
        for i in range(len(obj.get('material_slots'))):          
          mslot = obj.get('material_slots')[i]
          log.debug(f'base_name: {base_name}, material: {material}, mslot: {mslot}')
          obj_scene.material_slots[i].material = obj.get('material_slots')[i]

      if base_name != self.name_emitter:
        obj_scene = bpy.data.objects.get(base_name)
        obj_scene.hide_viewport = False
        obj_scene.hide_render = False
      for idx, dupe_name in enumerate(obj.get('duplicates', [])):
        obj_scene = bpy.data.objects.get(dupe_name)
        material = bpy.data.materials.get(obj.get('material'))
        obj_scene.active_material = material
        for i in range(len(obj.get('material_slots'))):          
          obj_scene.material_slots[i].material = obj.get('material_slots')[i]


  def cleanup(self):
    self.emitter.hide_render = False
    self.emitter.hide_viewport = False
    self.clear_real()
    self.set_render_visibility(True)
    # remove the materials created during init
    for base_name, obj in self.system_objects.items():
      for mat_name in obj.get('materials', []):
        if mat_name in bpy.data.materials.keys():
          bpy.data.materials.remove(bpy.data.materials.get(mat_name))
    # Reset the particle system settings
    for s in self.systems:
      s.reset()



class ParticleSystemManager:
  '''Manages a system of ParticleObjects and Emitter'''

  def __init__(self, cfg):
    
    self.cfg = cfg
    cfg_sys = cfg.get('particle_system', {})
    self._iterations = cfg_sys.get('iterations', 0)
    
    # find max number of trainable objects
    n_trainable = 0
    for e in cfg_sys.get('emitters', []):
      for s in e.get('systems'):
        if s.get('trainable'):
          n_trainable += len(s.get('objects'))


    # allocate color spectrum, appending color list to objects
    color_range_rgba = color_utils.create_palette_rgba(n_trainable)

    for e in cfg_sys.get('emitters', []):
      color_idx_offset = 0
      for s in e.get('systems'):
        count = max(s.get('count')) * len(s.get('objects'))
        for object_idx, o in enumerate(s.get('objects')):
          materials = []
          max_emitter_count = np.max(np.array(s.get('count'), dtype=np.uint16))
          if s.get('trainable'):
            # use color range, creating new color shader materials
            rgba = color_range_rgba[color_idx_offset]  # RGBA norm
            color_idx_offset += 1
            rgba_cf_colors = color_utils.create_shaded_range_rgba(rgba, max_emitter_count)
            # create a color fill material for all possible emitter objects
            for c_idx, rgba_cf_color in enumerate(rgba_cf_colors):
              mat_name = f'{o.get("name")}_colorfill_{c_idx}'
              rgba_cf_color_int = [int(x * 255) for x in rgba_cf_color]
              if not mat_name in bpy.data.materials.keys():
                cfm = ColorFillMaterial(mat_name, rgba_cf_color)
              materials.append(mat_name)
          else:
            # single color material for all
            rgba_cf_color = color_utils.rgb_packed_to_rgba_norm(o.get('color', 0x000000))
            mat_name = f'{o.get("material")}_colorfill'
            im_alpha_name = o.get('image')
            if not mat_name in bpy.data.materials.keys():
              cfm = ColorFillMaterial(mat_name, rgba_cf_color, alpha_image=im_alpha_name)
            rgba_cf_colors = [ rgba_cf_color ] * max_emitter_count
            materials = [mat_name] * count
          # create materials for each color
          o['materials'] = materials
          o['colors'] = rgba_cf_colors
          # store reference to material slots
          scene_obj = bpy.data.objects.get(o.get('name'))
          if not scene_obj:
            log.error(f'Object name: {o.get("name")} does not exist')
            
          o['material_slots'] = [ms.material for ms in scene_obj.material_slots]

    # create emitter objects
    self.emitters = [Emitter(x) for x in cfg_sys.get('emitters', [])]

  
  def get_annotation_meta(self):
    """Returns annotation metadata"""

    annotation_meta = []
    cfg_sys = self.cfg.get('particle_system', {})
    for e in cfg_sys.get('emitters', []):
      for s in e.get('systems'):
        for obj_idx, o in enumerate(s.get('objects')):
          if s.get('trainable'):
            label = o.get('label', 'default_label')
            description = o.get('description', 'default_description')
            label_index = o.get('label_index', None)
            if label_index is None:
              log.error(f'No label_index provided for {label}. Edit YAML')
            for color_idx, rgba in enumerate(o.get('colors')):
              rgb_int = color_utils.rgba_norm_to_rgb_int(rgba)
              r,g,b = rgb_int
              anno_obj = {
                'color_r':r,
                'color_g': g,
                'color_b':b,
                'description': description,
                'label': label,
                'label_index': label_index,
                'mat_idx': color_idx,
                'object_idx': obj_idx,
                }
              annotation_meta.append(anno_obj)

    return annotation_meta


  def randomize(self):
    '''Randomizes all emitter systems'''
    for e in self.emitters:
      e.randomize()

  def make_real(self):
    '''Makes duplicates into real objects'''
    for e in self.emitters:
      if e.make_real:
        e.make_real()

  def clear_real(self):
    '''Removes the temporarily created duplicate objects'''
    for e in self.emitters:
      if e.make_real:
        e.clear_real()

  def mask(self):
    '''Masks all emitter systems'''
    for e in self.emitters:
        e.mask()

  def unmask(self):
    '''Unmasks all emitter systems'''
    for e in self.emitters:
      e.unmask()

  def cleanup(self):
    for e in self.emitters:
      e.cleanup()
  
  
  @property
  def iterations(self):
    return self._iterations
