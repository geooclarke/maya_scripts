# select all relevant objects you want, run the script and it will have default values applied on subdivision and displacement.
# works with full path so duplicated items with no name changes won't throw an error 

import maya.cmds as cmds

selected = cmds.ls(sl=True)

shapes = cmds.listRelatives(shapes=True, noIntermediate=True, fullPath=True)

print(shapes)

def makeVrayAttributes():
    for i in selected:
        shapes = cmds.listRelatives(shapes=True, noIntermediate=True, fullPath=True)
        if shapes:
            for s in shapes:
                melCmd = "vray addAttributesFromGroup "+s+" vray_subdivision 1"
                mel.eval(melCmd)
                melCmd = "vray addAttributesFromGroup "+s+" vray_subquality 1"
                mel.eval(melCmd)
                
makeVrayAttributes()