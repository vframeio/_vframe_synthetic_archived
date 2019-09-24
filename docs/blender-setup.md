# Blender Installation and Setup

- Download Blender <https://www.blender.org/download/>

## Linux

- this will download a file with a name similar to `blender-2.80-linux-glibc217-x86_64.tar.bz2`
- double-click to unzip via GUI, or `bunzip2 /path/to/blender-2.80-linux-glibc217-x86_64.tar.bz2`
- set path as variable `export BLENDER=/path/to/blender-2.80-linux-glibc217-x86_64`
- create symlink `sudo ln -s ${BLENDER}/blender /usr/bin/blender`
- from the command line, type `blender` to open

## Mac OS

- install via .dmg

## Windows

- TBD

## Install Python Packages for Blender

Blender 2.8 uses a bundled Python/PIP package located in the installed blender local folder.

Before installing new Python packages, remove the old version of Numpy distributed by Blender.

- `cd ${BLENDER_PATH}`
- `mkdir ${BLENDER_PATH}/python_libs_deprecated`
- `mv ${BLENDER_PATH}/2.8/python/lib/python3.7/site-packages/numpy/ ${BLENDER_PATH}/python_libs_deprecated/`

Then, install PIP for Blender

- navigate to Blender's python directory `cd ${BLENDER}/2.8.python/bin`
- install PIP by running `./python3.7m ../lib/python3.7/ensurepip`
- install requirements.txt `./pip3.7 install -r vframe_synthetic/cli/requirements_blender.txt`
