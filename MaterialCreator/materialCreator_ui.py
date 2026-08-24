import maya.cmds as cmds
import sys
import maya.OpenMayaUI as omui
import PySide2
from PySide2.QtCore import *
from PySide2.QtGui import *
from PySide2.QtWidgets import *

import Maya_MaterialSetup_Redshift


def maya_main_window():
    main_window_ptr = omui.MQtUtil.mainWindow()
    return wrapInstance(int(main_window_ptr), QtWidgets.QWidget)


class MainToolWindow(QtWidgets.QDialog):
    FILE_FILTERS = " All Files (*.*);; tif (*.tif *.tiff);; png (*.png);; \
    jpeg (*.jpeg *.jpg *.jp2);; exr (*.exr);; hdr (*.hdr);; tga (*.tga)"

    image_filters = "tif (*.tif *.tiff);; png (*.png);; \
    jpeg (*.jpeg *.jpg *.jp2);; exr (*.exr);; hdr (*.hdr);; tga (*.tga)"

    base_colour_filters = ["diffuse", "Diffuse", "base_colour", "albedo", "Albedo", "baseColour", "base_color",
                           "baseColor", "BaseColour", "diff"]
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
                                               self.base_colour_filters, self.defined_files, self.base_colour_le,
                                               folder=False)

        metallic_assign = self.file_scanner(self.directory,
                                            self.metallic_filters, self.defined_files, self.metallic_le, folder=False)

        roughness_assign = self.file_scanner(self.directory,
                                             self.roughness_filters, self.defined_files, self.roughness_le,
                                             folder=False)

        opacity_assign = self.file_scanner(self.directory,
                                           self.opacity_filters, self.defined_files, self.opacity_le, folder=False)

        normal_assign = self.file_scanner(self.directory,
                                          self.normal_filters, self.defined_files, self.normal_le, folder=False)

        displacement_assign = self.file_scanner(self.directory,
                                                self.displacement_filters, self.defined_files, self.displacement_le,
                                                folder=False)

        print(file_paths)

    # retrieving the material prefix and suffix name text
    def get_material_prefix_name(self):
        return (self.material_prefix_le.text())

    def get_material_suffix_name(self):
        return (self.material_suffix_le.text())

    # retrieving the selected file names ready to be input into the file nodes

    def base_colour_file_path(self):
        return (self.base_colour_le.text())

    def metallic_file_path(self):
        return (self.metallic_le.text())

    def roughness_file_path(self):
        return (self.roughness_le.text())

    def opacity_file_path(self):
        return (self.opacity_le.text())

    def normal_file_path(self):
        return (self.normal_le.text())

    def displacement_file_path(self):
        return (self.displacement_le.text())

def creatingMaterial(self):
    self.redshiftMaterial = Maya_MaterialSetup_Redshift.createMaterial()

def creatingMateralAndClose(self):
    self.redshiftMaterial = Maya_MaterialSetup_Redshift.createMaterial()
    self.close()

if __name__ == "__main__":
    try:
        Mat_Create.close()  # pylint: disable=E0601
        Mat_Create.deleteLater()
    except:
        pass

    Mat_Create = MainToolWindow()
    Mat_Create.show()