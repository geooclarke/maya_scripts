import maya.cmds as cmds
import maya.OpenMaya as om
import random

def randomObjects(objects, amount):
    newList = objects
    random.shuffle(newList)
    
    for i in range(amount):
        yield objects.pop()

selected = cmds.ls(sl=True)
newSelection = []
om.MGlobal.displayWarning("How many objects would you like to select?")
amount = int(input("Name how many objects you'd like to select"))

for object in randomObjects(selected, amount):
    newSelection.append(object)
    
cmds.select(newSelection)    
