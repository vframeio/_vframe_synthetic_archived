# VFRAME: Synthetic Data Notes

## Install Blender

- Download Blender, bunzip .bz2 file
- `tar -xf [blendrfile]`
- create symlink `sudo ln -s /home/username/blender-2.80-1b839e85e142-linux-glibc224-x86_64/blender /usr/bin/blender`

## Install PIP

Blender 2.8 uses a bundled Python/PIP package located in the installed blender local folder

- install pip, `cd 2.80/python/bin`, `./python3.7m ../lib/python3.7/ensurepip`
- install requirements `./pip3.7 install -r path/to/requirements.txt`

Fix numpy version conflict by removing old numpy

- `cd ${BLENDER_PATH}`
- `mkdir ${BLENDER_PATH}/python_libs_deprecated`
- `mv ${BLENDER_PATH}/2.8/python/lib/python3.7/site-packages/numpy/ ${BLENDER_PATH}/python_libs_deprecated/`
- then `./pip3.7 install numpy`


## Jazz Decoys

- https://www.blendermarket.com/products/shape-generator
- https://www.blendswap.com/blends/view/93431
- https://www.blendswap.com/blends/view/68647
- https://internethealthreport.org/2019/wp-content/uploads/sites/7/2019/03/IHR2019_spotlight_da-2-3-1-1620x1080.jpg
- http://www.fubiz.net/wp-content/uploads/2019/04/PT7.png
- https://www.turbosquid.com/3d-models/3d-model-complex-shape/882607

## TODO

- rigid body detection
- alpha channel in colorfill objects
- adding a few more scenic objects for each category (trash, rocks, trees, bushes)
- adding multiple version of training objects (dirty sign, bent sign, mangled munition, etc)
- adding more primitive (jazzy) shapes (squiggly lines, rods, random shapes)
- adding textures for the ground (these can be swapped too)
- 
