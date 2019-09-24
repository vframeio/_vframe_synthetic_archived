"""
Color fill shader node utilities

"""
#import logging

import bpy

#log = logging.getLogger('VFRAME')


class ColorFillObject:

  _material = None

  NODE_TYPE_RGB = 'ShaderNodeRGB'
  NODE_TYPE_BG = 'ShaderNodeBackground'
  NODE_TYPE_OUT_WORLD = 'ShaderNodeOutputWorld'

  NODE_TYPE_IMAGE_TEXTURE = 'ShaderNodeTexImage'
  NODE_TYPE_TRANSPARENT_BSDF = 'ShaderNodeBsdfTransparent'
  
  NODE_TYPE_LIGHT_PATH = 'ShaderNodeLightPath'
  NODE_TYPE_EMISSION = 'ShaderNodeEmission'
  NODE_TYPE_MIX = 'ShaderNodeMixShader'
  NODE_TYPE_MAT_OUT = 'ShaderNodeOutputMaterial'
  NODE_TYPE_IS_CAM_RAY = 'Is Camera Ray'
  NODE_TYPE_FAC = 'Fac'
  NODE_TYPE_MAT_OUT = 'Material Output'

  LABEL_COLOR = 'Color'
  LABEL_SHADER = 'Shader'
  LABEL_EMISSION = 'Emission'
  LABEL_SURFACE = 'Surface'
  LABEL_BG = 'Background'
  LABEL_RGB = 'RGB'
  LABEL_BSDF = 'BSDF'
  
  nodes = None
  links = None

  def __init__(self, material):
    self._material = material
    self._material.use_nodes = True
    self.nodes = self._material.node_tree.nodes
    self.links = self._material.node_tree.links

  @property
  def material(self):
    return self._material

  def remove_material(self):
    bpy.data.material.remove(self._material)



class ColorFillWorld(ColorFillObject):

  def __init__(self, name, color):
    """Creates a Color Shader material object
    :param name: (str) name of material
    :param color: (rgb) float rgb (1.0, 0, 0, 0)
    """
    existing_materials = bpy.data.worlds.keys()
    bpy.ops.world.new()
    new_materials = bpy.data.worlds.keys()
    new_material_name = list(set(new_materials) - set(existing_materials))[0]
    new_material = bpy.data.worlds.get(new_material_name)
    new_material.name = name

    super().__init__(new_material)
    
    # add RGB node
    node_rgb = self.nodes.new(type=self.NODE_TYPE_RGB)
    node_rgb.outputs['Color'].default_value = color
    node_rgb_link_id = node_rgb.outputs[self.LABEL_COLOR]

    # add bg
    node_bg = self.nodes.get(self.LABEL_BG)
    node_bg_link_id = node_bg.inputs[self.LABEL_COLOR]

    # link RGB to BG
    self.links.new(node_rgb_link_id, node_bg_link_id)



class ColorFillMaterial(ColorFillObject):

  def __init__(self, name, color, alpha_image=None):
    """Creates a Color Shader material object
    :param name: (str) name of material
    :param color: (rgb) float rgb (1.0, 0, 0, 1)
    """
    
    new_material = bpy.data.materials.new(name=name)
    
    super().__init__(new_material)

    # add LightPath node
    if alpha_image:
      node_im_light = self.nodes.new(self.NODE_TYPE_IMAGE_TEXTURE)
      node_im_light.image = bpy.data.images.get(alpha_image)
      # add transparent BSDF
      node_trans_bsdf = self.nodes.new(self.NODE_TYPE_TRANSPARENT_BSDF)
    else:
      node_im_light = self.nodes.new(self.NODE_TYPE_LIGHT_PATH)

    # add RGB node
    node_rgb = self.nodes.new(self.NODE_TYPE_RGB)
    node_rgb.outputs[self.LABEL_COLOR].default_value = color

    # add Emission node
    node_emission = self.nodes.new(self.NODE_TYPE_EMISSION)

    # add MixShader node
    node_mix = self.nodes.new(self.NODE_TYPE_MIX)

    # link LightPath to MixShader
    if alpha_image:
      self.links.new(node_im_light.outputs[self.LABEL_COLOR], node_mix.inputs[self.NODE_TYPE_FAC])
      self.links.new(node_trans_bsdf.outputs[self.LABEL_BSDF], node_mix.inputs[1])
    else:
      self.links.new(node_im_light.outputs[self.NODE_TYPE_IS_CAM_RAY], node_mix.inputs[self.NODE_TYPE_FAC])

    # link RGB to Emission
    self.links.new(node_rgb.outputs[self.LABEL_COLOR], node_emission.inputs[self.LABEL_COLOR])

    # link Emission to MixShader
    #self.links.new(node_emission.outputs[self.LABEL_EMISSION], node_mix.inputs[1])  # Shader 1 and
    self.links.new(node_emission.outputs[self.LABEL_EMISSION], node_mix.inputs[2])  # Shader 2

    # create link for mix shader
    self.node_colorfill = node_mix
    self.node_colorfill_link_id = self.node_colorfill.outputs[self.LABEL_SHADER]

    # check if material output node exits and link it
    if self.NODE_TYPE_MAT_OUT in self.nodes.keys():
      self.node_out = self.nodes.get(self.NODE_TYPE_MAT_OUT)
      self.node_out_link_id = self.node_out.inputs.get(self.LABEL_SURFACE)
      self.links.new(self.node_colorfill_link_id, self.node_out_link_id)

    if alpha_image:
      mat = bpy.data.materials.get(name)
      mat.blend_method = 'CLIP'
      mat.shadow_method = 'CLIP'

  