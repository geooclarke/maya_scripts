# Maya_SelectHeirarchy v1.0.1
# this will select the hierarchy of the chosen groups and will deselect the original grouped selection
# so that the children will be the only objects selected

import maya.cmds as cmds

selected = cmds.ls(sl=True)

cmds.SelectHierarchy()

if selected:
    for object in selected:
        cmds.select(selected, d=True)
else:
   cmds.warning("Select an group first!")
