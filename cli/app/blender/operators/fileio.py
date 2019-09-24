import sys
from os.path import join
from pathlib import Path
import importlib
import math
import random

import pandas as pd

import bpy

sys.path.append('/work/vframe_synthetic/vframe_synthetic')
from app.utils import log_utils
from app.settings import app_cfg
# reload application python modules
importlib.reload(log_utils)

# shortcuts
log = log_utils.Logger.getLogger()


# ---------------------------------------------------------------------------
# Mange File I/O settings
# ---------------------------------------------------------------------------

class FileIOManager:
  '''Manages File I/O settings'''

  fp_dir_out = None
  fp_name = None

  def __init__(self, cfg):
    cfg_output = cfg.get('render').get('output')
    self.fp_dir_out = cfg_output.get('filepath')
    self.fname_prefix = cfg_output.get('filename_prefix')
    self.ext = cfg_output.get('file_format').lower()
    self.fp_out_annos = join(self.fp_dir_out, app_cfg.FN_METADATA)
    
    if not Path(self.fp_dir_out).exists():
      Path(self.fp_dir_out).mkdir(exist_ok=True, parents=True)


  def build_fp_real(self, fname):
    fp = join(app_cfg.DN_REAL, f'{self.fname_prefix}{fname}.{self.ext}')
    return join(self.fp_dir_out, fp)

  def build_fp_mask(self, fname):
    fp = join(app_cfg.DN_MASK, f'{self.fname_prefix}{fname}.{self.ext}')
    return join(self.fp_dir_out, fp)

  def annos_to_csv(self, anno_data):
    df = pd.DataFrame.from_dict(anno_data)
    df.to_csv(self.fp_out_annos, index=False)

  def cleanup(self):
    ''''''
    pass
