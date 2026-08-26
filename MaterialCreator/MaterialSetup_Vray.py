from maya import cmds

# ============================================================
# LOAD VRAY
# ============================================================

def ensure_vray():
    if cmds.pluginInfo("vrayformaya", q=True, loaded=True):
        print("Vray Loaded")
    else:
        raise RuntimeError("Could not load V-Ray")

# ============================================================
# CREATE FILE NODE
# ============================================================

def create_texture_node(name, filepath, raw=True):
    file_node = cmds.shadingNode("file", asTexture=True, name=f"{name}_file")
    place = cmds.shadingNode("place2dTexture", asUtility=True, name=f"{name}_place2d")
    colour_correction = cmds.shadingNode("VRayColorCorrection", asTexture=True, name=f"{name}_CC")

    cmds.connectAttr(f"{place}.outUV", f"{file_node}.uvCoord", f=True)
    cmds.connectAttr(f"{place}.outUvFilterSize", f"{file_node}.uvFilterSize", f=True)

    cmds.setAttr(f"{file_node}.fileTextureName", filepath, type="string")
    if raw:
        cmds.setAttr(f"{file_node}.colorSpace", "Utility - Raw", type="string")
    else:
        cmds.setAttr(f"{file_node}.colorSpace", "Utility - sRGB - Texture", type="string")
    cmds.setAttr(f"{file_node}.ignoreColorSpaceFileRules", 1)

    cmds.connectAttr(f"{file_node}.outColor", f"{colour_correction}.texture_map", f=True)



    return colour_correction

# ============================================================
# BUILD MATERIAL
# ============================================================

def build_material(material_name, data):
    shader = cmds.shadingNode("VRayMtl", asShader=True, name=material_name)
    sg = cmds.sets(renderable=True, noSurfaceShader=True, empty=True, name=f"{material_name}_SG")
    cmds.connectAttr(f"{shader}.outColor", f"{sg}.surfaceShader", f=True)

    # ----------------------------------
    # Base Color
    # ----------------------------------

    if "base_colour" in data:
        colour_file = create_texture_node(f"{material_name}_colour", data["base_colour"], raw=False)
        # AO multiply if found

        if "ao" in data:
            ao_file = create_texture_node(material_name + "_AO", data["ao"], raw=False)

            layered = cmds.shadingNode("VRayLayeredTex", asTexture=True, name=material_name + "_ao_layered")

            cmds.connectAttr(f"{colour_file}.outColor", f"{layered}.layers[0].tex", f=True)
            cmds.connectAttr(f"{ao_file}.outColor", f"{layered}.layers[1].tex", f=True)

            cmds.setAttr(f"{layered}.layers[0].name", color_file, type="string")
            cmds.setAttr(f"{layered}.layers[1].name", ao_file, type="string")

            color_output = layered + ".outColor"
        cmds.connectAttr(f"{colour_file}.outColor", f"{shader}.color", f=True)

    # ----------------------------------
    # Opacity
    # ----------------------------------

    if "opacity" in data:
        opacity = create_texture_node(f"{material_name}_opacity", data["opacity"], raw=True)
        cmds.connectAttr(f"{opacity}.outColor", f"{shader}.opacityMap", f=True)

    # ----------------------------------
    # Emission
    # ----------------------------------

    if "emission" in data:
        emission = create_texture_node(f"{material_name}_emission", data["emission"])
        cmds.connectAttr(f"{emission}.outColor", f"{shader}.illumColor", f=True)
        cmds.setAttr(f"{shader}.illumGI", 1)

    # ----------------------------------
    # Roughness
    # ----------------------------------

    if "roughness" in data:
        rough = create_texture_node(f"{material_name}_roughness", data["roughness"], raw=True)
        try:
            cmds.setAttr(f"{shader}.useRoughness", 1)
            cmds.setAttr(f"{shader}.reflectionColor", 1, 1, 1, type="double3")
            cmds.connectAttr(f"{rough}.outColor.outColorR", f"{shader}.reflectionGlossiness", f=True)
        except:
            pass

    # ----------------------------------
    # Metalness
    # ----------------------------------

    if "metalness" in data:
        metal = create_texture_node(f"{material_name}_metalness", data["metalness"], raw=True)
        try:
            cmds.connectAttr(f"{metal}.outAlpha", f"{shader}.metalness", f=True)
        except:
            pass

    # ----------------------------------
    # Normal
    # ----------------------------------

    if "normal" in data:
        normal_file = create_texture_node(f"{material_name}_normal", data["normal"], raw=True)
        # Set bump node to Tangent Space Normals
        cmds.setAttr(f"{shader}.bumpMapType", 1)
        cmds.connectAttr(f"{normal_file}.outColor", f"{shader}.bumpMap", force=True)

    # ----------------------------------
    # Height / Displacement
    # ----------------------------------

    if "displacement" in data:

        disp_file = create_texture_node(f"{material_name}_displacement", data["displacement"], raw=True)
        cmds.connectAttr(f"{disp_file}.outColor", f"{sg}.displacementShader", f=True)

    return shader


# ============================================================
# MAIN BUILD
# ============================================================

def createMaterial(name, data ):
    ensure_vray()
    print("Material Built")
    return build_material(name, data)


