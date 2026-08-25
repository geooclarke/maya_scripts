from ui import MainToolWindow

try:
    Mat_Create.close()  # pylint: disable=E0601
    Mat_Create.deleteLater()
except:
    pass

Mat_Create = MainToolWindow()
Mat_Create.show()