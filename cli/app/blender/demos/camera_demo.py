"""
This is a Blender Python script
- run from inside Blender or using Blender as CLI application
"""
import sys
import shlex

import argparse


# -------------------------------------------------------------------
# START ArgumentParser block
# this section must copied into any Python file being run from Blender

try:
  parser = argparse.ArgumentParser(description='Blender generator arguments')
  parser.add_argument('--cfg', dest='opt_fp_cfg', required=True, default=None,
    help='Path to .yaml config file')
  parser.add_argument('--root', dest='opt_dir_root', 
    help='Path to vframe_synthetic directory')
  parser.add_argument('--checkpoint', dest='opt_checkpoint', type=int, 
    help='Checkpoint to resume')
  parser.add_argument('--verbosity', dest='opt_verbosity', type=int, 
    default=4, help='Verbosity 1 - 4')

  # parse from string
  args_str = ' '.join(sys.argv[sys.argv.index("--") + 1:])
  args = parser.parse_args(shlex.split(args_str))

  # append sys paths
  sys.path.append(args.opt_dir_root)

except Exception as e:
  print('Error. Incomplete arguments to run script.')
  sys.exit()


# END ArgumentParser block
# -------------------------------------------------------------------


# -------------------------------------------------------------------
# imports

from pathlib import Path

import bpy

from tqdm import tqdm, trange

from app.utils import log_utils, sys_utils
from app.utils.file_utils import zpad, load_yml
from app.blender.operators.render import RenderManager
from app.blender.operators.ground import GroundManager
from app.blender.operators.world import WorldManager
from app.blender.operators.camera import CameraManager
from app.blender.operators.fileio import FileIOManager
from app.blender.operators.static_system import StaticSystem


# -------------------------------------------------------------------
# init

# init logger
log_utils.Logger.create(verbosity=args.opt_verbosity)
log = log_utils.Logger.getLogger()

# init sinnal interrupt handler
sigint = sys_utils.SignalInterrupt()

# error check parsed args
if not Path(args.opt_fp_cfg).is_file():
  log.error(f'"{args.opt_fp_cfg}" is not a valid config file. Exiting.')
  log.info('Add --config argument to generator command')
  sys.exit()

# init hello
log.info(f'Running: {Path(__file__).name}')
log.debug(f'Config : {args.opt_fp_cfg}')
log.debug(f'Resume checkpoint: {args.opt_checkpoint}')

# init yaml
yaml_data = load_yml(args.opt_fp_cfg)

# init managers
render = RenderManager(yaml_data)
world = WorldManager(yaml_data)
ground = GroundManager(yaml_data)
camera = CameraManager(yaml_data)
fileio = FileIOManager(yaml_data)
object_system = StaticSystem(yaml_data)

# generate metadata file, overwrites existing
anno_meta = object_system.get_annotation_meta()
fileio.annos_to_csv(anno_meta)


# -------------------------------------------------------------------
# iterate data generator

for cam_view_idx in trange(camera.num_iterations, desc='Camera', leave=False):
  
  sigint.check()  # Check for signal interrupt to quit during loop
  camera.set_cam_idx(cam_view_idx)  
  num_frames = camera.num_view_frames(cam_view_idx)
  log.debug(f'num_frames: {num_frames}')

  for cam_rot_idx in trange(1, num_frames + 1, desc='Angle', leave=False):

    sigint.check()  # Check for signal interrupt to quit during loop
    camera.set_rotation_idx(cam_rot_idx)
    camera.focus(jitter=False)  # focus camera to target object/xyz
    fname = f'cam_{zpad(cam_view_idx)}_frame_{zpad(cam_rot_idx)}'

    # render real
    if render.save_real:
      render.set_engine_real()
      world.unmask()
      ground.unmask()
      object_system.unmask()
      fp_out = fileio.build_fp_real(fname)
      render.render(fp_out)

    # render mask
    if render.save_mask:
      render.set_engine_mask()
      world.mask()
      ground.mask()
      object_system.mask()
      fp_out = fileio.build_fp_mask(fname)
      render.render(fp_out)

  #bpy.context.evaluated_depsgraph_get().update()
