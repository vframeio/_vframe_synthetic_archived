import sys
import importlib

import bpy

sys.path.append('/work/vframe_synthetic/vframe_synthetic')
from app.utils import log_utils

# reload application python modules
importlib.reload(log_utils)

# shortcuts
log = log_utils.Logger.getLogger()


# ---------------------------------------------------------------------------
# Mange Blender preferences
# ---------------------------------------------------------------------------

class PreferenceManager:
  ''''Manages Blender preferences'''
  preferences = {'edit': {}, 'system': {}}
  # copy original preferences
  #preferences['system']['memory_cache_limit'] = bpy.context.preferences.system.memory_cache_limit
  #preferences['edit']['undo_steps'] = bpy.context.preferences.edit.undo_steps
  #preferences['edit']['undo_memory_limit']= bpy.context.preferences.edit.undo_memory_limit


  def __init__(self, cfg):

    cfg_prefs = cfg.get('preferences', {})

    # Enable CUDA
    if cfg_prefs.get('cuda'):
      try:
        bpy.context.preferences.addons['cycles'].preferences.compute_device_type = 'CUDA'
      except Exception as e:
        log.info('Warning: CUDA is not available')

    # update to render preferences
    #bpy.context.preferences.system.memory_cache_limit = cfg_prefs.get('memory_cache_limit', 4096)  # 16GB
    #bpy.context.preferences.edit.undo_steps = cfg_prefs.get('undo_steps', 1)  # limit undo steps
    #bpy.context.preferences.edit.undo_memory_limit = cfg_prefs.get('undo_memory_limit', 16000)
      

  def cleanup(self):
    '''Reset preferences'''
    pass
    #bpy.context.preferences.system.memory_cache_limit = self.preferences['system']['memory_cache_limit']
    #bpy.context.preferences.edit.undo_memory_limit = self.preferences['edit']['undo_memory_limit']
    #bpy.context.preferences.edit.undo_steps = self.preferences['edit']['undo_steps']
