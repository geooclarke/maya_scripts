# Maya_ToPFTrack_LocatorExporter v0.0.4

# this script was created to send out a text file that meets the standard import format for PFTrack. 
# the text file will be sent out to the location of the saved maya file. i.e. the scenes folder etc
# if the file has not been saved then it will prompt a save location
# start by selecting a series of locators with locators that are in position of what you're trying to track
# then run the script, this will create a text file in the location of the maya file with all the transform data

import maya.cmds as cmds
import os

# user defined attributes

uncertainty_value_default = 3

# TO TEST OUT
    # what heppens in PFTrack if the locator naming conventions push it outside of the first tab group
    # does PF track still take them not in alphabetical order or do they need sorting first

# getting the scene name in order to isolate both the scene name and the file path

filepath = cmds.file(q=True, sn=True)
filename = os.path.basename(filepath)
raw_name, extension = os.path.splitext(filename)
filepath = filepath.replace(filename, "")

# getting all the transforms from selected locators

selected_markers = cmds.ls(sl=True)
print(selected_markers)
locator_dimensions_list = []

# writing the information to the text file

text_file_suffix = "trackingMarkers.txt"
default_heading = "# Name		SurveyX			SurveyY			SurveyZ			Uncertainty"

# define where it will be saved. If the scene has been saved, place in same location. If not, ask the user to select a folder.
if filepath:
    file_name_path = f"{filepath}{raw_name}_{text_file_suffix}"
else:
    title = "Select a folder"
    caption = "Open"
    selected_folder = cmds.fileDialog2(fileMode=3, caption=title, okCaption=caption)
    filepath = selected_folder[0]
    file_name_path = f"{filepath}_{text_file_suffix}"

uncertainty_value = format(uncertainty_value_default, ".6f")

file_create = open(file_name_path, "w")

file_create.write(f"{default_heading} \n")

for locator in selected_markers:
    locator_transformX = format(cmds.getAttr(f"{locator}.translateX"), ".15f")
    locator_transformY = format(cmds.getAttr(f"{locator}.translateY"), ".15f")
    locator_transformZ = format(cmds.getAttr(f"{locator}.translateZ"), ".15f")
    file_create.write(f"\"{locator}\" \t")
    file_create.write(f"{locator_transformX} \t")
    file_create.write(f"{locator_transformY} \t")
    file_create.write(f"{locator_transformZ} \t")
    file_create.write(uncertainty_value)
    
    file_create.write("\n")
    
file_create.close()

file_written_message = f"The .txt file has been successfully written here: \n {file_name_path}"
cmds.confirmDialog(title="Text Output File", message=file_written_message, button="OK", icon="information")
