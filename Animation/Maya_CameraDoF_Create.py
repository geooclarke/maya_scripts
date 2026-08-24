# Maya_CameraDoF_Create v0.0.3
# simple code that will create a DoF expression that connects to a distanceDimension node with locators.
# select the camera first and then run the code.

import maya.cmds as cmds

def createLocator(cameraName):
    name = f"{cameraName}_DoF_loc_#"
    locator = cmds.spaceLocator(n=name)
    return locator[0]
    
def zeroAttrs(obj):
    cmds.move(0, 0, 0, obj, localSpace=True)
    cmds.rotate(0, 0, 0, obj)
    cmds.scale(1, 1, 1, obj)
    
def lockAttrs(obj):
    axis = ["X", "Y", "Z"]
    
    for ax in axis:
        cmds.setAttr(f"{loc_1}.translate{ax}", lock=True)
        cmds.setAttr(f"{loc_1}.rotate{ax}", lock=True)
        
selectedCam = cmds.ls(sl=True, dag=True)
camShape = selectedCam[1]
camName = selectedCam[0]
print(selectedCam)
print(camShape)
# creation of the locators and distance object
loc_1 = createLocator(camName)
loc_2 = createLocator(camName)

print(loc_1)
cmds.move(0, 0, 1, loc_1, localSpace=True) # the distanceDimension won't work if the points are both on top of each other
startPoint = cmds.getAttr(f"{loc_1}.translate")
endPoint = cmds.getAttr(f"{loc_2}.translate")

create_dist = cmds.distanceDimension(sp=startPoint[0], ep=endPoint[0])
distDimParent = cmds.listRelatives(create_dist, p=True)
cmds.select(clear=True)
distDimParent = cmds.rename(distDimParent, f"{camName}_DoF")

# creating the expression connected to the original camera
cmds.expression(s=f"{camShape}.focusDistance = {distDimParent}.distance")

# parenting the first locator to the camera
cmds.parent(loc_1, selectedCam[0])
zeroAttrs(loc_1)
lockAttrs(loc_1)
