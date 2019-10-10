# pcbnew loads this folder as a package using import
# thus __init__.py (this file) is executed
# We import the plugin class here and register it to pcbnew

from . import uwArcPrimitive_wizard
from . import uwMitered_wizard
from . import uwTaper_wizard




