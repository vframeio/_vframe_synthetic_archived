"""
File utilities for reading, writing, and formatting data
"""
import yaml

def load_yml(fp_yml, loader=yaml.Loader):
  '''Loads YAML file '''
  with open(fp_yml, 'r') as fp:
    cfg = yaml.load(fp, Loader=loader)
  return cfg

def zpad(x, zeros=4):
  return str(x).zfill(zeros)
