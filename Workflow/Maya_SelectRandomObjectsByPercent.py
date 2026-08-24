import maya.cmds as cmds
import random

percentage_input = 60

def CalculatePercentage(percentage, amount):
    return (amount / 100) * percentage
    
selected = cmds.ls(sl=True)
length_selected = len(selected)
print(selected)
print(length_selected)

amount_to_select = int(CalculatePercentage(percentage_input, length_selected))
print(amount_to_select)
selected_randomised = random.sample(selected, amount_to_select)

print(selected_randomised)
cmds.select(selected_randomised)