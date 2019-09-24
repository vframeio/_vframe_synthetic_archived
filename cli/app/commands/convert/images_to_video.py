"""
Generates a composite video for preview to show color overlaps on synethic images
"""

import click

from app.models import types
from app.settings import app_cfg
from app.utils import click_utils


@click.command()
@click.option('-i', '--input', 'opt_dir_in', required=True)
@click.option('-o', '--output', 'opt_fp_out')
@click.option('--fps', 'opt_fps', type=int, default=24, help='Frames per second')
@click.option('--ext', 'opt_ext', default='png', help='ext to glob')
@click.option('--bitrate', 'opt_bitrate', default=16, type=float, help='Video bitrate (Mbp/s')
@click.option('--mp4_codec', 'opt_codec', default='libx264', help='Video bitrate (Mbp/s')
@click.option('--slice', 'opt_slice', type=(int, int), default=(None, None),
  help='Slice list of files')
@click.option('--random', 'opt_random', is_flag=True,
  help='Randomize list')
@click.option('-f', '--force', 'opt_force', is_flag=True,
  help='Force overwrite video file')
@click.pass_context
def cli(ctx, opt_dir_in, opt_fp_out, opt_fps, opt_bitrate, opt_codec, opt_ext, 
  opt_slice, opt_random, opt_force):
  """Converts still image sequence to video"""
  
  from glob import glob
  from pathlib import Path
  import random

  import cv2 as cv
  import numpy as np
  import blend_modes
  from moviepy.editor import VideoClip
  from tqdm import tqdm
  from app.utils import file_utils

  log = app_cfg.LOG
  log.info('Generating movie file')

  if not opt_fp_out:
    opt_fp_out = str(Path(opt_dir_in).parent / f'{Path(opt_dir_in).name}.mp4')
    if Path(opt_fp_out).is_dir() and not opt_force:
      log.error(f'{opt_fp_out} exists. Use "-f/--force" to overwrite')

  # glob comp images  
  fps_im = sorted([im for im in glob(str(Path(opt_dir_in) / f'*.{opt_ext}'))])
  if opt_slice:
    fps_im = fps_im[opt_slice[0]:opt_slice[1]]

  if opt_random:
    random.shuffle(fps_im)

  opt_bitrate = f'{opt_bitrate}M'  # megabits / second
  num_frames = len(fps_im)
  duration_sec = num_frames / opt_fps

  def make_frame(t):
    #global fps_im
    frame_idx = int(np.clip(np.round(t * opt_fps), 0, num_frames - 1))
    fp_im = fps_im[frame_idx]
    im = cv.cvtColor(cv.imread(fp_im), cv.COLOR_BGR2RGB)  # Moviepy uses RGB
    return im

  log.info('Generating movieclip...')
  VideoClip(make_frame, duration=duration_sec).write_videofile(opt_fp_out, fps=opt_fps, codec=opt_codec, bitrate=opt_bitrate)
  log.info('Done.')