# force reload imports for Blender Python module

__all__ = ['colorfill']

from . import colorfill

import importlib
importlib.reload(colorfill)