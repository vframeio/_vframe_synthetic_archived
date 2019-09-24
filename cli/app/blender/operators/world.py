import sys
from os.path import join
from pathlib import Path
import importlib
import math
import random

import bpy

sys.path.append('/work/vframe_synthetic/cli')
from app.utils import log_utils, color_utils
# reload application python modules
importlib.reload(log_utils)
importlib.reload(color_utils)
from app.blender.materials import colorfill
importlib.reload(colorfill)

# shortcuts
log = log_utils.Logger.getLogger()
ColorFillWorld = colorfill.ColorFillWorld


# ---------------------------------------------------------------------------
# Manage World object
# ---------------------------------------------------------------------------


class WorldManager:

  bg_images = {}
  node_mask_name = 'NODE_WORLD_BG_COLOR'
  node_orig = None
  node_active = None

  def __init__(self, cfg):
    
    # get world
    world_cfg = cfg.get('world')
    self.name_world = world_cfg.get('name', 'World')
    self.world = bpy.data.worlds.get(self.name_world)
    self.nodes = self.world.node_tree.nodes
    self.links = self.world.node_tree.links
    # setup world output nodes
    self.node_out = self.nodes.get(world_cfg.get('output', 'World Output'))
    self.node_out_link_id = self.node_out.inputs['Surface']
    # get mapping node for adjusting rotation values
    self.node_mapping = self.nodes.get('Mapping')  # Default name of Mapping nodes
    if not self.node_mapping:
      log.warn(f'No "Mapping" World node. Unable to rotate background.')
    # setup render opts
    self.rotations = world_cfg.get('rotations')
    self.environments = world_cfg.get('backgrounds', [])
    self.environment_texture_node = self.nodes.get('Environment Texture')
    self.jitter = world_cfg.get('jitter')

    # TODO this may cause errors
    # create temporary mask node and add to scene
    mat_name = f'mat_world_mask'
    if not mat_name in bpy.data.worlds.keys():
      color = color_utils.rgb_packed_to_rgba_norm(world_cfg.get('color', 0x000000))
      cfm = ColorFillWorld(mat_name, color)
    self.material_mask_name = mat_name
    self.material_default_name = self.name_world


    # store reference to user's current active background
    for link in self.links:
      if link.to_node.name == self.node_out.name:
        try:
          self.node_orig = link.from_node
          self.node_orig_link_id = self.node_orig.outputs['Background']
          self.node_active = self.node_orig
          self.node_active_link_id = self.node_active.outputs['Background']
        except Exception as e:
          log.error(f'{e}')


  def remove_cur_output(self):
    # find node currently linked to world output and store ref
    for link in self.links:
      if link.to_node.name == self.node_out.name:
        self.links.remove(link)

  
  def set_rotation_idx(self, idx):
    '''Rotates the background image by degrees to alter lighting'''
    deg = self.rotations[idx]
    self.set_rotation_deg(deg)
    

  def set_rotation_deg(self, deg):
    '''Rotates the background image by degrees to alter lighting'''
    try:
      self.node_mapping.rotation[2] = math.radians(deg)
    except Exception as e:
      #log.warning(f'Could not rorate self.node_mapping')
      pass


  def set_environment(self, idx):
    '''Connects image backgroud node to world output'''
    self.environment_texture_node.image = bpy.data.images.get(self.environments[idx])


  def randomize(self):
    """Randomizes world material and angle"""
    self.set_environment(random.randint(0, len(self.environments) - 1))
    self.set_rotation_deg(random.randint(0, 360))


  def mask(self):
    '''Converts World into black background for masked render'''
    bpy.context.scene.world = bpy.data.worlds.get(self.material_mask_name)
    #self.remove_cur_output()


  def unmask(self): 
    ''''Resets World material to original'''
    # relink
    #self.links.new(self.node_orig_link_id, self.node_out_link_id)
    bpy.context.scene.world = bpy.data.worlds.get(self.material_default_name)


  def cleanup(self):
    '''Removes temporary nodes and restores previous settings'''
    if self.node_orig is not None:
      self.remove_cur_output()
      self.links.new(self.node_orig_link_id, self.node_out_link_id)
    # delete temp node
    #self.nodes.remove(self.node_mask)
    # delete colorfill mask
    if self.material_mask_name in bpy.data.worlds.keys():
      bpy.data.worlds.remove(bpy.data.worlds.get(self.material_mask_name))

    # reset to orig material
    bpy.context.scene.world = bpy.data.worlds.get(self.material_default_name)


  @property
  def num_environments(self):
    return len(self.environments)


  @property
  def num_rotations(self):
    return len(self.rotations)
