"""
Generates a composite video for preview to show color overlaps on synethic images
"""

import click

from app.settings import app_cfg

@click.command()
@click.option('-i', '--input', 'opt_dir_ims', required=True)
@click.option('-o', '--output', 'opt_fp_out_video',
  help='Path to video output file')
@click.option('--video', 'opt_write_video', is_flag=True,
  help='Writes video to default location as parent directory name MP4"')
@click.option('--fps', 'opt_fps', type=int, default=24, help='Frames per second')
@click.option('--bg', 'opt_bg_color', default=125, type=click.IntRange(0,255),
  help='Background color')
@click.option('--bitrate', 'opt_bitrate', default=16, type=float, help='Video bitrate (Mbp/s')
@click.option('--mp4_codec', 'opt_codec', default='libx264', help='Video bitrate (Mbp/s')
@click.option('--cleanup', 'opt_cleanup', is_flag=True, default=False, show_default=True,
  help='Deletes image sequence files after writing video')
@click.pass_context
def cli(ctx, opt_dir_ims, opt_fps, opt_bitrate, opt_codec, opt_fp_out_video, opt_bg_color, 
  opt_write_video, opt_cleanup):
  """Composites real and mask images, writes optional video"""
  
  import pandas as pd
  from glob import glob
  from pathlib import Path

  import cv2 as cv
  import numpy as np
  import blend_modes
  from moviepy.editor import VideoClip
  from tqdm import tqdm

  from app.utils import log_utils, file_utils

  log = app_cfg.LOG
  log.info('Compositing masks and synthetic 3D images')

  # init
  fps_ims_comp = []

  # glob images
  fps_ims_real = [im for im in glob(str(Path(opt_dir_ims) / app_cfg.DN_REAL / '*.png'))]
  fps_ims_mask = [im for im in glob(str(Path(opt_dir_ims) / app_cfg.DN_MASK / '*.png'))]
  if not len(fps_ims_mask) == len(fps_ims_real):
    print('Error: number images not same')
  print(f'found {len(fps_ims_mask)} masks, {len(fps_ims_real)} images')

  # ensure output dir
  opt_dir_ims_comp = Path(opt_dir_ims) / app_cfg.DN_COMP
  if not Path(opt_dir_ims_comp).is_dir():
    Path(opt_dir_ims_comp).mkdir(parents=True, exist_ok=True)

  # generate image sequence
  for fp_im_mask, fp_im_real in tqdm(zip(fps_ims_mask, fps_ims_real), total=len(fps_ims_real)):
    
    #im_mask = cv.cvtColor(cv.imread(fp_im_mask).astype(np.float32), cv.COLOR_BGR2BGRA)
    im_mask = cv.cvtColor(cv.imread(fp_im_mask), cv.COLOR_BGR2BGRA).astype(np.float32)
    bg_color = np.array([0.,0.,0.,255.])  # black fill
    mask_idxs = np.all(im_mask == bg_color, axis=2)
    im_mask[mask_idxs] = [0,0,0,opt_bg_color]

    im_real = cv.cvtColor(cv.imread(fp_im_real), cv.COLOR_BGR2BGRA).astype(np.float32)
    im_comp = blend_modes.multiply(im_real, im_mask, 0.5)
    im_comp = blend_modes.addition(im_comp, im_mask, 0.5)
    im_comp = cv.cvtColor(im_comp, cv.COLOR_BGRA2BGR)
    fp_out = Path(opt_dir_ims_comp) / Path(fp_im_mask).name
    cv.imwrite(str(fp_out), im_comp)

  if not opt_fp_out_video and opt_write_video:
    opt_fp_out_video = str(Path(opt_dir_ims) / f'{Path(opt_dir_ims).name}.mp4')

  if opt_fp_out_video:
    # glob comp images  
    fps_ims_comp = sorted([im for im in glob(str(Path(opt_dir_ims_comp) / '*.png'))])

    opt_bitrate = f'{opt_bitrate}M'  # megabits / second
    num_frames = len(fps_ims_comp)
    duration_sec = num_frames / opt_fps

    log.debug(f'num images: {len(fps_ims_comp)}')
    def make_frame(t):
      #global fps_ims_comp
      frame_idx = int(np.clip(np.round(t * opt_fps), 0, num_frames - 1))
      fp_im = fps_ims_comp[frame_idx]
      im = cv.cvtColor(cv.imread(fp_im), cv.COLOR_BGR2RGB)  # Moviepy uses RGB
      return im

    log.info(f'Generating movieclip to: {opt_fp_out_video}')
    VideoClip(make_frame, duration=duration_sec).write_videofile(opt_fp_out_video, fps=opt_fps, codec=opt_codec, bitrate=opt_bitrate)
    log.info('Done.')

  if opt_cleanup:
    # remove all comp images
    log.info('Removing all temporary images...')
    import shutil
    shutil.rmtree(opt_dir_ims_comp)
    log.info(f'Deleted {opt_dir_ims_comp}')