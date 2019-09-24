"""
Runs Blender with Python script for tests
"""
from os.path import join
from pathlib import Path
import click

from app.models import types
from app.settings import app_cfg
from app.utils import click_utils


@click.command()
@click.option('--blender', 'opt_fp_blender', default=app_cfg.FP_BLENDER_BIN,
  help='Path to Blender binary', show_default=True,)
@click.option('--blend', 'opt_fp_blend', required=True,
  help='Path to Blender .blend file', show_default=True,)
@click.option('--python', 'opt_fp_python', required=True,
  help='Path to input Python script')
@click.option('--config', 'opt_fp_cfg',
  help='Path to input config YAML script', show_default=True,)
@click.option('--resume', 'opt_checkpoint', default='0', type=str,
  help='Resume particle iteration', show_default=True)
@click.option('--dry-run', 'opt_dry_run', is_flag=True, default=False,
  show_default=True)
@click.option('--root', 'opt_dir_cli_root', default=app_cfg.DIR_CLI,
  help='Path to root directory of vframe_synthetic code')
@click.pass_context
def cli(ctx, opt_fp_blender, opt_fp_blend, opt_fp_cfg, opt_fp_python,
  opt_checkpoint, opt_dry_run, opt_dir_cli_root):
  """Runs Blender demos and test"""
  
  import subprocess

  log = app_cfg.LOG
  log.info('Running Blender test')

  # Blender variables. The trailing '--' indicates end of arguments
  args = [opt_fp_blender, opt_fp_blend, '--background', '--python', opt_fp_python, '--']

  # Python script variables
  args.append(f'--cfg {opt_fp_cfg}')
  args.append(f'--root {opt_dir_cli_root}')
  args.append(f'--checkpoint {opt_checkpoint}')

  if opt_dry_run:
    log.debug('This was a dry run. Script would have called:')
    log.debug(' '.join([str(x) for x in args]))
  else:
    # Dispatch subprocess to Blender
    subprocess.call(args, stdin=None, stdout=None, stderr=None, shell=False)
