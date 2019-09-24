"""
Command for testing the Blender Python CLI subprocess script
This is a template to be useful for buiding other CLI generators
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

from pathlib import Path

import bpy

from app.utils import log_utils
from app.utils import log_utils, file_utils, sys_utils
from app.utils.file_utils import zpad

# logger
log_utils.Logger.create()  # initialize
log = log_utils.Logger.getLogger()



# -------------------------------------------------------------------
# Main app
# -------------------------------------------------------------------

# create logger
log_utils.Logger.create(verbosity=args.opt_verbosity)
log = log_utils.Logger.getLogger()

log.info(f'Running: {Path(__file__).name}')
log.info('Parse demo successful')

