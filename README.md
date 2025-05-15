# Blender-OpenGEX
"OpenGEX Exporter" for Blender 4.4 x, based on the original exporter code by Jonathan Hale, which in turn was based 
on original code by Eric Lengyel (can be found at http://opengex.org/).

# How to install

Install instructions for all operating systems:
 1. Download the latest release as a .zip from ["releases"](https://github.com/Squareys/Blender-OpenGEX/releases).
 2. Open Blender and under `File > User Preferences... > Addons` select `Install from File...` and locate the zip file.
 Finally click `Install from File..` to close the file browser.
 3. Search for "OpenGEX" and enable the addon.

# Differences to the Official Exporter

* Support for exporting linked objects and linked groups
* Faster geometry export, but: \*
  * No support for morphing
  * No support for vertex skin weights
* Support for exporting object game physics as Extensions [=> documentation](https://github.com/Squareys/Blender-OpenGEX/wiki/PhysicsMaterial-Extension)
* Support for exporting custom properties as Extensions [=> documentation](https://github.com/Squareys/Blender-OpenGEX/wiki/Property-Extension)
* Support for exporting the worlds ambient color and material ambient factor [=> documentation](https://github.com/Squareys/Blender-OpenGEX/wiki/Ambient-Colors)
* Support for exporting speakers and sound source properties as Extensions [=> documentation](https://github.com/Squareys/Blender-OpenGEX/wiki/AudioSource-Extension)
* Option for rounding floating point number to n decimal places
* Option to export only the first material slot of each object
* Option to specify prefix for exported texture paths
* Image texture export
* Export OpenGEX in an compressed text format (without whitespaces)

\* Some of the broken features may be implemented in the future if I start needing them.

# Development Notes

The most ergonomic way to develop and debug the extension is to make a symlink (or _junction_ on windows) pointing to `src/io_scene_ogex`
```
%APPDATA%\Roaming\Blender Foundation\Blender\4.4\extensions\user_default\opengex_exporter --> src/io_scene_ogex
```

In blender's python console, install `debugpy` (you have to do it only once):

```python
import sys
import subprocess
subprocess.check_call([sys.executable, "-m", "pip", "install", "debugpy"])
```

Then you listen to connections by running:

```python
import debugpy
debugpy.listen(("localhost", 5678))
```

VS Codes's python debugger can connect to it (when you set "pathMappings" in `launch.json`)

```
"pathMappings": [
            {
                "localRoot": "${workspaceFolder}\\src\\io_scene_ogex",
                "remoteRoot": "C:\\Users\\YOUR_USERNAME\\AppData\\Roaming\\Blender Foundation\\Blender\\4.4\\extensions\\user_default\\io_scene_ogex"
            }
        ]
```

# Version Semantics

OpenGEX Exporter Addon versions are built up as:

`<OpenGEX specification version>.<1 digit for OpenGEX Exporter Addon version>`

# License

```
Copyright © 2015, 2016 Jonathan Hale
Copyright © 2015 Terathon Software LLC
Copyright © 2015 Nicolas Wehrle
Copyright © 2025 Roland Sadowski

This software is licensed under the Creative Commons
Attribution-ShareAlike 3.0 Unported License:

http://creativecommons.org/licenses/by-sa/3.0/deed.en_US

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED,
INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR
PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE
FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR
OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER
DEALINGS IN THE SOFTWARE.
```
