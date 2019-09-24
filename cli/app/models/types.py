"""
Enumerated application data types
"""
import os
from os.path import join
from pathlib import Path
from enum import Enum

from app.utils import file_utils, click_utils

SELF_CWD = os.path.dirname(os.path.realpath(__file__))


# ---------------------------------------------------------------------
# Logger, monitoring
# --------------------------------------------------------------------
class GeneratorSystem(Enum):
  """Generator script options"""
  STATIC, EMITTER = range(2)

GeneratorSystemVar = click_utils.ParamVar(GeneratorSystem)

# ---------------------------------------------------------------------
# Logger, monitoring
# --------------------------------------------------------------------
class LogLevel(Enum):
  """Loger vebosity"""
  DEBUG, INFO, WARN, ERROR, CRITICAL = range(5)

LogLevelVar = click_utils.ParamVar(LogLevel)

# ---------------------------------------------------------------------
# Helpers
# --------------------------------------------------------------------

def find_type(name, enum_type):
  for enum_opt in enum_type:
    if name == enum_opt.name.lower():
      return enum_opt
  return None