"""
This is a Blender Python script
- run from inside Blender or using Blender as CLI application
"""

import os
import sys
import time
import importlib
import logging
import shlex

import argparse
from tqdm import tqdm, trange


# -------------------------------------------------------------------
# initialize
# -------------------------------------------------------------------

# Parse CLI args
if '--' in sys.argv:
  
  # build argument parser
  parser = argparse.ArgumentParser(description='Blender generator arguments')
  parser.add_argument('--cfg', dest='opt_fp_cfg', 
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

else:
  print('Error. Incomplete arguments to run script.')
  sys.exit()

# append sys paths
print(args.opt_dir_root)
sys.path.append(args.opt_dir_root)

# imports
from app.utils import log_utils

# create logger
log_utils.Logger.create(verbosity=args.opt_verbosity)
log = log_utils.Logger.getLogger()
log.debug('it works!')


# -------------------------------------------------------------------
# Reload imports if files change because Blender holds modules in memory

import bpy

from app.utils import file_utils, sys_utils
from app.utils.file_utils import zpad
from app.blender.operators.boss import Boss

# logger
log_utils.Logger.create()  # initialize
log = log_utils.Logger.getLogger()

# signal handler
sigint = sys_utils.SignalInterrupt()

# Debug
log.info(f'Running: {os.path.basename(__file__)}')
log.debug(f'Config : {args.opt_fp_cfg}')
log.debug(f'Resume checkpoint: {args.opt_checkpoint}')


# init manager
st = time.time()
boss = Boss(args.opt_fp_cfg)

# iterate data generate systems
for particle_idx in trange(args.opt_checkpoint, boss.object_system.iterations, desc='Emitter'):
  if sigint.interrupted:
    sys.exit('Signal interrupted. Exiting.')

  boss.object_system.randomize()
  boss.object_system.make_real()

  for cam_idx in trange(boss.camera.num_iterations, desc='Camera', leave=False):
    if sigint_interrupt: break

    boss.camera.set_cam_idx(cam_idx)

    num_frames = boss.camera.num_view_frames(cam_idx)
    for cam_rot_iter in trange(1, num_frames + 1, desc='Angle', leave=False):
      if sigint_interrupt: break

      boss.camera.set_rotation_idx(cam_rot_iter)
      boss.camera.focus(jitter=True)

      #boss.ground.randomize()
      boss.world.randomize()

      # real
      fname = f'emitter_{zpad(particle_idx)}_cam_{zpad(cam_idx)}_{zpad(cam_rot_iter)}'
      if boss.render.save_real:
        if boss.render.save_mask:
          boss.unmask()  # redundant
        fp_out = boss.fileio.build_fp_out(f'real/{fname}')
        boss.render.render(fp_out)

      # masked
      if boss.render.save_mask:
        boss.mask()
        fp_out = boss.fileio.build_fp_out(f'mask/{fname}')
        boss.render.render(fp_out)

      dg = bpy.context.evaluated_depsgraph_get()
      dg.update()


  boss.object_system.unmask()
  boss.object_system.clear_real()