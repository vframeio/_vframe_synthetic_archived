import os
from os.path import join
from pathlib import Path
import logging
import codecs
codecs.register(lambda name: codecs.lookup('utf8') if name == 'utf8mb4' else None)

from dotenv import load_dotenv


# -----------------------------------------------------------------------------
# Click settings
# -----------------------------------------------------------------------------

DIR_COMMANDS_BLENDER = 'app/commands/blender'
DIR_COMMANDS_CONVERT = 'app/commands/convert'
DIR_COMMANDS_CUSTOM = 'app/commands/custom'
DIR_COMMANDS_TEST = 'app/commands/test'


# -----------------------------------------------------------------------------
# Environment vars and filepaths
# -----------------------------------------------------------------------------

load_dotenv() # dotenv_path=DIR_DOTENV)

# base path
DIR_SELF = os.path.dirname(os.path.realpath(__file__))
DIR_ROOT = Path(DIR_SELF).parent.parent.parent

# data_stores
DATA_STORE = '/data_store_hdd/'  # default
DATA_STORE_NAS = '/data_store_nas/'
DATA_STORE_HDD = '/data_store_hdd/'
DATA_STORE_SSD = '/data_store_ssd/'
DIR_APPS = join(DATA_STORE,'apps')
DIR_APP = join(DIR_APPS,'vframe')
DIR_MODELS = join(DIR_APP,'models')
DIR_CLI = join(DIR_ROOT, 'cli')
DIR_GENERATORS = join(DIR_CLI, 'app/blender/generators')

# standardize Blender output files
FN_METADATA = 'metadata.csv'  # filenamne
DN_REAL = 'real'  # directory name
DN_MASK = 'mask'  # directory name
DN_COMP = 'comp'  # directory name


# -----------------------------------------------------------------------------
# Project root
# -----------------------------------------------------------------------------

SELF_CWD = os.path.dirname(os.path.realpath(__file__))  # Script CWD
DIR_PROJECT_ROOT = str(Path(SELF_CWD).parent.parent.parent)


# -----------------------------------------------------------------------------
# Drawing, GUI settings
# -----------------------------------------------------------------------------

#DIR_ASSETS = join(DIR_APP, 'assets')
#FP_FONT = join(DIR_ASSETS, 'font')


# -----------------------------------------------------------------------------
# Blender binary
# -----------------------------------------------------------------------------
LOG = logging.getLogger('VFRAME')

# -----------------------------------------------------------------------------
# Blender binary
# -----------------------------------------------------------------------------

FP_BLENDER_BIN = str(Path.home() / 'code/blender-2.80-linux-glibc217-x86_64/blender')