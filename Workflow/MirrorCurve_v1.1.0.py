try:
    from PySide2 import QtWidgets
    from PySide2 import QtCore
    from shiboken2 import wrapInstance
except:
    from PySide6 import QtWidgets
    from PySide6 import QtCore
    from shiboken6 import wrapInstance

import maya.OpenMaya as om
import maya.OpenMayaUI as omui

# converting the maya main window as a python object in order to keep the new window on top.
# notice it is defined above the class method
def maya_main_window():
    main_window_ptr = omui.MQtUtil.mainWindow()
    return wrapInstance(int(main_window_ptr), QtWidgets.QWidget)


class MainToolWindow(QtWidgets.QDialog):
    
    def __init__(self, parent=maya_main_window()):
        super().__init__(parent)
        
        self.setWindowTitle("Mirror Curve")
        self.setMinimumSize(400, 150)
        
        self.create_widgets()
        self.create_layouts()
        self.create_connections()
        
        
    def create_widgets(self):
        self.define_axis_x_radio_btn = QtWidgets.QRadioButton("X", self)
        self.define_axis_y_radio_btn = QtWidgets.QRadioButton("Y", self)
        self.define_axis_z_radio_btn = QtWidgets.QRadioButton("Z", self)
        
        self.delete_old_curves_checkbox = QtWidgets.QCheckBox("Delete Old Curves", self)
        
        self.information_text = QtWidgets.QLabel()
        self.information_text.setText("Select only 1 curve, then run.")
        #self.information_text.setText("test")
        
        self.create_and_close_btn = QtWidgets.QPushButton("Create and Close")
        self.create_curve_btn = QtWidgets.QPushButton("Create Curve")
        self.close_btn = QtWidgets.QPushButton("Close")
        
    def create_layouts(self):
        axis_layout = QtWidgets.QHBoxLayout()
        axis_layout.addWidget(self.define_axis_x_radio_btn)
        axis_layout.addWidget(self.define_axis_y_radio_btn)
        axis_layout.addWidget(self.define_axis_z_radio_btn)
        self.define_axis_x_radio_btn.setChecked(True)
        
        axis_main_layout = QtWidgets.QFormLayout()
        axis_main_layout.addRow("Define Axis:", axis_layout)
        
        delete_old_curves_layout = QtWidgets.QHBoxLayout()
        delete_old_curves_layout.addWidget(self.delete_old_curves_checkbox)
        
        information_layout = QtWidgets.QFormLayout()
        information_layout.addRow(self.information_text)
        #information_layout.addWidget(self.information_text)
        
        button_layout = QtWidgets.QHBoxLayout()
        button_layout.addWidget(self.create_and_close_btn)
        button_layout.addWidget(self.create_curve_btn)
        button_layout.addWidget(self.close_btn)
        
        main_layout = QtWidgets.QVBoxLayout(self)
        main_layout.setSpacing(2)
        main_layout.addLayout(axis_main_layout)
        main_layout.addLayout(delete_old_curves_layout)
        main_layout.addStretch()
        main_layout.addLayout(information_layout)
        main_layout.addLayout(button_layout)
        
    def create_connections(self):
        
        self.create_and_close_btn.clicked.connect(self.create_curve_and_close)
        self.create_curve_btn.clicked.connect(self.create_curve)
        self.close_btn.clicked.connect(self.close)

    def create_curve(self):
            
        selected_curve = cmds.ls(sl=True)
        
        if len(selected_curve) == 1:
            shape = cmds.listRelatives(selected_curve, shapes=True)
            is_it_a_curve = isCurve(shape[0])
            
            if is_it_a_curve:
            
                duplicated_curve = cmds.duplicate(selected_curve)
                duplicated_curve_grp = cmds.group(duplicated_curve[0])
            
            
                zero_transforms_grp = cmds.group(empty=True)
                cmds.matchTransform(duplicated_curve_grp, zero_transforms_grp, pivots=True)
                
                if self.define_axis_x_radio_btn.isChecked():
                    cmds.setAttr(f"{duplicated_curve_grp}.scaleX", -1)
                if self.define_axis_y_radio_btn.isChecked():
                    cmds.setAttr(f"{duplicated_curve_grp}.scaleY", -1)
                if self.define_axis_z_radio_btn.isChecked():
                    cmds.setAttr(f"{duplicated_curve_grp}.scaleZ", -1)
                
                cmds.reverseCurve(f"{duplicated_curve[0]}", constructionHistory=0)
                
                attached_curve = cmds.attachCurve(f"{selected_curve[0]}", f"{duplicated_curve[0]}", constructionHistory=0, replaceOriginal=0, method=1)
                
                cmds.rename(attached_curve[0], f"{selected_curve[0]}mirrored")
                
                cmds.delete(zero_transforms_grp)
                
                if self.delete_old_curves_checkbox.isChecked():
                    cmds.delete(selected_curve[0])
                    cmds.delete(duplicated_curve[0])
            else:
                om.MGlobal.displayError("Please select a curve")
                
                
        elif len(selected_curve) > 1:
            om.MGlobal.displayError("You have more than 1 curve selected")
        
        else:
            om.MGlobal.displayError("Please select only 1 curve")
        
    def isCurve(shape):
        is_a_curve = cmds.objectType(shape, isType="nurbsCurve")
        return is_a_curve
        
    def create_curve_and_close(self):
        
        self.create_curve()
        self.close()

        
if __name__ == "__main__":
    try:
        win.close()        # pylint: disable=E0601
        win.deleteLater()
    except:
        pass
    win = MainToolWindow()
    win.show()
