import ui
import importlib
importlib.reload(ui)
importlib.reload(keywords)

try:
    Mat_Create.close()  # pylint: disable=E0601
    Mat_Create.deleteLater()
except:
    pass

Mat_Create = ui.MainToolWindow()
Mat_Create.show()