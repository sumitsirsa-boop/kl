"""Selects which video project (timeline + scenes modules) the pipeline builds.

Pass `--project NAME` to build_audio.py / render.py to use NAME_timeline.py and
NAME_scenes.py; without it the original Dear 1000 video (timeline.py, scenes.py) is built.
"""
import importlib
import sys


def _name():
    argv = sys.argv
    if "--project" in argv:
        i = argv.index("--project")
        if i + 1 < len(argv):
            return argv[i + 1]
    return ""


PROJECT = _name()
_prefix = PROJECT + "_" if PROJECT else ""


def load(kind):
    return importlib.import_module(_prefix + kind)
