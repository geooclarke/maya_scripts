# Maya_UV_TileBreakup v0.0.1
# this will create a maxon noise node for controlling the tile offset on a file texture node. Really useful for breaking up a repeating pattern
# select the place 2d nodes that you want to plug the maxon noise node into 
# then run script

import maya.cmds as cmds

selected = cmds.ls(sl=True)

maxon_noise = cmds.shadingNode("RedshiftMaxonNoise", asTexture=True)
remap_node = cmds.shadingNode("remapValue", asUtility=True)
cmds.connectAttr(f"{maxon_noise}.outColorR", f"{remap_node}.inputValue")
cmds.setAttr(f"{maxon_noise}.noise_type", 24)
cmds.setAttr(F"{remap_node}.outputMax", 10)

for node in selected:
    if cmds.objectType(node, isType="place2dTexture"):
        cmds.connectAttr(f"{remap_node}.outValue", f"{node}.offset.offsetU")
        cmds.connectAttr(f"{remap_node}.outValue", f"{node}.offset.offsetV")
