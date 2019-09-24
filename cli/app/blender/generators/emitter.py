"""
This is a Blender Python script
- run from inside Blender or using Blender as CLI application
"""

import os
import sys
import signal
import time
import importlib
import logging

import argparse
from tqdm import tqdm, trange

os.environ.setdefault('DIR_VFRAME_SYNTHETIC', '/work/vframe_synthetic/cli')
DIR_VFRAME_SYNTHETIC = os.getenv('DIR_VFRAME_SYNTHETIC')
sys.path.append(DIR_VFRAME_SYNTHETIC)

# -------------------------------------------------------------------
# initialize
# -------------------------------------------------------------------

# Get YAML config file
resume_particle_iter = 0
fp_cfg = '/work/vframe_synthetic/cli/configs/ars_blu63_01.yml'  # Edit

if '--' in sys.argv:
  args = sys.argv[sys.argv.index("--") + 1:]
  # config 
  if len(args) > 0 and 'yml' in args[0]:
    fp_cfg = args[0]
  # resume point
  if len(args) > 1:
    resume_particle_iter = int(args[1])
  # if len(args) > 2:
    # idx_gpu = str(args[2])
    # idx_gpu = 1
    #log.debug(f'Setting CUDA_VISIBLE_DEVICES = {idx_gpu}')
    # os.environ['CUDA_VISIBLE_DEVICES'] = idx_gpu


# -------------------------------------------------------------------
# Reload imports if files change because Blender holds modules in memory

import bpy

from app import utils  # reload
importlib.reload(utils)
from app.blender.operators import boss  # reload
importlib.reload(boss)

# aliases
utils.log_utils.Logger.create()
log = utils.log_utils.Logger.getLogger()
zpad = utils.file_utils.zpad


# Debug
log.info(f'Running: {os.path.basename(__file__)}')
log.debug(f'Config file: {fp_cfg}')
log.debug(f'resume_particle_iter: {resume_particle_iter}')
st = time.time()

# init manager
boss = boss.Boss(fp_cfg)

# add signal interrrupts to terminate script early
sigint_interrupt = False
def signal_handler(sig, frame):
  global sigint_interrupt
  sigint_interrupt = True
  log.warn('Gracefully exiting')

signal.signal(signal.SIGINT, signal_handler)
log.info('Press Ctrl+C to quit')


# -------------------------------------------------------------------
# render
# -------------------------------------------------------------------
if True:
  for particle_idx in trange(resume_particle_iter, boss.object_system.iterations, desc='Emitter System'):
    if sigint_interrupt: break

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
    
    # for block in bpy.data.meshes:
    #   if block.users == 0:
    #     bpy.data.meshes.remove(block)

    # for block in bpy.data.materials:
    #   if block.users == 0:
    #     bpy.data.materials.remove(block)

    # for block in bpy.data.textures:
    #   if block.users == 0:
    #     bpy.data.textures.remove(block)

    # for block in bpy.data.images:
    #   if block.users == 0:
    #     bpy.data.images.remove(block)


    # for block in bpy.data.curves:
    #   if block.users == 0:
    #     D.curves.remove(block)
    #bpy.ops.outliner.orphans_purge()



# -------------------------------------------------------------------
# cleanup

boss.cleanup()

# -------------------------------------------------------------------
# status udpate

print(f'Done. Elapsed time: {(time.time() - st):.2f} seconds')



# -------------------------------------------------------------------
#
# Headless rendering is not yet supported
# https://devtalk.blender.org/t/blender-2-8-unable-to-open-a-display-by-the-rendering-on-the-background-eevee/1436/17