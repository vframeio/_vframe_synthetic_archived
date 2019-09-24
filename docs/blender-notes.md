# Blender

Opearator notes for using Blender.

## Tips

- views: click _Grid Icon_ next to camera to enable/disable world view and ortho 

## Issues

Accessing Pixels Directly. This might be possible. Currently not possible to correctly scale np.float64 data.

```
import bpy
import numpy as np
 
# switch on nodes
bpy.context.scene.use_nodes = True
tree = bpy.context.scene.node_tree
links = tree.links
rl = tree.nodes.new('CompositorNodeRLayers')      
rl.location = 185,285
v = tree.nodes.new('CompositorNodeViewer')   
v.location = 750,210
v.use_alpha = False
links.new(rl.outputs[0], v.inputs[0])  # link Image output to Viewer input
bpy.ops.render.render()
pixels = bpy.data.images['Viewer Node'].pixels
pixels = np.array(pixels[:])
im = pixels.reshape(810,1440,4)[:,:,:3]
info = np.finfo(im.dtype)
im = im.astype(np.float64)
im = (im * 255).astype(np.uint8)
im = cv.cvtColor(im, cv.COLOR_RGB2BGR)
cv.imwrite('/home/adam/Downloads/test.png', im)


# this didn't seem to scale correctly
im = img_as_ubyte(im)
cv.imwrite('/home/adam/Downloads/test.png', im)
#im = im.astype(np.float64) / info.max

im = cv.cvtColor(im, cv.COLOR_RGB2BGR)
cv.imwrite('/home/adam/Downloads/test.png', im)

```


## Unsolvable Issues

- Headless rendering is not yet supported <https://devtalk.blender.org/t/blender-2-8-unable-to-open-a-display-by-the-rendering-on-the-background-eevee/1436/17>
