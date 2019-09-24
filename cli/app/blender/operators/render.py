import os
import sys
from os.path import join
from pathlib import Path
import importlib
import math
import random

import bpy

sys.path.append('/work/vframe_synthetic/vframe_synthetic')
from app.utils import log_utils

# reload application python modules
importlib.reload(log_utils)

# shortcuts
log = log_utils.Logger.getLogger()


# ---------------------------------------------------------------------------
# Mange render settings
# ---------------------------------------------------------------------------

class RenderManager:
  '''Manages the render settings'''
  OPT_FILMIC = 'Filmic'
  OPT_LOOK_MD_CONTRAST = 'Filmic - Medium High Contrast'
  OPT_STANDARD = 'Standard'
  OPT_SRGB = 'sRGB'
  OPT_RAW = 'Raw'
  OPT_NONE = 'None'
  OPT_EEVEE = 'BLENDER_EEVEE'
  OPT_CYCLES = 'CYCLES'
  OPT_DEVICE_GPU = 'GPU'

  def __init__(self, cfg):

    # set scene
    self.scene = bpy.data.scenes[cfg.get('scene').get('name')]

    # TODO: include all settings
    self.cycles_device_default = self.scene.cycles.device
    self.engine_default = self.scene.render.engine 

    cfg_render = cfg.get('render')

    # save options
    self._save_real = cfg_render.get('save_real', True)
    self._save_mask = cfg_render.get('save_mask', True)

    # dimensions
    dimensions = cfg_render.get('dimensions')
    self.scene.render.resolution_x = int(dimensions.get('width'))
    self.scene.render.resolution_y = int(dimensions.get('height'))
    self.scene.render.resolution_percentage = int(float(dimensions.get('scale', 1.0)) * 100)

    # render engine
    engine = cfg_render.get('engine')
    self.engine_mask = engine.get('mask', 'eevee').lower()
    self.engine_real = engine.get('real', 'cycles').lower()
    self.opt_gpu = engine.get('gpu', True)

    # set render prefences
    self.scene.display_settings.display_device = self.OPT_SRGB

    # File format
    render_opts = self.scene.render
    output = cfg_render.get('output')
    render_opts.image_settings.file_format = output.get('file_format', 'PNG')
    render_opts.image_settings.color_mode = output.get('color_mode', 'RGB')
    render_opts.image_settings.compression = int(output.get('compression', 0))
    render_opts.image_settings.color_depth = str(output.get('color_depth', 8))
    render_opts.use_overwrite = output.get('overwrite', True)
    render_opts.use_file_extension = output.get('file_extension', True)
    render_opts.use_placeholder = output.get('placeholders', False)
    render_opts.use_render_cache = output.get('render_cache', False)

    # Color management
    color_mgmt = cfg_render.get('color_management')
    self.color_mgmt = color_mgmt
    self.view_settings = bpy.context.scene.view_settings
    self.display_settings = self.scene.display_settings


  def set_engine_mask(self):
    self.set_engine_eevee()
    self.scene.display_settings.display_device = self.OPT_NONE
    self.scene.view_settings.view_transform = self.OPT_STANDARD
    self.scene.view_settings.look = self.OPT_NONE
    self.scene.sequencer_colorspace_settings.name = self.OPT_RAW
    self.scene.view_settings.use_curve_mapping = False
    self.scene.render.use_sequencer = False
    self.scene.render.dither_intensity = 0
    self.scene.render.filter_size = 0


  def set_engine_real(self):
    if self.engine_real == 'eevee':
      self.set_engine_eevee()
    elif self.engine_real == 'cycles':
      self.set_engine_cycles()

    self.display_settings.display_device = self.OPT_SRGB
    self.view_settings.view_transform = self.OPT_FILMIC
    self.view_settings.look = self.color_mgmt.get('look', self.OPT_LOOK_MD_CONTRAST)
    self.view_settings.use_curve_mapping = True
    self.scene.render.use_sequencer = True
    self.scene.render.dither_intensity = 0.0  # noise setting, externalize
    self.scene.render.filter_size = 1.5
    

  def set_engine_eevee(self):
    self.scene.render.engine = self.OPT_EEVEE


  def set_engine_cycles(self):
    self.scene.render.engine = self.OPT_CYCLES
    if self.opt_gpu:
      self.scene.cycles.device = self.OPT_DEVICE_GPU


  def render(self, fp_out):
    self.scene.render.filepath = fp_out
    # redirect output to log file
    logfile = 'blender_render.log'
    open(logfile, 'a').close()
    old = os.dup(1)
    sys.stdout.flush()
    os.close(1)
    os.open(logfile, os.O_WRONLY)

    # do the rendering
    bpy.ops.render.render(write_still=True)

    # disable output redirection
    os.close(1)
    os.dup(old)
    os.close(old)


  @property
  def save_real(self):
    return self._save_real


  @property
  def save_mask(self):
    return self._save_mask


  def cleanup(self):
    '''Resets render engine to original settings'''
    self.scene.render.engine = self.engine_default
    self.scene.cycles.device = self.cycles_device_default
    # TODO set to original if EEVEE or Cycles
    try:
      self.scene.display_settings.display_device = self.OPT_SRGB
      self.view_settings.view_transform = self.OPT_FILMIC
      bpy.context.scene.render.dither_intensity = 0.75
      bpy.context.scene.render.filter_size = 1.5
      bpy.context.scene.view_settings.look = 'Filmic - Medium Contrast'
    except Exception as e:
      pass