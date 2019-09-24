import sys
from os.path import join
from pathlib import Path
import importlib
import math
import random
import mathutils
from dataclasses import dataclass

import bpy

sys.path.append('/work/vframe_synthetic/vframe_synthetic')
from app.utils import log_utils
importlib.reload(log_utils)


# ---------------------------------------------------------------------------
# Manage camera
# ---------------------------------------------------------------------------

DEFAULT_SENSOR_WIDTH = 36
DEFAULT_JITTER_LOC = (0, 0, 0)
DEFAULT_JITTER_ROT = (0, 0, 0)
DEFAULT_JITTER_TARGET = (0,0,0)
DEFAULT_FOCAL_LENGTH = 50  # lens mm

@dataclass
class CameraView:
  """Variable names match config YAML"""
  height: float
  x_radius: float
  y_radius: float 
  frames: int
  target_xyz: list = (0,0,0)
  zoom: int = DEFAULT_FOCAL_LENGTH
  jitter_location: list = DEFAULT_JITTER_LOC
  jitter_rotation: list = DEFAULT_JITTER_ROT
  jitter_target: list = DEFAULT_JITTER_TARGET
  sensor_width: int = DEFAULT_SENSOR_WIDTH
  target_name: str = None  # overrides xyz

  @property
  def period(cls):
    return int(cls.frames) + 2
  

class CameraManager:

  CAMERA_NAME = 'VFRAME_CAMERA'
  cur_cam_view = None
  cur_cam_rot_iter = 0

  def __init__(self, cfg):

    # init logger
    self.log = log_utils.Logger.getLogger()

    # set scene
    self.scene_name = cfg.get('scene', 'Scene').get('name', 'Scene')  # Default to 'Scene'
    self.scene = bpy.data.scenes.get(self.scene_name)
    if not self.scene:
      log.error(f'Scene "{self.scene_name}" is not available in this file')

    self.scene_obj_names_orig = bpy.context.scene.objects.keys()
    existing_camera_names = bpy.data.cameras.keys()
    cfg_cam = cfg.get('camera')
    self._iterations = len(cfg_cam.get('views', []))
    # store default, debug position
    self.camera_orig = self.scene.camera
    # camera views
    self._cam_views = [CameraView(**x) for x in cfg_cam.get('views', [])]
    # create camera
    bpy.ops.object.camera_add()
    obj_cam_name = str(list(set(bpy.context.scene.objects.keys()) - set(self.scene_obj_names_orig))[0])
    new_camera_names = bpy.data.cameras.keys()
    cam_name = str(list(set(new_camera_names) - set(existing_camera_names))[0])
    self.obj_camera_new = bpy.data.objects.get(obj_cam_name)
    self.camera_new = bpy.data.cameras.get(cam_name)
    self.camera_new.name = self.CAMERA_NAME
    self.obj_camera_new.name = self.CAMERA_NAME
    # activate new camera
    self.set_camera(self.obj_camera_new)


  def set_cam_idx(self, cam_idx):
    """Sets Blender Camera to new CamView defined in YAML config"""
    self.cam_idx = cam_idx

  def set_rotation_idx(self, cam_rot_iter):
    self.cur_cam_rot_iter = cam_rot_iter
  
  def set_rotation_random(self):
    """Randomly sets a rotation from selected camera"""
    nframes = self._cam_views[self.cam_idx].frames
    rr = random.randint(0, nframes - 1)
    self.cur_cam_rot_iter = rr

  def set_camera_random(self):
    """Randomly sets a rotation from selected camera"""
    self.cam_idx = random.randint(0, len(self._cam_views) - 1)

  def set_random(self):
    """Sets random camera and rotation frame"""
    self.set_camera_random()
    self.set_rotation_random()

  def focus(self, jitter=False):
    '''Sets current camera position'''
    self.cam_view = self._cam_views[self.cam_idx]
    self.set_lens_mm(self.cam_view.zoom)
    self.set_sensor_width(self.cam_view.sensor_width)
    if self.cam_view.frames == 1:
      # update location
      nframes = self.cam_view.frames + 1
      x = self.cam_view.x_radius
      y = self.cam_view.y_radius
      z = self.cam_view.height
    else:
      # update location
      nframes = self.cam_view.frames + 1
      z = self.cam_view.height
      # TODO add custom range
      x = self.cam_view.x_radius * math.cos((self.cur_cam_rot_iter / nframes) * 2 * math.pi)
      y = self.cam_view.y_radius * math.sin((self.cur_cam_rot_iter / nframes) * 2 * math.pi)
      #z = math.atan2(y, x) + math.pi / 2
    self.set_location((x, y, z), jitter=jitter)
    # update rotation
    if self.cam_view.target_name:
      self.look_at_target(self.cam_view.target_name, jitter=jitter)
    else:
      self.look_at_xyz(self.cam_view.target_xyz, jitter=jitter)

  def set_camera(self, camera):
    '''Sets the current scene camera'''
    self.scene.camera = camera


  def set_x(self, x):
    '''Sets the X value of location'''
    (_, y, z) = self.obj_camera_new.location
    self.set_location((x,y,z))


  def set_y(self, y):
    '''Sets the Y value of location'''
    (x, _, z) = self.obj_camera_new.location
    self.set_location((x,y,z))


  def set_z(self, z):
    '''Sets the Z value of location'''
    (x, y, _) = self.obj_camera_new.location
    self.set_location((x,y,z))


  def set_location(self, xyz, jitter=False):

    self.obj_camera_new.location = xyz
    if jitter:
      self.jitter_location()
    # update dep graph
    # TODO: not sure where this should be called yet
    # see: https://blender.stackexchange.com/questions/140789/what-is-the-replacement-for-scene-update
    dg = bpy.context.evaluated_depsgraph_get()
    dg.update()


  def set_rotation(self, xyz, jitter=False):
    '''Sets camera rotation in Euler XYZ'''
    self.obj_camera_new.rotation_euler = xyz
    if jitter:
      self.jitter_rotation()
    # TODO: not sure where this should be called yet
    # see: https://blender.stackexchange.com/questions/140789/what-is-the-replacement-for-scene-update
    dg = bpy.context.evaluated_depsgraph_get()
    dg.update()


  def set_lens_mm(self, mm):
    '''Sets Camera lens zoom in millimeters'''
    self.obj_camera_new.data.lens = mm


  def set_sensor_width(self, width):
    '''Sets Camera sensor width in mm'''
    self.obj_camera_new.data.sensor_width = width  # sensor size mm


  def jitter_all(self):
    '''Applies rotation and location jitter'''
    # first jitter location
    self.jitter_location()
    # look at target again
    if self.cam_view.target_name:
      self.look_at_target(self.cam_view.target_name, jitter=True)
    else:
      self.look_at_xyz(self.cam_view.target_xyz, jitter=True)
    # then jitter rotation
    #self.jitter_rotation()


  def jitter_rotation(self):
    '''Applies randomness to the rotation'''
    xyz = self.jitter_xyz(self.obj_camera_new.rotation_euler, self.cam_view.jitter_location)
    self.set_rotation(xyz)


  def jitter_location(self):
    '''Applies randomness to the location'''
    xyz = self.jitter_xyz(self.obj_camera_new.location, self.cam_view.jitter_location)
    self.set_location(xyz)


  def jitter_xyz(self, xyz, delta):
    return [random.uniform(_xyz - _delta, _xyz + _delta) for _xyz, _delta in zip(xyz, delta)]

  
  def look_at_xyz(self, xyz, jitter=False):
      '''Orients camera towards XYZ coords'''
      xyz_targ = mathutils.Vector(xyz)
      if jitter:
        xyz_targ = self.jitter_xyz(xyz_targ, self.cam_view.jitter_target)
        xyz_targ = mathutils.Vector(xyz_targ)
      xyz_source = self.obj_camera_new.matrix_world.to_translation()
      direction = xyz_source - xyz_targ
      # point the cameras '-Z' and use its 'Y' as up
      rot_euler = direction.to_track_quat('Z', 'Y').to_euler()
      self.set_rotation(rot_euler)


  def look_at_target(self, target_name, jitter=False):
      '''Orients camera towards target object'''
      #xyz_targ = target_obj.matrix_world.to_translation()
      xyz_targ = bpy.data.objects.get(target_name).location
      if jitter:
        xyz_targ = self.jitter_xyz(xyz_targ, self.cam_view.jitter_target)
        xyz_targ = mathutils.Vector(xyz_targ)
      xyz_source = self.obj_camera_new.matrix_world.to_translation()
      direction = xyz_source - xyz_targ
      # point the cameras '-Z' and use its 'Y' as up
      rot_euler = direction.to_track_quat('Z', 'Y').to_euler()
      self.set_rotation(rot_euler)


  def cleanup(self):
    '''Restores scene to existing camera'''
    if self.CAMERA_NAME in bpy.data.objects.keys():
     bpy.data.objects.remove(bpy.data.objects.get(self.CAMERA_NAME))
    if self.CAMERA_NAME in bpy.data.cameras.keys():
      bpy.data.cameras.remove(bpy.data.cameras.get(self.CAMERA_NAME))

  
  
  def num_view_frames(self,  idx):
    """Retruns number of frames viewable for this camera index"""
    return self._cam_views[idx].frames

  # ---------------------------------------------------------------------
  # Properties
  # ---------------------------------------------------------------------


  @property
  def num_iterations(self):
    return self._iterations

  @property
  def cam_views(self):
    return self._cam_views
  
