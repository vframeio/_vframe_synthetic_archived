"""
Generates training data from Blender generator
"""
import click

@click.command()
@click.option('-i', '--input', 'opt_fp_in', required=True,
  help='Path to input file')
@click.option('-o', '--output', 'opt_fp_out', required=True,
  help='Path to input file')
@click.option('--dry-run', 'opt_dry_run', is_flag=True, default=False,
  show_default=True, help='Run code as dry run test')
@click.pass_context
def cli(ctx, opt_fp_in, opt_fp_out, opt_dry_run):
  """Example CLI script"""
  
  from pathlib import Path

  from app.settings import app_cfg

  log = app_cfg.LOG
  log.info('This is an example script')

  log.debug(f'input: {opt_fp_in}, output: {opt_fp_out}, dry-run: {opt_dry_run}')