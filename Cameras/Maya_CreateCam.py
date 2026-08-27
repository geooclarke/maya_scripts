# Maya_CreateCam_v1.0.4.py
# features to add:   Create camera and close when hitting enter when on line edit
#                    If setting suffix manually, the code to recognise this and not add an extra suffix
#                    Nurbs curves as controls to make it a bit more user friendly

try:
    from PySide2 import QtWidgets
    from PySide2 import QtCore
    from shiboken2 import wrapInstance
except:
    from PySide6 import QtWidgets
    from PySide6 import QtCore
    from shiboken6 import wrapInstance

import maya.OpenMayaUI as omui

# converting the maya main window as a python object in order to keep the new window on top.
# notice it is defined above the class method
def maya_main_window():
    main_window_ptr = omui.MQtUtil.mainWindow()
    return wrapInstance(int(main_window_ptr), QtWidgets.QWidget)


class GCCreateCamWindow(QtWidgets.QDialog):
    
    def __init__(self, parent=maya_main_window()):
        super().__init__(parent)
        
        self.setWindowTitle("Create Camera")
        self.setMinimumSize(400, 90)
        
        self.create_widgets()
        self.create_layouts()
        self.create_connections()
        
        
    def create_widgets(self):
        self.camera_name_le = QtWidgets.QLineEdit()
        
        self.create_camera_btn = QtWidgets.QPushButton("Create Camera")
        self.create_camera_and_close_btn = QtWidgets.QPushButton("Create and Close")
        self.cancel_btn = QtWidgets.QPushButton("Cancel")
        
    def create_layouts(self):
        self.name_layout = QtWidgets.QFormLayout()
        self.name_layout.addRow("Camera Name: ", self.camera_name_le)
        
        self.button_layout = QtWidgets.QHBoxLayout()
        self.button_layout.addWidget(self.create_camera_and_close_btn)
        self.button_layout.addWidget(self.create_camera_btn)
        self.button_layout.addWidget(self.cancel_btn)
        
        self.main_layout = QtWidgets.QVBoxLayout(self)
        self.main_layout.setSpacing(2)
        self.main_layout.setContentsMargins(5, 5, 5, 5)
        self.main_layout.addLayout(self.name_layout)
        self.main_layout.addStretch()
        self.main_layout.addLayout(self.button_layout)
        
    def create_connections(self):
        
        # buttons
        self.create_camera_and_close_btn.clicked.connect(self.createAndClose)
        self.create_camera_btn.clicked.connect(self.createCamera)
        self.cancel_btn.clicked.connect(self.close)
        
    def get_camera_name(self):
        return(self.camera_name_le.text())
    
# main camera method
    def createCamera(self, *args):
        self.camName = self.get_camera_name()
        
        def create_camera(camera_name):
            self.create_rendercam = cmds.camera()

            if len(camera_name) > 0:
                self.rename_cam = cmds.rename(self.create_rendercam[0], f"{camera_name}#")

            self.cam_main = cmds.ls(sl=True)
            self.camera_shape = cmds.listRelatives(self.cam_main, children=True)
            self.camera_list = [self.cam_main[0], self.camera_shape[0]]
            self.camera_attrs = ['translate', 'rotate']
            self.camera_axis = ['X', 'Y']
            
            # run through each attribute and lock accordingly
            for axis in self.camera_axis:
                for attr in self.camera_attrs:
                    cmds.setAttr(f"{self.camera_list[0]}.{attr}{axis}", lock=1)
            return self.camera_list
        
        # define the function that will lock the attributes on the tilt group
        def lock_tilt_attrs(name):
            tilt_axis = ["X", "Y", "Z"]
            tilt_attrs = ["translate", "rotate", "scale"]
            obj = cmds.ls(sl=True)[0]
            
            # skipping the X axis to avoid locking
            for axis in tilt_axis:
                if axis != "X":
                    for attr in tilt_attrs:
                        cmds.setAttr(f"{obj}.{attr}{axis}", lock=1)
                else:
                    for attr in tilt_attrs:
                        if attr != "rotate":
                            cmds.setAttr(f"{obj}.{attr}{axis}", lock=1)
            return
            
        # define the function that will lock the the attributes on the crane group
        def lock_crane_attrs(name):
                tilt_axis = ["X",]
                tilt_attrs = ["rotate"]
                obj = cmds.ls(sl=True)[0]
                
                for axis in tilt_axis:
                    for attr in tilt_attrs:
                        cmds.setAttr(f"{obj}.{attr}{axis}", lock=1)
                return
        
        # define the group creation
        def create_grp(name):
            cmds.group(name=name) # indexing is so that it only selects the transform node
            return name
        
        # define locator
        def createLocator(name):
            name = name
            locator_size = 10
            locator = cmds.spaceLocator(n=name)
            cmds.setAttr(f"{locator[0]}.localScaleX", locator_size)
            cmds.setAttr(f"{locator[0]}.localScaleY", locator_size)
            cmds.setAttr(f"{locator[0]}.localScaleZ", locator_size)
            return name
        
        self.cam = create_camera(self.camName)
        self.camMain = self.cam[0]
        self.tilt_grp = create_grp(f"{self.camMain}_tilt")
        lock_tilt_attrs((cmds.ls(sl=True)[0]))
        self.crane_grp = create_grp(f"{self.camMain}_crane")
        lock_crane_attrs((cmds.ls(sl=True)[0]))
        
        # creation of the locators and distance object
        self.loc_1 = createLocator(f"{self.camMain}_DoF_loc_1")
        self.loc_2 = createLocator(f"{self.camMain}_DoF_loc_2")
        
        cmds.move(0, 1, 0, self.loc_1)
        self.startPoint = cmds.getAttr(f"{self.loc_1}.translate")
        self.endPoint = cmds.getAttr(f"{self.loc_2}.translate")
        self.create_dist = cmds.distanceDimension(sp=self.startPoint[0], ep=self.endPoint[0])
        cmds.move(0, 0, 0, self.loc_1)
        self.distDimParent = cmds.listRelatives(self.create_dist, p=True)
        cmds.select(clear=True)
        self.distDimParent = cmds.rename(self.distDimParent, f"{self.camMain}_DoF")
        
        # parenting to the main group
        cmds.parent(self.loc_2, self.tilt_grp)
        cmds.parent(self.loc_1, self.crane_grp)
        cmds.parent(self.distDimParent, self.crane_grp)
        cmds.select(clear=True)
        cmds.parentConstraint(self.camMain, self.loc_2)
        
        cmds.expression(o=self.camMain, s=(f"{self.camMain}.focusDistance = {self.distDimParent}.distance"))
        
        # setting up a few basic camera settings
        cmds.setAttr(f"{self.camMain}.locatorScale", 10)                
        cmds.setAttr(f"{self.camMain}.translateZ", 10)
        
        return
        
    def createAndClose(self):
        self.createCamera()
        self.close()    
    
if __name__ == "__main__":
    try:
        win.close()        # pylint: disable=E0601
        win.deleteLater()
    except:
        pass
    win = GCCreateCamWindow()
    win.show()
