import os
import re
from maya import cmds

# ============================================================
# SELECT TEXTURE FOLDER
# ============================================================

def choose_texture_folder():

    result = cmds.fileDialog2(
        dialogStyle=2,
        fileMode=3,  # Folder selection
        caption="Select Texture Folder"
    )

    if not result:
        cmds.warning("No folder selected.")
        return None

    return result[0]

# ============================================================
# LOAD VRAY
# ============================================================

def ensure_vray():
    if not cmds.pluginInfo("vrayformaya", q=True, loaded=True):
        try:
            cmds.loadPlugin("vrayformaya")
        except:
            raise RuntimeError("Could not load V-Ray")

# ============================================================
# FIND TEXTURES
# ============================================================

def find_materials(folder):
    keywords = {
        "basecolor": ["basecolor", "base_color", "albedo", "diffuse", "color", "diff"],
        "opacity": ["opacity", "opac", "alpha", "mask", "transparency, cutout"],
        "emission": ["emission", "emissive", "emit", "glow"],
        "roughness": ["roughness", "rough"],
        "metalness": ["metalness", "metallic", "metal"],
        "normal": ["normal", "nrm", "nor"],
        "ao": ["ao", "ambientocclusion", "ambient_occlusion", "occlusion"],
        "height": ["height", "disp", "displacement"]
    }

    materials = {}

    for file_name in os.listdir(folder):
        ext = os.path.splitext(file_name)[1].lower()
        if ext not in [".png", ".jpg", ".jpeg", ".tif", ".tiff", ".exr"]:
            continue

        lower = file_name.lower()

        for map_type, names in keywords.items():
            matched = False
            for word in names:
                if word in lower:
                    prefix = re.split(word, lower)[0]
                    prefix = prefix.rstrip("_- .")
                    if prefix not in materials:
                        materials[prefix] = {}
                    materials[prefix][map_type] = os.path.join(
                        folder,
                        file_name
                    )
                    matched = True
                    break
            if matched:
                break

    return materials

# ============================================================
# CREATE FILE NODE
# ============================================================

def create_texture_node(name, filepath, raw=False):
    file_node = cmds.shadingNode("file", asTexture=True, name=f"{name}_file")
    place = cmds.shadingNode("place2dTexture", asUtility=True, name=f"{name}_place2d")
    cc = cmds.shadingNode("VRayColorCorrection", asTexture=True, name=f"{name}_CC")

    cmds.connectAttr(f"{place}.outUV", f"{file_node}.uvCoord", f=True)
    cmds.connectAttr(f"{place}.outUvFilterSize", f"{file_node}.uvFilterSize", f=True)

    cmds.setAttr(f"{file_node}.fileTextureName", filepath, type="string")
    cmds.setAttr(f"{file_node}.colorSpace", "Utility - sRGB - Texture", type="string")
    cmds.setAttr(f"{file_node}.ignoreColorSpaceFileRules", 1)

    cmds.connectAttr(f"{file_node}.outColor", f"{cc}.texture_map", f=True)

    if raw:
        try:
            cmds.setAttr(f"{file_node}.colorSpace", "Utility - Raw", type="string")
        except:
            pass

    return cc

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

    if "basecolor" in data:
        color_file = create_texture_node(f"{material_name}_Color", data["basecolor"])
        color_output = color_file + ".texture_map"
        # AO multiply if found

        if "ao" in data:
            ao_file = create_texture_node(material_name + "_AO", data["ao"], raw=True)

            layered = cmds.shadingNode("VRayLayeredTex", asTexture=True, name=material_name + "_Layered")

            cmds.connectAttr(f"{color_file}.outColor", f"{layered}.layers[0].tex", f=True)
            cmds.connectAttr(f"{ao_file}.outColor", f"{layered}.layers[1].tex", f=True)

            cmds.setAttr(f"{layered}.layers[0].name", color_file, type="string")
            cmds.setAttr(f"{layered}.layers[1].name", ao_file, type="string")

            color_output = layered + ".outColor"
        cmds.connectAttr(color_output, shader + ".color", f=True)

    # ----------------------------------
    # Opacity
    # ----------------------------------

    if "opacity" in data:
        opacity = create_texture_node(f"{material_name}_Opacity", data["opacity"], raw=True)
        cmds.connectAttr(f"{opacity}.outColor", f"{shader}.opacityMap", f=True)

    # ----------------------------------
    # Emission
    # ----------------------------------

    if "emission" in data:
        emission = create_texture_node(f"{material_name}_Emission", data["emission"])
        cmds.connectAttr(f"{emission}.outColor", f"{shader}.illumColor", f=True)
        cmds.setAttr(f"{shader}.illumGI", 1)

    # ----------------------------------
    # Roughness
    # ----------------------------------

    if "roughness" in data:
        rough = create_texture_node(f"{material_name}_Roughness", data["roughness"], raw=True)
        try:
            cmds.setAttr(f"{shader}.useRoughness", 1)
            cmds.setAttr(f"{shader}.reflectionColor", 1, 1, 1, type="double3")
            cmds.connectAttr(f"{rough}.outColor.outColorR", f"{shader}.reflectionColorAmount", f=True)
        except:
            pass

    # ----------------------------------
    # Metalness
    # ----------------------------------

    if "metalness" in data:
        metal = create_texture_node(f"{material_name}_Metalness", data["metalness"], raw=True)
        try:
            cmds.connectAttr(f"{metal}.outAlpha", f"{shader}.metalness", f=True)
        except:
            pass

    # ----------------------------------
    # Normal
    # ----------------------------------

    if "normal" in data:
        normal_file = create_texture_node(material_name + "_Normal", data["normal"], raw=True)
        bump_node = cmds.shadingNode("bump2d", asUtility=True, name=material_name + "_Normal_Bump")
        # Set bump node to Tangent Space Normals
        cmds.setAttr(bump_node + ".bumpInterp", 1)
        cmds.connectAttr(normal_file + ".outAlpha", bump_node + ".bumpValue", force=True)
        cmds.connectAttr(bump_node + ".outNormal", shader + ".bumpMap", force=True)

    # ----------------------------------
    # Height / Displacement
    # ----------------------------------

    if "height" in data:

        disp_file = create_texture_node(f"{material_name}_Displacement", data["height"], raw=True)
        cmds.connectAttr(f"{disp_file}.outColor", f"{sg}.displacementShader", f=True)

    return shader


# ============================================================
# MAIN
# ============================================================

def build_all_materials(texture_folder):

    ensure_vray()
    mats = find_materials(texture_folder)

    for mat_name, data in mats.items():
        clean_name = mat_name.title().replace(" ", "_")
        print("Building:", clean_name)
        build_material(clean_name, data)


# ============================================================
# RUN
# ============================================================

texture_folder = choose_texture_folder()

if texture_folder:
    build_all_materials(texture_folder)