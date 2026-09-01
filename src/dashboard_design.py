"""Compatibility entry point for the project's premium visual system.

Running this file regenerates the hero art, analytical figures, insight storyboard,
and executive dashboard using the unified visual-refresh script.
"""
from pathlib import Path
import runpy

SCRIPT = Path(__file__).with_name('visual_refresh.py')
runpy.run_path(str(SCRIPT), run_name='__main__')
