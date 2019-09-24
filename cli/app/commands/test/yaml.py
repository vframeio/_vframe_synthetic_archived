"""
Generates training data from Blender generator
"""
from os.path import join
from pathlib import Path
from pprint import pprint

import click

from app.models import types
from app.settings import app_cfg
from app.utils import click_utils


FP_CLI_ROOT = join(app_cfg.DIR_PROJECT_ROOT, 'cli')
FP_PY = str(Path(app_cfg.DIR_PROJECT_ROOT) / 'cli/app/blender/render_particle_system.py')


@click.command()
@click.option('--config', 'opt_fp_cfg', required=True,
  help='Path to input Python script', show_default=True)
@click.option('-v', '--verbose', 'opt_verbose', is_flag=True,
  help='Print YAML even if no errors', show_default=True)
@click.pass_context
def cli(ctx, opt_fp_cfg, opt_verbose):
  """Test YAML file"""

  log = app_cfg.LOG
  log.info(f'Testing: {opt_fp_cfg}')

  from app.utils.file_utils import load_yml

  try:
    yaml_data = load_yml(opt_fp_cfg)
    log.debug('YAML is OK')
    if opt_verbose:
      pprint(yaml_data)  
  except Exception as e:
    log.error('YAML errors')
    pprint(yaml_data)