# MayaRSMaterialSetup_v1.1.4
# added a few more keywords to the filters to increase the chance of textures getting picked up straight away
# to do: 
#       add case-sensitive option (off by default)
#       add tab for adding and removing extra keywords
#       add new words to material creation script - ao, diff, disp, nor, rough
#       add a tickbox for switching between glossiness workflow
#       make the search paths include and not just exclusively be the common phrases
#       all other common texture files as well. (emission, SSS, transmission, opacity)
#       multiple tabs in the UI, one for settings with keywords etc.
#       tickbox for all maps that will hide or unhide selected map types
#       spit out all the files that weren't on that list and make sure they get sent back to the user in a new window for them to assign seperately
#       drag and drop functionality
#       rework it so that all extra options will open and close in a sort of dropdown fashion
#       when multiple files get linked to the same map, assign them to a list and open a new window indicating this. Allow the user to select one of these maps to move on
#       side tab for files that haven't been assigned to anything
#       button to toggle apply suffix to all nodes
#       figure out how to compress down the methods for the file opening boxes to 1 method
#       have a folder remembering function on the select multiple files button
#       remembering check state of tick boxes
#       could I condense the main file widgets down into a single method?
#       tick box to toggle projection type
#       add more shader options such as arnold

try:
    # Qt5
    from PySide2 import QtCore
    from PySide2 import QtWidgets
    from PySide2 import QtGui
    from shiboken2 import wrapInstance
except:
    # Qt6
    from PySide6 import QtCore
    from PySide6 import QtWidgets
    from PySide6 import QtGui
    from shiboken6 import wrapInstance

import maya.cmds as cmds
import sys
import maya.OpenMayaUI as omui
    
def maya_main_window():
    main_window_ptr = omui.MQtUtil.mainWindow()
    return wrapInstance(int(main_window_ptr), QtWidgets.QWidget)
    
class MainToolWindow(QtWidgets.QDialog):
    
    FILE_FILTERS = " All Files (*.*);; tif (*.tif *.tiff);; png (*.png);; \
    jpeg (*.jpeg *.jpg *.jp2);; exr (*.exr);; hdr (*.hdr);; tga (*.tga)"
    
    image_filters = "tif (*.tif *.tiff);; png (*.png);; \
    jpeg (*.jpeg *.jpg *.jp2);; exr (*.exr);; hdr (*.hdr);; tga (*.tga)"
    
    base_colour_filters = ["diffuse", "Diffuse", "base_colour", "albedo", "Albedo", "baseColour", "base_color", "baseColor", "BaseColour", "diff"]
    metallic_filters = ["metallic", "metalness", "Metalness", "Metallic"]
    roughness_filters = ["roughness", "Roughness", "Reflection", "reflection", "rough"]
    normal_filters = ["normal", "bump", "Normal", "Bump", "nor"]
    opacity_filters = ["opacity", "Opacity"]
    displacement_filters = ["displacement", "Displacement", "height", "Height", "DisplaceHeightField", "disp"]
    
    selected_filter = "Images ( )"
    
    def __init__(self, parent=maya_main_window()):
        super().__init__(parent)
        
        self.setWindowTitle("Redshift Material Creation")
        self.setMinimumSize(500, 600)
        
        self.rootDirectory = cmds.workspace(rootDirectory=True, query=True)
        self.defaultFolder = f"{self.rootDirectory}"
        if "sourceImages" in cmds.workspace(query=True, fileRuleList=True):
            self.defaultFolder += "/sourceImages"
        
        # On macOS make the window a Tool to keep it on top of Maya
        if sys.platform == "darwin":
            self.setWindowFlag(QtCore.Qt.Tool, True)
            
        self.create_widgets()
        self.create_layouts()
        self.create_connections()
            
    def create_widgets(self):
        """ This creates all the widgets required for the UI.

            Returns:

        """
        self.material_prefix_le = QtWidgets.QLineEdit()
        self.material_suffix_le = QtWidgets.QLineEdit("_mat")
        
        self.select_folder_btn = QtWidgets.QPushButton("Select Folder")
        self.select_multiple_files_btn = QtWidgets.QPushButton("Select Multiple Files")
        
        self.base_colour_cb = QtWidgets.QCheckBox()
        self.base_colour_cb.setChecked(True)
        self.base_colour_le = QtWidgets.QLineEdit()
        self.base_colour_UDIM_cb = QtWidgets.QCheckBox("UDIM")
        self.base_colour_btn = QtWidgets.QPushButton()
        self.base_colour_btn.setToolTip("Select File")
        self.base_colour_btn.setIcon(QtGui.QIcon(":fileOpen.png"))
                
        self.metallic_cb = QtWidgets.QCheckBox()
        self.metallic_cb.setChecked(True)
        self.metallic_le = QtWidgets.QLineEdit()
        self.metallic_UDIM_cb = QtWidgets.QCheckBox("UDIM")
        self.metallic_btn = QtWidgets.QPushButton()
        self.metallic_btn.setToolTip("Select File")
        self.metallic_btn.setIcon(QtGui.QIcon(":fileOpen.png"))
        
        self.roughness_cb = QtWidgets.QCheckBox()
        self.roughness_cb.setChecked(True)
        self.roughness_le = QtWidgets.QLineEdit()
        self.roughness_UDIM_cb = QtWidgets.QCheckBox("UDIM")
        self.roughness_btn = QtWidgets.QPushButton()
        self.roughness_btn.setToolTip("Select File")
        self.roughness_btn.setIcon(QtGui.QIcon(":fileOpen.png"))
        
        self.opacity_cb = QtWidgets.QCheckBox()
        self.opacity_cb.setChecked(True)
        self.opacity_le = QtWidgets.QLineEdit()
        self.opacity_UDIM_cb = QtWidgets.QCheckBox("UDIM")
        self.opacity_btn = QtWidgets.QPushButton()
        self.opacity_btn.setToolTip("Select File")
        self.opacity_btn.setIcon(QtGui.QIcon(":fileOpen.png"))
        
        self.normal_cb = QtWidgets.QCheckBox()
        self.normal_cb.setChecked(True)
        self.normal_le = QtWidgets.QLineEdit()
        self.normal_UDIM_cb = QtWidgets.QCheckBox("UDIM")
        self.normal_btn = QtWidgets.QPushButton()
        self.normal_btn.setToolTip("Select File")
        self.normal_btn.setIcon(QtGui.QIcon(":fileOpen.png"))
        
        self.displacement_cb = QtWidgets.QCheckBox()
        self.displacement_cb.setChecked(True)
        self.displacement_le = QtWidgets.QLineEdit()
        self.displacement_UDIM_cb = QtWidgets.QCheckBox("UDIM")
        self.displacement_btn = QtWidgets.QPushButton()
        self.displacement_btn.setToolTip("Select File")
        self.displacement_btn.setIcon(QtGui.QIcon(":fileOpen.png"))
        
        self.assign_obj_cb = QtWidgets.QCheckBox("Assign to Selected Objects")
        
        self.create_and_close_btn = QtWidgets.QPushButton("Create And Close")
        self.create_material_btn = QtWidgets.QPushButton("Create Material")
        self.close_btn = QtWidgets.QPushButton("Close")
        
    def create_layouts(self):
        """ This creates all the layouts for the UI.

            Returns:
                Does not need to return anything given its use case.
        """
        material_prefix_layout = QtWidgets.QHBoxLayout()
        material_prefix_layout.addWidget(self.material_prefix_le)
        material_suffix_layout = QtWidgets.QHBoxLayout()
        material_suffix_layout.addWidget(self.material_suffix_le)
        material_layout = QtWidgets.QFormLayout()
        material_layout.addRow("Material Prefix: ", material_prefix_layout)
        material_layout.addRow("Material Suffix: ", material_suffix_layout)
        
        top_button_layout = QtWidgets.QHBoxLayout()
        top_button_layout.addWidget(self.select_folder_btn)
        top_button_layout.addWidget(self.select_multiple_files_btn)
        
        base_colour_layout_top = QtWidgets.QHBoxLayout()
        base_colour_layout_top.setSpacing(0)
        base_colour_layout_top.addWidget(self.base_colour_cb)
        base_colour_layout_top.addWidget(self.base_colour_le)
        base_colour_layout_top.addWidget(self.base_colour_btn)
        
        base_colour_layout_bot = QtWidgets.QHBoxLayout()
        base_colour_layout_bot.addWidget(self.base_colour_UDIM_cb)
        
        base_colour_layout = QtWidgets.QFormLayout()
        base_colour_layout.setSpacing(2)
        base_colour_layout.addRow(base_colour_layout_top)
        base_colour_layout.addRow(base_colour_layout_bot)
        
        metallic_layout_top = QtWidgets.QHBoxLayout()
        metallic_layout_top.addWidget(self.metallic_cb)
        metallic_layout_top.addWidget(self.metallic_le)
        metallic_layout_top.addWidget(self.metallic_btn)
        
        metallic_layout_bot = QtWidgets.QHBoxLayout()
        metallic_layout_bot.addWidget(self.metallic_UDIM_cb)
        
        metallic_layout = QtWidgets.QFormLayout()
        metallic_layout.addRow(metallic_layout_top)
        metallic_layout.addRow(metallic_layout_bot)

        roughness_layout_top = QtWidgets.QHBoxLayout()
        roughness_layout_top.addWidget(self.roughness_cb)
        roughness_layout_top.addWidget(self.roughness_le)
        roughness_layout_top.addWidget(self.roughness_btn)
        
        roughness_layout_bot = QtWidgets.QHBoxLayout()
        roughness_layout_bot.addWidget(self.roughness_UDIM_cb)
        
        roughness_layout = QtWidgets.QFormLayout()
        roughness_layout.addRow(roughness_layout_top)
        roughness_layout.addRow(roughness_layout_bot)
        
        opacity_layout_top = QtWidgets.QHBoxLayout()
        opacity_layout_top.setSpacing(0)
        opacity_layout_top.addWidget(self.opacity_cb)
        opacity_layout_top.addWidget(self.opacity_le)
        opacity_layout_top.addWidget(self.opacity_btn)
        
        opacity_layout_bot = QtWidgets.QHBoxLayout()
        opacity_layout_bot.addWidget(self.opacity_UDIM_cb)
        
        opacity_layout = QtWidgets.QFormLayout()
        opacity_layout.setSpacing(2)
        opacity_layout.addRow(opacity_layout_top)
        opacity_layout.addRow(opacity_layout_bot)
        
        normal_layout_top = QtWidgets.QHBoxLayout()
        normal_layout_top.addWidget(self.normal_cb)
        normal_layout_top.addWidget(self.normal_le)
        normal_layout_top.addWidget(self.normal_btn)
        
        normal_layout_bot = QtWidgets.QHBoxLayout()
        normal_layout_bot.addWidget(self.normal_UDIM_cb)
        
        normal_layout = QtWidgets.QFormLayout()
        normal_layout.addRow(normal_layout_top)
        normal_layout.addRow(normal_layout_bot)
        
        displacement_layout_top = QtWidgets.QHBoxLayout()
        displacement_layout_top.addWidget(self.displacement_cb)
        displacement_layout_top.addWidget(self.displacement_le)
        displacement_layout_top.addWidget(self.displacement_btn)
        
        displacement_layout_bot = QtWidgets.QHBoxLayout()
        displacement_layout_bot.addWidget(self.displacement_UDIM_cb)
        
        displacement_layout = QtWidgets.QFormLayout()
        displacement_layout.addRow(displacement_layout_top)
        displacement_layout.addRow(displacement_layout_bot)
        
        global_options_layout = QtWidgets.QHBoxLayout()
        global_options_layout.addWidget(self.assign_obj_cb)
        
        button_layout = QtWidgets.QHBoxLayout()
        button_layout.addWidget(self.create_and_close_btn)
        button_layout.addWidget(self.create_material_btn)
        button_layout.addWidget(self.close_btn)
        
        form_layout = QtWidgets.QFormLayout()
        form_layout.addRow(material_layout)
        form_layout.addRow(top_button_layout)
        form_layout.addRow("Base Colour:", base_colour_layout)
        form_layout.addRow("Metallic: ", metallic_layout)
        form_layout.addRow("Roughness: ", roughness_layout)
        form_layout.addRow("Opacity: ", opacity_layout)
        form_layout.addRow("Normal: ", normal_layout)
        form_layout.addRow("Displacement: ", displacement_layout)
        
        main_layout = QtWidgets.QVBoxLayout(self)
        main_layout.setSpacing(2)
        main_layout.addLayout(form_layout)
        main_layout.addStretch()
        main_layout.addLayout(global_options_layout)
        main_layout.addLayout(button_layout)
        
    def create_connections(self):
        """  This creates all the connections which enables the functionality of the UI user inputs.

            Returns:
                Does not return anything given the nature of the function.
        """
        # top buttons
        self.select_folder_btn.clicked.connect(self.select_folder)
        self.select_multiple_files_btn.clicked.connect(self.select_multiple_files)
        
        # file paths
        self.base_colour_btn.clicked.connect(self.show_file_select_base_colour)
        self.metallic_btn.clicked.connect(self.show_file_select_metallic)
        self.roughness_btn.clicked.connect(self.show_file_select_roughness)
        self.opacity_btn.clicked.connect(self.show_file_select_opacity)
        self.normal_btn.clicked.connect(self.show_file_select_normal)
        self.displacement_btn.clicked.connect(self.show_file_select_displacement)
        
        # checkbox connections
        self.base_colour_cb.toggled.connect(self.update_base_colour_visibility)
        self.metallic_cb.toggled.connect(self.update_metallic_visibility)
        self.roughness_cb.toggled.connect(self.update_roughness_visibility)
        self.opacity_cb.toggled.connect(self.update_opacity_visibility)
        self.normal_cb.toggled.connect(self.update_normal_visibility)
        self.displacement_cb.toggled.connect(self.update_displacement_visibility)
        
        # lower buttons
        self.create_and_close_btn.clicked.connect(self.creatingMateralAndClose)
        self.create_material_btn.clicked.connect(self.creatingMaterial)
        self.close_btn.clicked.connect(self.close)
        
    # defining the various checkboxes    
        
    def update_base_colour_visibility(self, checked):
        self.base_colour_le.setEnabled(checked)
        self.base_colour_btn.setEnabled(checked)
        
    def update_metallic_visibility(self, checked):
        self.metallic_le.setEnabled(checked)
        self.metallic_btn.setEnabled(checked)
        
    def update_roughness_visibility(self, checked):
        self.roughness_le.setEnabled(checked)
        self.roughness_btn.setEnabled(checked)
        
    def update_opacity_visibility(self, checked):
        self.opacity_le.setEnabled(checked)
        self.opacity_btn.setEnabled(checked)
        
    def update_normal_visibility(self, checked):
        self.normal_le.setEnabled(checked)
        self.normal_btn.setEnabled(checked)
        
    def update_displacement_visibility(self, checked):
        self.displacement_le.setEnabled(checked)
        self.displacement_btn.setEnabled(checked)
        
# function for the file opening boxes for each map type. I'm sure this can be done in 1 function...
        
    def show_file_select_base_colour(self):
        file_path, self.selected_filter = QtWidgets.QFileDialog.getOpenFileName(
        self, "Select File", "", self.FILE_FILTERS, self.selected_filter)
        
        # below makes sure code is run just in case user closed dialog box
        if file_path:
            # adding the returned file path to the line edit
            self.base_colour_le.setText(file_path)
            
    def show_file_select_metallic(self):
        file_path, self.selected_filter = QtWidgets.QFileDialog.getOpenFileName(
        self, "Select File", "", self.FILE_FILTERS, self.selected_filter)
        
        if file_path:
            self.metallic_le.setText(file_path)
            
    def show_file_select_roughness(self):
        file_path, self.selected_filter = QtWidgets.QFileDialog.getOpenFileName(
        self, "Select File", "", self.FILE_FILTERS, self.selected_filter)
        
        if file_path:
            self.roughness_le.setText(file_path)
            
    def show_file_select_opacity(self):
        file_path, self.selected_filter = QtWidgets.QFileDialog.getOpenFileName(
        self, "Select File", "", self.FILE_FILTERS, self.selected_filter)
        
        if file_path:
            self.opacity_le.setText(file_path)
            
    def show_file_select_normal(self):
        file_path, self.selected_filter = QtWidgets.QFileDialog.getOpenFileName(
        self, "Select File", "", self.FILE_FILTERS, self.selected_filter)
        
        if file_path:
            self.normal_le.setText(file_path)
            
    def show_file_select_displacement(self):
        file_path, self.selected_filter = QtWidgets.QFileDialog.getOpenFileName(
        self, "Select File", "", self.FILE_FILTERS, self.selected_filter)
        
        if file_path:
            self.displacement_le.setText(file_path)
    
    # top buttons for quick assignment
    
    def file_scanner(self, directory, specificFilters, file_list, mapType, folder=True):
            self.mapType = mapType
            self.specificFilters = specificFilters
            self.directory = directory
            
            located_file = []
            for file in file_list:
                for search_filter in specificFilters:
                    if search_filter in file:
                        located_file.append(file)
            
            if folder:
                if len(located_file) == 1:
                    mapType.setText(f"{self.directory}/{located_file[0]}")
                elif len(located_file) > 1:
                    
                    print(f"More than 1 file located: {located_file}")
            else:
                if len(located_file) == 1:
                    mapType.setText(located_file[0])
                elif len(located_file) > 1:
                    print(f"More than 1 file located: {located_file}")
            return None
    
    def select_folder(self):
    
        def folder_popup(self):
            dir = QtWidgets.QFileDialog.getExistingDirectory(
            self, "Select Folder", self.defaultFolder)
            if dir:
                self.defaultFolder = dir
            files = ""
            
            if dir:
                directory = QtCore.QDir(dir)
                directory.setNameFilters(self.image_filters)
                files = directory.entryList()
            else:
                print("Please select a valid folder")
                
            return files, dir
        
        self.defined_files, self.directory = folder_popup(self)
        
        base_colour_assign = self.file_scanner(self.directory, 
            self.base_colour_filters, self.defined_files, self.base_colour_le)
            
        metallic_assign = self.file_scanner(self.directory, 
            self.metallic_filters, self.defined_files, self.metallic_le)
            
        roughness_assign = self.file_scanner(self.directory, 
            self.roughness_filters, self.defined_files, self.roughness_le)
            
        opacity_assign = self.file_scanner(self.directory, 
            self.opacity_filters, self.defined_files, self.opacity_le)
        
        normal_assign = self.file_scanner(self.directory, 
            self.normal_filters, self.defined_files, self.normal_le)
            
        displacement_assign = self.file_scanner(self.directory, 
            self.displacement_filters, self.defined_files, self.displacement_le)

    def select_multiple_files(self):
        file_paths, self.selected_filter = QtWidgets.QFileDialog.getOpenFileNames(
        self, "Select Files", self.defaultFolder, self.FILE_FILTERS, self.selected_filter)
        
        self.directory = ""
        self.defined_files = file_paths
        
        base_colour_assign = self.file_scanner(self.directory, 
            self.base_colour_filters, self.defined_files, self.base_colour_le, folder=False)
            
        metallic_assign = self.file_scanner(self.directory, 
            self.metallic_filters, self.defined_files, self.metallic_le, folder=False)
            
        roughness_assign = self.file_scanner(self.directory, 
            self.roughness_filters, self.defined_files, self.roughness_le, folder=False)
            
        opacity_assign = self.file_scanner(self.directory, 
            self.opacity_filters, self.defined_files, self.opacity_le, folder=False)
            
        normal_assign = self.file_scanner(self.directory, 
            self.normal_filters, self.defined_files, self.normal_le, folder=False)
            
        displacement_assign = self.file_scanner(self.directory, 
            self.displacement_filters, self.defined_files, self.displacement_le, folder=False)
        
        print(file_paths)
    
    # retrieving the material prefix and suffix name text
    def get_material_prefix_name(self):
        return(self.material_prefix_le.text())
        
    def get_material_suffix_name(self):
        return(self.material_suffix_le.text())
        
    # retrieving the selected file names ready to be input into the file nodes 
    
    def base_colour_file_path(self):
        return(self.base_colour_le.text())
        
    def metallic_file_path(self):
        return(self.metallic_le.text())
        
    def roughness_file_path(self):
        return(self.roughness_le.text())
        
    def opacity_file_path(self):
        return(self.opacity_le.text())
        
    def normal_file_path(self):
        return(self.normal_le.text())
        
    def displacement_file_path(self):
        return(self.displacement_le.text())

    
    ####################################
    # MATERIAL HEIRARCHY CREATION
    ####################################
    def createMaterial(self):
        
        self.selectedObjects = cmds.ls(sl=True)
        self.materialCustomPrefix = self.get_material_prefix_name()
        self.materialCustomSuffix = self.get_material_suffix_name()
        
        if len(self.materialCustomPrefix) == 0:
            self.materialCustomPrefix = "rsStandardMaterial"
            
        if len(self.materialCustomSuffix) == 0:
            self.materialCustomSuffix = ""
            
        self.full_name = f"{self.materialCustomPrefix}{self.materialCustomSuffix}#"
        print(self.full_name)
        
        # creating variabvles for each file path
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
        
        if self.assign_obj_cb.isChecked():
            for object in self.selectedObjects:
                cmds.select(object)
                cmds.hyperShade(assign=self.materialNode[0]) 

    def creatingMaterial(self):
        self.redshiftMaterial = self.createMaterial()
        
    def creatingMateralAndClose(self):
        self.redshiftMaterial = self.createMaterial()
        self.close()
   
        
if __name__ == "__main__":
    try:
        RSMat_Create.close()        # pylint: disable=E0601
        RSMat_Create.deleteLater()
    except:
        pass

    RSMat_Create = MainToolWindow()
    RSMat_Create.show()
