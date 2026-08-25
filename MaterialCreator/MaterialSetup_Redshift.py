from maya import cmds

####################################
# MATERIAL HEIRARCHY CREATION
####################################


def createMaterial(self, name):

    self.materialCustomPrefix = self.get_material_prefix_name()
    self.materialCustomSuffix = self.get_material_suffix_name()

    if len(self.materialCustomPrefix) == 0:
        self.materialCustomPrefix = "rsStandardMaterial"

    if len(self.materialCustomSuffix) == 0:
        self.materialCustomSuffix = ""

    self.full_name = f"{self.materialCustomPrefix}{self.materialCustomSuffix}#"

    # creating variables for each file path
    self.base_colour_file = self.base_colour_file_path()
    self.metallic_file = self.metallic_file_path()
    self.roughness_file = self.roughness_file_path()
    self.normal_file = self.normal_file_path()
    self.displacement_file = self.displacement_file_path()

    # creating the standard material node
    def createStandardMaterial(self, *args):
        self.materialList = []
        self.materialCreation = cmds.shadingNode('RedshiftStandardMaterial', asShader=True, name=self.full_name)
        self.shadingGroup = cmds.sets(renderable=True, noSurfaceShader=True, empty=True, name=f'{self.full_name}SG')
        cmds.connectAttr(f"{self.materialCreation}.outColor", f"{self.shadingGroup}.surfaceShader")
        self.materialList.append(self.materialCreation)
        self.materialList.append(self.shadingGroup)

        return self.materialList

    def createTextureFile(self, mapType, raw=False):

        def createFileNode(self):
            self.mapType = mapType
            self.fileName = self.materialCustomPrefix
            self.fileNode = cmds.shadingNode('file', asTexture=True, name=f"{self.materialCustomPrefix}_{self.mapType}_#")
            cmds.setAttr(f"{self.fileNode}.filterType", False)
            cmds.setAttr(f"{self.fileNode}.uvTilingMode", 0)
            return self.fileNode

        def create_place2dNode(self):
            self.place2dNode = cmds.shadingNode('place2dTexture', asUtility=True)
            return self.place2dNode

        def attachFileNodeToPlace2d(self, place2dNode, fileNode):
            cmds.connectAttr(f"{self.place2dNode}.coverage", f"{self.fileNode}.coverage")
            cmds.connectAttr(f"{self.place2dNode}.translateFrame", f"{self.fileNode}.translateFrame")
            cmds.connectAttr(f"{self.place2dNode}.rotateFrame", f"{self.fileNode}.rotateFrame")
            cmds.connectAttr(f"{self.place2dNode}.mirrorU", f"{self.fileNode}.mirrorU")
            cmds.connectAttr(f"{self.place2dNode}.mirrorV", f"{self.fileNode}.mirrorV")
            cmds.connectAttr(f"{self.place2dNode}.stagger", f"{self.fileNode}.stagger")
            cmds.connectAttr(f"{self.place2dNode}.wrapU", f"{self.fileNode}.wrapU")
            cmds.connectAttr(f"{self.place2dNode}.wrapV", f"{self.fileNode}.wrapV")
            cmds.connectAttr(f"{self.place2dNode}.repeatUV", f"{self.fileNode}.repeatUV")
            cmds.connectAttr(f"{self.place2dNode}.offset", f"{self.fileNode}.offset")
            cmds.connectAttr(f"{self.place2dNode}.rotateUV", f"{self.fileNode}.rotateUV")
            cmds.connectAttr(f"{self.place2dNode}.noiseUV", f"{self.fileNode}.noiseUV")
            cmds.connectAttr(f"{self.place2dNode}.vertexUvOne", f"{self.fileNode}.vertexUvOne")
            cmds.connectAttr(f"{self.place2dNode}.vertexUvTwo", f"{self.fileNode}.vertexUvTwo")
            cmds.connectAttr(f"{self.place2dNode}.vertexUvThree", f"{self.fileNode}.vertexUvThree")
            cmds.connectAttr(f"{self.place2dNode}.vertexCameraOne", f"{self.fileNode}.vertexCameraOne")
            cmds.connectAttr(f"{self.place2dNode}.outUV", f"{self.fileNode}.uv")
            cmds.connectAttr(f"{self.place2dNode}.outUvFilterSize", f"{self.fileNode}.uvFilterSize")


        self.create2dNode = create_place2dNode(self)
        self.createFile = createFileNode(self)

        if raw:
            cmds.setAttr(f"{self.createFile}.ignoreColorSpaceFileRules", 1)
            cmds.setAttr(f"{self.createFile}.colorSpace", "Raw", type="string")
            cmds.setAttr(f"{self.createFile}.alphaIsLuminance", 1)

        attachFileNodeToPlace2d(self, self.create2dNode, self.createFile)

        return self.createFile

    def normalNode(self):
        self.bumpNode = cmds.shadingNode("RedshiftBumpMap", asTexture=True)
        cmds.setAttr(f"{self.bumpNode}.inputType", 1)
        cmds.setAttr(f"{self.bumpNode}.scale", 1)

        return self.bumpNode

    # creating main node structure based on the tickbox
    self.materialNode = createStandardMaterial(self)
    if self.base_colour_cb.isChecked() and len(self.base_colour_le.text()) > 0:
        self.baseColourFile = createTextureFile(self, "base_colour")
        cmds.setAttr(f"{self.baseColourFile}.fileTextureName", f"{self.base_colour_file}", type="string")
        cmds.connectAttr(f"{self.baseColourFile}.outColor", f"{self.materialNode[0]}.base_color")
        if self.base_colour_UDIM_cb.isChecked():
            cmds.setAttr(f"{self.baseColourFile}.uvTilingMode", 3)

    if self.metallic_cb.isChecked() and len(self.metallic_le.text()) > 0:
        self.metallicFile = createTextureFile(self, "metallic", raw=True)
        cmds.setAttr(f"{self.metallicFile}.fileTextureName", f"{self.metallic_file}", type="string")
        cmds.connectAttr(f"{self.metallicFile}.outAlpha", f"{self.materialNode[0]}.metalness")
        if self.metallic_UDIM_cb.isChecked():
            cmds.setAttr(f"{self.metallicFile}.uvTilingMode", 3)

    if self.roughness_cb.isChecked() and len(self.roughness_le.text()) > 0:
        self.roughnessFile = createTextureFile(self, "roughness", raw=True)
        cmds.setAttr(f"{self.roughnessFile}.fileTextureName", f"{self.roughness_file}", type="string")
        cmds.connectAttr(f"{self.roughnessFile}.outAlpha", f"{self.materialNode[0]}.refl_roughness")
        if self.roughness_UDIM_cb.isChecked():
            cmds.setAttr(f"{self.roughnessFile}.uvTilingMode", 3)

    if self.normal_cb.isChecked() and len(self.normal_le.text()) > 0:
        self.normalFile = createTextureFile(self, "normal", raw=True)
        cmds.setAttr(f"{self.normalFile}.fileTextureName", f"{self.normal_file}", type="string")
        self.bumpNode = normalNode(self)
        cmds.connectAttr(f"{self.normalFile}.outColor", f"{self.bumpNode}.input")
        cmds.connectAttr(f"{self.bumpNode}.out", f"{self.materialNode[0]}.bump_input")
        if self.normal_UDIM_cb.isChecked():
            cmds.setAttr(f"{self.normalFile}.uvTilingMode", 3)

    if self.displacement_cb.isChecked() and len(self.displacement_le.text()) > 0:
        self.displacementFile = createTextureFile(self, "displacement", raw=True)
        cmds.setAttr(f"{self.displacementFile}.fileTextureName", f"{self.displacement_file}", type="string")
        self.displacementNode = cmds.shadingNode("RedshiftDisplacement", asShader=True)
        cmds.connectAttr(f"{self.displacementFile}.outColor", f"{self.displacementNode}.texMap")
        cmds.connectAttr(f"{self.displacementNode}.out", f"{self.materialNode[1]}.displacementShader")
        if self.displacement_UDIM_cb.isChecked():
            cmds.setAttr(f"{self.displacementFile}.uvTilingMode", 3)

