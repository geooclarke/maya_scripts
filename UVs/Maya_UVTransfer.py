# Maya_UVTransfer v0.0.1 
# Very quickly transfer UV shells from one mesh to multiple ones without affecting transform history. 
# Select the source object first and then follow with at least one item after this.

import maya.cmds as cmds
import maya.OpenMaya as om

selection = cmds.ls(sl=True)


def uvTransfer(list):
    if not selection:
        om.MGlobal.displayError("Please select the source object and then at least one target object after this.")
    else: 
        source = list[0]
        target = list[1:]
        for object in target:
            cmds.polyTransfer(object, uv=True, constructionHistory=False, alternateObject=source)
            cmds.polyTransfer(object, uv=True, ch=False, alternateObject=source) # run it twice because UV sets don't come with it on the first time
    
if __name__ == "__main__":
    uvTransfer(selection)
