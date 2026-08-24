# Maya_SendToTopOfOutliner v0.0.1
# Really basic script that will take the selected object and send it directly to the top of the outliner.
# Mainly use it for just getting objects out of my way.

import maya.cmds as cmds

selected = cmds.ls(sl=True)

cmds.reorder(selected, f=True)