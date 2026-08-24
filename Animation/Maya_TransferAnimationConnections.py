# TransferAnimationConnections v1.0.1
# Currently pretty basic and only works on transform attributes
# Select the animated object first and then the target objects afterwards to be connected.
# TO DO:
    # Need to add the functionality for finding and transferring other animate nodes.

import maya.cmds as cmds
import maya.OpenMaya as om


# select animated object first, then select target
selection = cmds.ls(sl=True)
source_object = selection[0]
target_objects = selection[1:]
print(target_objects)


def connectAttributes(source, target):
    cmds.connectAttr(f"{source}_translateX.output", f"{target}.translateX", force=True)
    cmds.connectAttr(f"{source}_translateY.output", f"{target}.translateY", force=True)
    cmds.connectAttr(f"{source}_translateZ.output", f"{target}.translateZ", force=True)
    
    cmds.connectAttr(f"{source}_rotateX.output", f"{target}.rotate.rotateX", force=True)
    cmds.connectAttr(f"{source}_rotateY.output", f"{target}.rotate.rotateY", force=True)
    cmds.connectAttr(f"{source}_rotateZ.output", f"{target}.rotate.rotateZ", force=True)

    cmds.connectAttr(f"{source}_scaleX.output", f"{target}.scale.scaleX", force=True)
    cmds.connectAttr(f"{source}_scaleY.output", f"{target}.scale.scaleY", force=True)
    cmds.connectAttr(f"{source}_scaleZ.output", f"{target}.scale.scaleZ", force=True)
    
    return
    
    
for object in target_objects:
    connectAttributes(source_object, object)
    om.MGlobal.displayInfo(f"Transferred {source_object} animated inputs to {object} joint inputs")
