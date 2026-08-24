# Maya_RenameDuplicates v0.0.2
# With nothing selected this will run through all objects in the scene and search for duplicate objects. 
# If there are objects selected it will just look at the selected group. 
# It will brute force rename those objects - taking the current name and adding a suffix.

import maya.cmds as cmds
import re
import maya.OpenMaya as om

def get_duplicate_objects(verbose=True):
    """Finds objects in scene with the same names.
    Args:
        verbose (bool): If True, all duplicates full DAG path is printed to the console.
    Returns:
        list: List with the full path name for all the duplicate objects found.
    """
    
    # making it so that if something is selected, it will only look into those objects
    selected = cmds.ls(sl=True)
    if selected:
        selected_relatives = cmds.listRelatives(selected, children=True, fullPath=True)
        selected += selected_relatives
    full_scene = cmds.ls()
    all_objects = []
    
    if selected:
        all_objects = selected
    else:
        all_objects = full_scene
    
    
    objects_tokens = [i.split("|")[-1] for i in all_objects]
    duplicates = [all_objects[i] for i, obj in enumerate(objects_tokens) if objects_tokens.count(obj) > 1]
    duplicates.sort(key=lambda obj: obj.count('|'), reverse=True)
    
    renamed_objects = []

    if verbose and duplicates:
        print(f"- Found {len(duplicates)} duplicates.")
        
        for name in duplicates:
            shortName = name.split("|")[-1]
            children = cmds.listRelatives(name, children=True, fullPath=True) or []
            newName = f"{shortName}_#"
            
            lock_status = cmds.lockNode(name, q=True)
            for response in lock_status:
                if response != False:
                    try:
                        cmds.lockNode(name, lock=False)
                        print(f"Unlocked node: {name}.")
                    except:
                        print(f"Could not unlock node: {name}.")
            
            try:
                renamed_object = cmds.rename(name, newName)
                renamed_objects.append(renamed_object)
            except:
                print(f"Could not rename locked node: {name}")
                continue
        
        print(f""" Renamed Objects:
        {renamed_objects})""")
        om.MGlobal.displayInfo(f"- Found {len(duplicates)} duplicates.")
        # now run through all the renamed objects and select the ones that can be selected
        # shape nodes can't be selected this way for some reason
        selectable_objects = []
        
        for object in renamed_objects:
            try:
                cmds.select(object, add=True)
            except:
                continue
    else:
        om.MGlobal.displayInfo("No duplicates found.")
    
    
if __name__ == '__main__':
    get_duplicate_objects()