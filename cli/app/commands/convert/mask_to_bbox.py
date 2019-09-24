import click

from app.models import types
from app.settings import app_cfg
from app.utils import click_utils

@click.command()
@click.option('-i', '--input', 'opt_dir_in', required=True,
  help='Path to project folder (metadata.csv, mask, real)')
@click.option('-f', '--force', 'opt_force', is_flag=True,
  help='Force overwrite annotations file')
@click.option('--width', 'opt_width', default=320,
  help='Image width to process mask at (over 320 is slow)')
@click.pass_context
def cli(ctx, opt_dir_in, opt_force, opt_width):
  """Converts image, masks, and metadata to CSV annotations"""
  
  from os.path import join
  from glob import glob
  from pathlib import Path
  from dataclasses import asdict
  import logging

  import pandas as pd
  import cv2 as cv
  import numpy as np
  from tqdm import tqdm

  from app.utils import file_utils, color_utils, anno_utils

  # init log
  log = app_cfg.LOG
  log.info('Converting masks to annotations')

  # init
  records = []

  # output file
  fp_annotations = join(opt_dir_in, 'annotations.csv')
  if Path(fp_annotations).exists() and not opt_force:
    log.error(f'File exists: {fp_annotations}. Use "-f/--force" to overwrite')
    return

  # load the color coded CSV
  fp_metadata = join(opt_dir_in, app_cfg.FN_METADATA)
  df_objects = pd.read_csv(fp_metadata)
  log.info(f'Metadata file contains {len(df_objects):,} objects')

  # glob mask
  fp_dir_im_reals = join(opt_dir_in, app_cfg.DN_REAL)
  fp_dir_im_masks = join(opt_dir_in, app_cfg.DN_MASK)
  fps_reals = glob(join(fp_dir_im_reals, '*.png'))
  fps_masks = glob(join(fp_dir_im_masks, '*.png'))
  if len(fps_masks) != len(fps_reals):
    log.warn(f'Directories not balanced: {len(fps_masks)} masks != {len(fps_real)}')
  
  log.info(f'Converting {len(fps_masks)} mask images to annotations...')

  # iterate through all images
  for fp_mask in tqdm(fps_masks):
    fn_mask = Path(fp_mask).name
    im_mask = cv.imread(fp_mask)
    w, h = im_mask.shape[:2][::-1]
    scale = opt_width / w
    im_mask_sm = cv.resize(im_mask, None, fx=scale, fy=scale, interpolation=cv.INTER_NEAREST)

    # flatten image and find unique colors
    im_mask_sm_rgb = cv.cvtColor(im_mask_sm, cv.COLOR_BGR2RGB)
    w_sm, h_sm = im_mask_sm.shape[:2][::-1]
    im_flat_rgb = im_mask_sm_rgb.reshape((w_sm * h_sm, 3))
    rgb_unique = np.unique(im_flat_rgb, axis=0)

    # iterate through all colors for all objects
    for df in df_objects.itertuples():
      # if the color is found in the image with a large enough area, append bbox
      rgb_int = (df.color_r, df.color_g, df.color_b)  # RGB uint8
      found = any([(rgb_int == tuple(c)) for c in rgb_unique])
      if found:
        color_hex = f'0x{color_utils.rgb_int_to_hex(rgb_int)}'
        bbox_norm = anno_utils.color_mask_to_rect(im_mask_sm_rgb, rgb_int)
        if bbox_norm:
          bbox_nlc = bbox_norm.to_labeled(df.label, df.label_index, fn_mask).to_colored(color_hex)
          records.append(asdict(bbox_nlc))

  # Convert to dataframe
  df_annos = pd.DataFrame.from_dict(records)

  # write CSV
  df_annos.to_csv(fp_annotations, index=False)

  # status
  log.info(f'Wrote {len(df_annos)} annotations to {fp_annotations} ')

