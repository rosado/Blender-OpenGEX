import sys
import unittest
import os
import pathlib as p

__author__ = "Jonathan Hale"

# We need to add the blender's extension directory to sys.path (not sure why it's not
# in there in the first place) to be able to import our extension.

user_blender_home = p.Path(os.getenv("APPDATA")) / "Blender Foundation" / "Blender"
blender_version_dirs = list(user_blender_home.iterdir())
if len(blender_version_dirs) == 0:
    print(f"No blender versions available in '{user_blender_home}'")
    print("Try launching blener at least once, the directory should be created automatically.")
    exit(2)

latest = blender_version_dirs[-1]
extensions_dir = latest / "extensions" / "user_default"
sys.path.append(str(extensions_dir))
print(f"Using '{extensions_dir}'")

# find all unittests in tests/
suite = unittest.TestLoader().discover('.', pattern='*Test.py', top_level_dir='.')

# run the found tests and exit with failure when not successful
if not unittest.TextTestRunner(verbosity=2).run(suite).wasSuccessful():
    exit(1)
